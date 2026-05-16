from __future__ import annotations

import re
from uuid import uuid4

from flask import current_app, session

from chatbot_app.database import db
from chatbot_app.models import ChatLog, FaqEntry, KnowledgeChunk, KnowledgeDocument
from chatbot_app.services.conversation_service import (
    DEFAULT_SUGGESTED_PROMPTS,
    build_clarification_response,
    build_effective_query,
    build_fallback_response,
    detect_topic,
    ensure_conversation_state,
    get_follow_up_replies,
    get_topic_label,
    normalize_topic_slug,
    save_conversation_state,
)
from chatbot_app.services.langchain_service import build_langchain_grounded_answer
from chatbot_app.services.llm_service import OpenAICompatibleService
from chatbot_app.services.text_utils import (
    cosine_similarity,
    excerpt,
    keyword_overlap_score,
    local_embedding,
    normalize_text,
    token_coverage_score,
)


SUGGESTED_PROMPTS = DEFAULT_SUGGESTED_PROMPTS


def ensure_session_id() -> str:
    if not session.get("chat_session_id"):
        session["chat_session_id"] = uuid4().hex
    return session["chat_session_id"]


def answer_query(message: str, session_id: str) -> dict:
    cleaned_message = message.strip()
    if not cleaned_message:
        raise ValueError("Please enter a question.")

    history = session.get("chat_history", [])
    conversation_state = ensure_conversation_state()
    previous_topic = conversation_state.get("current_topic")
    topic_detection = detect_topic(cleaned_message, previous_topic)

    if topic_detection["ambiguous"] and not topic_detection["inherited"]:
        answer, suggested_replies = build_clarification_response(topic_detection, previous_topic)
        payload = build_response_payload(
            answer=answer,
            mode="rag",
            route="clarify",
            confidence=max(topic_detection["confidence"], 0.18),
            topic=previous_topic or topic_detection.get("topic"),
            needs_clarification=True,
            suggested_replies=suggested_replies,
            sources=[],
        )
    else:
        effective_query = build_effective_query(cleaned_message, topic_detection)
        faq, faq_score = find_faq_match(effective_query)

        if faq:
            topic_slug = normalize_topic_slug(faq.category) or topic_detection.get("topic") or previous_topic
            sources = [
                {
                    "kind": "faq",
                    "source_label": "FAQ",
                    "title": f"{faq.category}: {faq.question}",
                    "excerpt": excerpt(faq.answer),
                }
            ]
            payload = build_response_payload(
                answer=faq.answer,
                mode="faq",
                route="faq_direct",
                confidence=min(0.99, max(float(faq_score), 0.88)),
                topic=topic_slug,
                needs_clarification=False,
                suggested_replies=get_follow_up_replies(topic_slug, "faq_direct"),
                sources=sources,
            )
        else:
            chunks = retrieve_relevant_chunks(effective_query)
            if not chunks:
                answer, suggested_replies = build_fallback_response(topic_detection.get("topic") or previous_topic)
                payload = build_response_payload(
                    answer=answer,
                    mode="rag",
                    route="fallback",
                    confidence=min(0.34, max(topic_detection["confidence"], 0.12)),
                    topic=topic_detection.get("topic") or previous_topic,
                    needs_clarification=False,
                    suggested_replies=suggested_replies,
                    sources=[],
                )
            else:
                topic_slug = topic_detection.get("topic") or infer_topic_from_chunks(chunks) or previous_topic
                sources = [
                    {
                        "kind": "document",
                        "source_label": f"S{index}",
                        "title": item["document"].title,
                        "excerpt": excerpt(item["chunk"].content),
                        "score": round(item["score"], 3),
                    }
                    for index, item in enumerate(chunks, start=1)
                ]
                answer = generate_grounded_answer(effective_query, chunks, history) or build_extractive_answer(chunks)
                payload = build_response_payload(
                    answer=answer,
                    mode="rag",
                    route="retrieve_docs",
                    confidence=min(0.96, max(float(chunks[0]["score"]) + 0.08, topic_detection["confidence"])),
                    topic=topic_slug,
                    needs_clarification=False,
                    suggested_replies=get_follow_up_replies(topic_slug, "retrieve_docs"),
                    sources=sources,
                )

    log_chat(session_id, cleaned_message, payload["answer"], payload["mode"], payload["sources"])
    append_session_history(cleaned_message, payload)
    update_conversation_state(conversation_state, payload)
    return payload


def build_response_payload(
    *,
    answer: str,
    mode: str,
    route: str,
    confidence: float,
    topic: str | None,
    needs_clarification: bool,
    suggested_replies: list[str],
    sources: list[dict],
) -> dict:
    topic_slug = normalize_topic_slug(topic)
    return {
        "answer": answer,
        "mode": mode,
        "route": route,
        "confidence": round(float(confidence), 3),
        "topic": topic_slug,
        "topic_label": get_topic_label(topic_slug),
        "needs_clarification": needs_clarification,
        "suggested_replies": suggested_replies[:3],
        "sources": sources,
    }


