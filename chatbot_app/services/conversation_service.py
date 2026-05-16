from __future__ import annotations

from copy import deepcopy

from flask import session

from chatbot_app.services.text_utils import keyword_overlap_score, normalize_text


TOPIC_BLUEPRINTS = {
    "admissions": {
        "label": "Admissions",
        "summary": "Application steps, required documents, eligibility, and admission confirmation.",
        "keywords": [
            "admission",
            "admissions",
            "apply",
            "application",
            "enrollment",
            "eligibility",
            "documents",
            "verification",
            "confirmation",
        ],
        "prompts": [
            "What is the admission process?",
            "What documents are required for admission?",
            "How is admission eligibility verified?",
        ],
    },
    "fees": {
        "label": "Fees",
        "summary": "Fee structure, payment options, due dates, and accounts office guidance.",
        "keywords": [
            "fee",
            "fees",
            "payment",
            "payments",
            "accounts",
            "tuition",
            "circular",
            "due",
            "portal",
        ],
        "prompts": [
            "What is the fee structure?",
            "How can I pay the college fees?",
            "Where can I find the latest fee circular?",
        ],
    },
    "exams": {
        "label": "Exams",
        "summary": "Exam schedules, assessment calendars, hall tickets, and exam readiness.",
        "keywords": [
            "exam",
            "exams",
            "examination",
            "assessment",
            "schedule",
            "calendar",
            "hall ticket",
            "internal",
            "semester",
        ],
        "prompts": [
            "When are exams conducted?",
            "How are hall tickets issued?",
            "Where is the official exam timetable published?",
        ],
    },
    "attendance": {
        "label": "Attendance",
        "summary": "Attendance status, minimum percentage, shortage handling, and student follow-up.",
        "keywords": [
            "attendance",
            "present",
            "percentage",
            "shortage",
            "classes",
            "absent",
            "justification",
        ],
        "prompts": [
            "How can I check attendance details?",
            "What is the minimum attendance requirement?",
            "What happens if attendance is short?",
        ],
    },
    "courses": {
        "label": "Courses",
        "summary": "Available programs, departments, and the academic brochure.",
        "keywords": [
            "course",
            "courses",
            "program",
            "programs",
            "department",
            "departments",
            "subject",
            "brochure",
        ],
        "prompts": [
            "Which courses are available?",
            "Which departments offer undergraduate programs?",
            "Where can I find the course brochure?",
        ],
    },
    "faculty": {
        "label": "Faculty",
        "summary": "Faculty allotment, coordinators, and department communication.",
        "keywords": [
            "faculty",
            "teacher",
            "teachers",
            "professor",
            "coordinator",
            "staff",
            "allotment",
        ],
        "prompts": [
            "How can I find faculty details?",
            "Who provides faculty allotment updates?",
            "Where are department coordinator details shared?",
        ],
    },
    "timetable": {
        "label": "Timetable",
        "summary": "Class schedules, revised routines, and department timetable notices.",
        "keywords": [
            "timetable",
            "time table",
            "routine",
            "schedule",
            "class timings",
            "timing",
            "revised schedule",
        ],
        "prompts": [
            "How can I view the timetable?",
            "Where are timetable revisions announced?",
            "Who shares the latest class schedule?",
        ],
    },
    "policy": {
        "label": "General Policy",
        "summary": "Official notices, handbook guidance, and institution-wide information.",
        "keywords": [
            "policy",
            "notice",
            "notices",
            "handbook",
            "official",
            "office",
            "general",
            "college",
        ],
        "prompts": [
            "Where can I find official college notices?",
            "Which office manages general student queries?",
            "What information is available in the college handbook?",
        ],
    },
}

ROUTE_GUIDE = [
    {
        "route": "faq_direct",
        "label": "Official Answer",
        "detail": "Matched to an approved FAQ maintained by staff.",
    },
    {
        "route": "retrieve_docs",
        "label": "From University Documents",
        "detail": "Grounded in notices, handbooks, or circulars on record.",
    },
    {
        "route": "clarify",
        "label": "Need One Detail",
        "detail": "Requests one short clarification before confirming the answer.",
    },
    {
        "route": "fallback",
        "label": "Not Yet Verified",
        "detail": "Stops rather than guessing when verified material is missing.",
    },
]

FOLLOW_UP_PREFIXES = (
    "what about",
    "and what about",
    "what else",
    "tell me more",
    "more on",
    "more about",
    "how about",
    "and ",
    "also ",
    "then ",
)

SHORT_GENERIC_MESSAGES = {
    "details",
    "more details",
    "more info",
    "more information",
    "eligibility",
    "documents",
    "fees",
    "payment",
    "schedule",
    "timings",
    "faculty",
    "attendance",
}

DEFAULT_SUGGESTED_PROMPTS = [
    TOPIC_BLUEPRINTS["admissions"]["prompts"][0],
    TOPIC_BLUEPRINTS["fees"]["prompts"][0],
    TOPIC_BLUEPRINTS["exams"]["prompts"][0],
    TOPIC_BLUEPRINTS["attendance"]["prompts"][0],
    TOPIC_BLUEPRINTS["courses"]["prompts"][0],
    TOPIC_BLUEPRINTS["timetable"]["prompts"][0],
]


def get_topic_cards() -> list[dict]:
    cards: list[dict] = []
    for slug, blueprint in TOPIC_BLUEPRINTS.items():
        cards.append(
            {
                "slug": slug,
                "label": blueprint["label"],
                "summary": blueprint["summary"],
                "prompts": blueprint["prompts"][:2],
            }
        )
    return cards


def get_route_guide() -> list[dict]:
    return deepcopy(ROUTE_GUIDE)


def get_topic_label(topic: str | None) -> str | None:
    if not topic:
        return None
    blueprint = TOPIC_BLUEPRINTS.get(topic)
    if blueprint:
        return blueprint["label"]
    return topic.replace("_", " ").title()


def normalize_topic_slug(raw_topic: str | None) -> str | None:
    if not raw_topic:
        return None

    normalized = normalize_text(raw_topic)
    for slug, blueprint in TOPIC_BLUEPRINTS.items():
        aliases = [slug, blueprint["label"], *blueprint["keywords"]]
        if any(normalize_text(alias) == normalized for alias in aliases):
            return slug
    return None


def ensure_conversation_state() -> dict:
    state = session.get("conversation_state") or {}
    normalized_topic = normalize_topic_slug(state.get("current_topic"))
    normalized_state = {
        "current_topic": normalized_topic,
        "topic_label": get_topic_label(normalized_topic),
        "unresolved_intent": str(state.get("unresolved_intent") or ""),
        "last_route": str(state.get("last_route") or ""),
        "last_confidence": float(state.get("last_confidence") or 0.0),
        "last_sources": list(state.get("last_sources") or []),
        "turn_count": int(state.get("turn_count") or 0),
    }

    if state != normalized_state:
        session["conversation_state"] = normalized_state
        session.modified = True

    return normalized_state


def save_conversation_state(state: dict) -> None:
    current_topic = normalize_topic_slug(state.get("current_topic"))
    state["current_topic"] = current_topic
    state["topic_label"] = get_topic_label(current_topic)
    session["conversation_state"] = state
    session.modified = True


def is_follow_up_query(message: str) -> bool:
    normalized = normalize_text(message)
    if not normalized:
        return False

    if any(normalized.startswith(prefix) for prefix in FOLLOW_UP_PREFIXES):
        return True

    words = normalized.split()
    return len(words) <= 4 and normalized in SHORT_GENERIC_MESSAGES


def detect_topic(message: str, previous_topic: str | None = None) -> dict:
    normalized = normalize_text(message)
    follow_up = is_follow_up_query(normalized)
    matches: list[dict] = []

    for slug, blueprint in TOPIC_BLUEPRINTS.items():
        keyword_score = keyword_overlap_score(normalized, blueprint["keywords"])
        label_score = keyword_overlap_score(normalized, blueprint["label"])
        prompt_score = max(keyword_overlap_score(normalized, prompt) for prompt in blueprint["prompts"])
        score = max(keyword_score, (0.55 * keyword_score) + (0.2 * label_score) + (0.25 * prompt_score))
        if previous_topic == slug and follow_up:
            score += 0.18
        matches.append({"slug": slug, "label": blueprint["label"], "score": round(score, 3)})

    matches.sort(key=lambda item: item["score"], reverse=True)
    best = matches[0] if matches else {"slug": None, "label": None, "score": 0.0}
    second = matches[1] if len(matches) > 1 else {"slug": None, "label": None, "score": 0.0}
    inherited = False

    if previous_topic and follow_up and best["score"] < 0.22:
        inherited = True
        best = {
            "slug": previous_topic,
            "label": get_topic_label(previous_topic),
            "score": 0.32,
        }

    candidates = [item for item in matches if item["score"] >= 0.16][:3]
    ambiguous = False
    if not inherited:
        ambiguous = best["score"] < 0.2 or (
            second["score"] >= 0.18 and abs(best["score"] - second["score"]) <= 0.08
        )
        if not candidates and not previous_topic:
            ambiguous = True

    chosen_topic = best["slug"] if (best["score"] >= 0.2 or inherited) else None
    return {
        "topic": chosen_topic,
        "label": best["label"] if chosen_topic else None,
        "confidence": round(float(best["score"]), 3),
        "ambiguous": ambiguous,
        "follow_up": follow_up,
        "inherited": inherited,
        "candidates": candidates,
    }


def build_effective_query(message: str, detected_topic: dict) -> str:
    topic = detected_topic.get("topic")
    label = detected_topic.get("label")
    if not topic or not label:
        return message

    blueprint = TOPIC_BLUEPRINTS.get(topic, {})
    normalized = normalize_text(message)
    if normalize_text(label) in normalized or normalize_text(topic) in normalized:
        return message

    if detected_topic.get("follow_up") or detected_topic.get("inherited"):
        keyword_boost = " ".join(blueprint.get("keywords", [])[:4])
        return f"{label} {keyword_boost}: {message}"

    return f"{label}: {message}"


def build_clarification_response(detected_topic: dict, previous_topic: str | None = None) -> tuple[str, list[str]]:
    suggestions: list[str] = []
    seen: set[str] = set()

    if previous_topic:
        for prompt in get_follow_up_replies(previous_topic, "clarify"):
            if prompt not in seen:
                suggestions.append(prompt)
                seen.add(prompt)

    for candidate in detected_topic.get("candidates", []):
        prompt = TOPIC_BLUEPRINTS[candidate["slug"]]["prompts"][0]
        if prompt not in seen:
            suggestions.append(prompt)
            seen.add(prompt)

    for prompt in DEFAULT_SUGGESTED_PROMPTS:
        if prompt not in seen:
            suggestions.append(prompt)
            seen.add(prompt)
        if len(suggestions) >= 4:
            break

    candidate_labels = [candidate["label"] for candidate in detected_topic.get("candidates", [])]
    if previous_topic and get_topic_label(previous_topic) and get_topic_label(previous_topic) not in candidate_labels:
        candidate_labels.insert(0, get_topic_label(previous_topic))

    if candidate_labels:
        answer = (
            "I can help with that. To provide an official answer, I need one quick detail first. "
            f"Is your question about {', '.join(candidate_labels[:3])}?"
        )
    else:
        answer = (
            "I can help once I know the service area. "
            "Please choose one academic topic so I can answer from approved FAQs or official university documents."
        )

    return answer, suggestions[:4]


def build_fallback_response(topic: str | None) -> tuple[str, list[str]]:
    topic_label = get_topic_label(topic)
    if topic_label:
        answer = (
            f"I could not verify that from the approved FAQs or current university documents for {topic_label.lower()}. "
            "Please check the latest official notice or contact the relevant department for confirmation."
        )
    else:
        answer = (
            "I could not verify that yet from the approved FAQs or current university documents. "
            "Please ask a more specific question, check the latest official notice, or contact the relevant department."
        )
    return answer, get_follow_up_replies(topic, "fallback")


def get_follow_up_replies(topic: str | None, route: str) -> list[str]:
    normalized_topic = normalize_topic_slug(topic)
    prompts = TOPIC_BLUEPRINTS.get(normalized_topic, {}).get("prompts", [])

    if route == "clarify":
        return prompts[:2] or DEFAULT_SUGGESTED_PROMPTS[:2]

    if route in {"faq_direct", "retrieve_docs"}:
        return prompts[1:3] or prompts[:1] or DEFAULT_SUGGESTED_PROMPTS[:2]

    fallback_prompts = list(prompts[:1]) if prompts else []
    for prompt in DEFAULT_SUGGESTED_PROMPTS:
        if prompt not in fallback_prompts:
            fallback_prompts.append(prompt)
        if len(fallback_prompts) >= 3:
            break
    return fallback_prompts
