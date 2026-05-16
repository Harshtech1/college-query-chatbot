from __future__ import annotations

from typing import Any

from flask import current_app

try:
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.documents import Document
    from langchain_core.messages import AIMessage, HumanMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
    from langchain_openai import ChatOpenAI

    LANGCHAIN_AVAILABLE = True
    LANGCHAIN_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - exercised only when deps are missing
    LANGCHAIN_AVAILABLE = False
    LANGCHAIN_IMPORT_ERROR = exc
    Document = Any  # type: ignore[assignment]
    AIMessage = Any  # type: ignore[assignment]
    HumanMessage = Any  # type: ignore[assignment]
    ChatPromptTemplate = Any  # type: ignore[assignment]
    MessagesPlaceholder = Any  # type: ignore[assignment]
    PromptTemplate = Any  # type: ignore[assignment]
    ChatOpenAI = Any  # type: ignore[assignment]


def langchain_enabled() -> bool:
    return bool(
        LANGCHAIN_AVAILABLE
        and current_app.config["USE_LANGCHAIN_PIPELINE"]
        and current_app.config["LLM_API_KEY"]
        and current_app.config["LLM_MODEL"]
    )


def build_langchain_grounded_answer(question: str, chunks: list[dict], history: list[dict] | None = None) -> str | None:
    if not langchain_enabled() or not chunks:
        return None

    llm = ChatOpenAI(
        model=current_app.config["LLM_MODEL"],
        api_key=current_app.config["LLM_API_KEY"],
        base_url=current_app.config["LLM_BASE_URL"],
        temperature=0.2,
        max_retries=1,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a college information assistant. "
                "Answer only from the retrieved context. "
                "If the answer is not supported by the context, say that you do not have enough verified information. "
                "Keep the answer concise and include citations like [S1] or [S2] for factual statements.\n\n"
                "Retrieved context:\n{context}",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "Question: {input}"),
        ]
    )
    document_prompt = PromptTemplate.from_template("[{source_label}] {title}\n{page_content}")
    chain = create_stuff_documents_chain(
        llm,
        prompt,
        document_prompt=document_prompt,
        document_separator="\n\n",
    )

    try:
        response = chain.invoke(
            {
                "input": question,
                "context": build_langchain_documents(chunks),
                "chat_history": build_message_history(history or []),
            }
        )
    except Exception:
        return None

    if isinstance(response, str) and response.strip():
        return response.strip()
    return None


def build_langchain_documents(chunks: list[dict]) -> list[Document]:
    documents: list[Document] = []
    for index, item in enumerate(chunks, start=1):
        documents.append(
            Document(
                page_content=item["chunk"].content,
                metadata={
                    "title": item["document"].title,
                    "source_label": f"S{index}",
                    "score": round(item["score"], 3),
                    "document_id": item["document"].id,
                    "chunk_id": item["chunk"].id,
                },
            )
        )
    return documents


def build_message_history(history: list[dict]) -> list[Any]:
    messages: list[Any] = []
    for item in history[-8:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages
