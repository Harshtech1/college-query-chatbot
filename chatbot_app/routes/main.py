from __future__ import annotations

from flask import Blueprint, render_template, session

from chatbot_app.models import FaqEntry, KnowledgeDocument
from chatbot_app.services.chat_service import SUGGESTED_PROMPTS, ensure_session_id
from chatbot_app.services.conversation_service import get_route_guide


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    ensure_session_id()
    history = session.get("chat_history", [])
    return render_template(
        "index.html",
        history=history,
        suggested_prompts=SUGGESTED_PROMPTS,
        route_guide=get_route_guide(),
        verification_status=get_verification_status(),
    )


def get_verification_status() -> str:
    latest_faq = FaqEntry.query.order_by(FaqEntry.updated_at.desc()).first()
    latest_document = KnowledgeDocument.query.order_by(KnowledgeDocument.updated_at.desc()).first()
    candidates = [
        item.updated_at
        for item in (latest_faq, latest_document)
        if item and item.updated_at
    ]
    if not candidates:
        return "Awaiting the next official notice import."

    latest_update = max(candidates)
    return f"Updated from official notices up to {latest_update.strftime('%d %B %Y')}"