def find_faq_match(message: str) -> tuple[FaqEntry | None, float]:
    threshold = current_app.config["FAQ_MATCH_THRESHOLD"]
    normalized_message = normalize_text(message)
    best_faq: FaqEntry | None = None
    best_score = 0.0

    faqs = FaqEntry.query.filter_by(is_active=True).order_by(FaqEntry.priority.desc(), FaqEntry.updated_at.desc()).all()
    for faq in faqs:
        normalized_question = normalize_text(faq.question)
        phrase_score = 0.0
        if normalized_message == normalized_question:
            phrase_score = 1.0
        elif normalized_message in normalized_question or normalized_question in normalized_message:
            phrase_score = 0.85

        keyword_score = keyword_overlap_score(message, faq.keywords or [])
        question_score = keyword_overlap_score(message, faq.question)
        score = max(phrase_score, (0.45 * keyword_score) + (0.55 * question_score))
        score += min(faq.priority, 5) * 0.02

        if score > best_score:
            best_score = score
            best_faq = faq

    if best_score >= threshold:
        return best_faq, best_score
    return None, best_score


def retrieve_relevant_chunks(message: str) -> list[dict]:
    service = OpenAICompatibleService()
    query_embedding = service.embed_text(message)
    top_k = current_app.config["RETRIEVAL_TOP_K"]
    threshold = current_app.config["RAG_MATCH_THRESHOLD"]

    rows = (
        db.session.query(KnowledgeChunk, KnowledgeDocument)
        .join(KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id)
        .filter(KnowledgeDocument.status == "processed")
        .order_by(KnowledgeDocument.updated_at.desc())
        .all()
    )

    scored: list[dict] = []
    for chunk, document in rows:
        chunk_embedding = chunk.embedding or local_embedding(chunk.content)
        semantic = cosine_similarity(query_embedding, chunk_embedding)
        lexical = keyword_overlap_score(message, chunk.content)
        coverage = token_coverage_score(message, chunk.content)
        score = (0.45 * semantic) + (0.2 * lexical) + (0.35 * coverage)
        if score >= threshold:
            scored.append({"chunk": chunk, "document": document, "score": score})

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def infer_topic_from_chunks(chunks: list[dict]) -> str | None:
    document_snapshot = " ".join(
        f"{item['document'].title} {excerpt(item['chunk'].content, limit=180)}"
        for item in chunks[:2]
    )
    return detect_topic(document_snapshot).get("topic")


def generate_grounded_answer(message: str, chunks: list[dict], history: list[dict] | None = None) -> str | None:
    langchain_answer = build_langchain_grounded_answer(message, chunks, history)
    if langchain_answer:
        return langchain_answer

    service = OpenAICompatibleService()
    payload = [
        {
            "title": item["document"].title,
            "content": item["chunk"].content,
        }
        for item in chunks
    ]
    try:
        return service.grounded_answer(message, payload)
    except Exception:
        return None


def build_extractive_answer(chunks: list[dict]) -> str:
    lines: list[str] = []
    for index, item in enumerate(chunks[:2], start=1):
        sentences = re.split(r"(?<=[.!?])\s+", item["chunk"].content.strip())
        snippet = " ".join(sentences[:2]).strip()
        if snippet:
            lines.append(f"{snippet} [S{index}]")

    if not lines:
        return "I found related information, but it is not detailed enough for a confident answer."

    return "Based on the available college documents, " + " ".join(lines)


def log_chat(session_id: str, user_message: str, assistant_message: str, mode: str, sources: list[dict]) -> None:
    db.session.add(
        ChatLog(
            session_id=session_id,
            user_message=user_message,
            assistant_message=assistant_message,
            answer_mode=mode,
            sources_json=sources,
        )
    )
    db.session.commit()


def append_session_history(user_message: str, payload: dict) -> None:
    history = session.get("chat_history", [])
    history.append({"role": "user", "content": user_message})
    history.append(
        {
            "role": "assistant",
            "content": payload["answer"],
            "mode": payload["mode"],
            "route": payload["route"],
            "confidence": payload["confidence"],
            "topic": payload["topic"],
            "topic_label": payload["topic_label"],
            "needs_clarification": payload["needs_clarification"],
            "suggested_replies": payload["suggested_replies"],
            "sources": payload["sources"],
        }
    )
    limit = current_app.config["CHAT_HISTORY_LIMIT"] * 2
    session["chat_history"] = history[-limit:]
    session.modified = True


def update_conversation_state(state: dict, payload: dict) -> None:
    state["current_topic"] = payload.get("topic")
    state["unresolved_intent"] = "clarify-topic" if payload.get("needs_clarification") else ""
    state["last_route"] = payload.get("route") or ""
    state["last_confidence"] = float(payload.get("confidence") or 0.0)
    state["last_sources"] = [source.get("title") for source in payload.get("sources", [])[:2] if source.get("title")]
    state["turn_count"] = int(state.get("turn_count") or 0) + 1
    save_conversation_state(state)
