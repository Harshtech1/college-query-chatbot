from __future__ import annotations

from flask import Blueprint, Response, current_app, jsonify, request

from chatbot_app.auth import admin_login_required
from chatbot_app.database import db
from chatbot_app.models import FaqEntry
from chatbot_app.services.chat_service import answer_query, ensure_session_id
from chatbot_app.services.document_service import ingest_uploaded_file
from chatbot_app.services.voice_service import (
    VoiceServiceError,
    get_voice_ui_config,
    synthesize_spoken_reply,
    transcribe_audio_upload,
)


api_bp = Blueprint("api", __name__)


def _admin_api_block_response():
    return jsonify({"error": "Admin management is disabled in the hosted demo preview. Use local development for uploads and FAQ editing."}), 403


@api_bp.before_request
def block_admin_api_in_hosted_demo():
    if request.path.startswith("/api/admin/") and not current_app.config["ADMIN_ENABLED"]:
        return _admin_api_block_response()
    return None


@api_bp.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        result = answer_query(message, ensure_session_id())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result)


@api_bp.get("/api/voice/config")
def voice_config():
    return jsonify(get_voice_ui_config())


@api_bp.post("/api/voice/transcribe")
def voice_transcribe():
    file = request.files.get("audio")
    if not file:
        return jsonify({"error": "Please record a question before sending audio."}), 400

    raw_duration = request.form.get("duration_ms") or "0"
    try:
        duration_ms = max(0, int(float(raw_duration)))
    except ValueError:
        duration_ms = 0

    try:
        payload = transcribe_audio_upload(
            audio_bytes=file.read(),
            mime_type=file.mimetype,
            filename=file.filename or "recording.webm",
            duration_ms=duration_ms,
        )
    except VoiceServiceError as exc:
        return jsonify({"error": str(exc)}), exc.status_code

    return jsonify(payload)


@api_bp.post("/api/voice/speak")
def voice_speak():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Please provide text to speak."}), 400

    try:
        audio_bytes, content_type, spoken_text, provider = synthesize_spoken_reply(
            text=text,
            topic=(data.get("topic") or "").strip() or None,
            route=(data.get("route") or "").strip() or None,
        )
    except VoiceServiceError as exc:
        return jsonify({"error": str(exc)}), exc.status_code

    return Response(
        audio_bytes,
        mimetype=content_type,
        headers={
            "Cache-Control": "no-store",
            "X-Voice-Provider": provider,
            "X-Spoken-Text-Length": str(len(spoken_text)),
        },
    )


@api_bp.route("/api/admin/faqs", methods=["GET", "POST"])
@admin_login_required
def faqs():
    if request.method == "GET":
        records = FaqEntry.query.order_by(FaqEntry.priority.desc(), FaqEntry.updated_at.desc()).all()
        return jsonify([faq.to_dict() for faq in records])

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    answer = (data.get("answer") or "").strip()
    if not question or not answer:
        return jsonify({"error": "Question and answer are required."}), 400

    faq = FaqEntry(
        question=question,
        answer=answer,
        category=(data.get("category") or "General").strip() or "General",
        keywords=_normalize_keywords(data.get("keywords")),
        priority=int(data.get("priority") or 1),
        is_active=bool(data.get("is_active", True)),
    )
    db.session.add(faq)
    db.session.commit()
    return jsonify(faq.to_dict()), 201


@api_bp.route("/api/admin/faqs/<int:faq_id>", methods=["PATCH", "DELETE"])
@admin_login_required
def faq_detail(faq_id: int):
    faq = db.session.get(FaqEntry, faq_id)
    if not faq:
        return jsonify({"error": "FAQ entry not found."}), 404

    if request.method == "DELETE":
        db.session.delete(faq)
        db.session.commit()
        return jsonify({"status": "deleted"})

    data = request.get_json(silent=True) or {}
    if "question" in data:
        faq.question = (data.get("question") or "").strip()
    if "answer" in data:
        faq.answer = (data.get("answer") or "").strip()
    if "category" in data:
        faq.category = (data.get("category") or "General").strip() or "General"
    if "keywords" in data:
        faq.keywords = _normalize_keywords(data.get("keywords"))
    if "priority" in data:
        faq.priority = int(data.get("priority") or 1)
    if "is_active" in data:
        faq.is_active = bool(data.get("is_active"))

    if not faq.question or not faq.answer:
        return jsonify({"error": "Question and answer are required."}), 400

    db.session.commit()
    return jsonify(faq.to_dict())


@api_bp.post("/api/admin/documents")
@admin_login_required
def upload_document():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "Please choose a document to upload."}), 400

    try:
        document = ingest_uploaded_file(file)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Import failed: {exc}"}), 500

    return jsonify(document.to_dict()), 201


def _normalize_keywords(raw_keywords) -> list[str]:
    if isinstance(raw_keywords, list):
        values = raw_keywords
    else:
        values = str(raw_keywords or "").split(",")
    return [value.strip() for value in values if value and value.strip()]
