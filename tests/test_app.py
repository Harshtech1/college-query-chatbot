from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest

from chatbot_app import create_app
from chatbot_app.services import langchain_service
from chatbot_app.services.langchain_service import build_langchain_grounded_answer


@pytest.fixture()
def app(tmp_path: Path):
    instance_dir = tmp_path / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)

    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(instance_dir / 'test.db').as_posix()}",
            "UPLOAD_DIR": instance_dir / "uploads",
            "ADMIN_USERNAME": "admin",
            "ADMIN_PASSWORD": "admin123",
            "LLM_API_KEY": "",
            "USE_REMOTE_EMBEDDINGS": False,
            "VOICE_ENABLED": True,
            "VOICE_PROVIDER": "stub",
            "VOICE_STUB_TRANSCRIPT": "What is the admission process?",
        }
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client):
    return client.post(
        "/admin/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Official Academic Service Interface" in response.data


def test_seeded_faq_chat_response(client):
    response = client.post("/api/chat", json={"message": "What is the admission process?"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["mode"] == "faq"
    assert payload["route"] == "faq_direct"
    assert payload["topic"] == "admissions"
    assert payload["confidence"] >= 0.88
    assert "apply" in payload["answer"].lower() or "admission" in payload["answer"].lower()


def test_ambiguous_query_triggers_single_clarification(client):
    response = client.post("/api/chat", json={"message": "Tell me more"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["mode"] == "rag"
    assert payload["route"] == "clarify"
    assert payload["needs_clarification"] is True
    assert len(payload["suggested_replies"]) >= 1


def test_follow_up_question_reuses_previous_topic_context(client):
    first_response = client.post("/api/chat", json={"message": "What is the admission process?"})
    first_payload = first_response.get_json()

    second_response = client.post("/api/chat", json={"message": "What about eligibility?"})
    second_payload = second_response.get_json()

    assert first_response.status_code == 200
    assert first_payload["topic"] == "admissions"
    assert second_response.status_code == 200
    assert second_payload["route"] == "retrieve_docs"
    assert second_payload["topic"] == "admissions"
    assert second_payload["needs_clarification"] is False
    assert second_payload["sources"]


def test_admin_can_create_update_and_delete_faq(client):
    login_response = login(client)
    assert login_response.status_code == 200

    create_response = client.post(
        "/api/admin/faqs",
        json={
            "question": "Who is the principal?",
            "answer": "The principal details are available at the administration office.",
            "category": "Administration",
            "keywords": ["principal", "head"],
            "priority": 2,
            "is_active": True,
        },
    )
    created = create_response.get_json()

    assert create_response.status_code == 201
    assert created["question"] == "Who is the principal?"

    update_response = client.patch(
        f"/api/admin/faqs/{created['id']}",
        json={"answer": "The principal information is listed on the administration notice board."},
    )
    updated = update_response.get_json()

    assert update_response.status_code == 200
    assert "notice board" in updated["answer"]

    delete_response = client.delete(f"/api/admin/faqs/{created['id']}")
    assert delete_response.status_code == 200


def test_admin_can_upload_text_document(client):
    login(client)

    response = client.post(
        "/api/admin/documents",
        data={
            "file": (BytesIO(b"Scholarship notices are published by the student welfare office."), "scholarship.txt")
        },
        content_type="multipart/form-data",
    )
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["status"] == "processed"
    assert payload["chunk_count"] >= 1


def test_hosted_demo_blocks_admin_pages(tmp_path: Path):
    instance_dir = tmp_path / "demo-instance"
    instance_dir.mkdir(parents=True, exist_ok=True)

    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(instance_dir / 'demo.db').as_posix()}",
            "UPLOAD_DIR": instance_dir / "uploads",
            "ADMIN_ENABLED": False,
            "DEMO_MODE": True,
            "VOICE_ENABLED": False,
        }
    )
    client = app.test_client()

    response = client.get("/admin/login")

    assert response.status_code == 403
    assert b"hosted demo preview" in response.data.lower()


def test_hosted_demo_blocks_admin_api_routes(tmp_path: Path):
    instance_dir = tmp_path / "demo-instance"
    instance_dir.mkdir(parents=True, exist_ok=True)

    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{(instance_dir / 'demo.db').as_posix()}",
            "UPLOAD_DIR": instance_dir / "uploads",
            "ADMIN_ENABLED": False,
            "DEMO_MODE": True,
            "VOICE_ENABLED": False,
        }
    )
    client = app.test_client()

    response = client.post(
        "/api/admin/faqs",
        json={
            "question": "Can I update this from preview?",
            "answer": "No.",
            "category": "Testing",
        },
    )
    payload = response.get_json()

    assert response.status_code == 403
    assert "hosted demo preview" in payload["error"].lower()


def test_langchain_layer_gracefully_skips_without_api_key(app):
    with app.app_context():
        chunks = [
            {
                "chunk": SimpleNamespace(content="Hall tickets are distributed after attendance and fee compliance is confirmed.", id=1),
                "document": SimpleNamespace(title="Exam Handbook", id=1),
                "score": 0.88,
            }
        ]
        history = [{"role": "user", "content": "How are hall tickets distributed?"}]

        assert build_langchain_grounded_answer("How are hall tickets distributed?", chunks, history) is None


def test_langchain_layer_can_build_grounded_answer_without_external_call(app, monkeypatch):
    class FakeLLM:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class FakeChain:
        def invoke(self, payload):
            assert payload["input"] == "How are hall tickets distributed?"
            assert payload["context"][0].metadata["source_label"] == "S1"
            assert payload["context"][0].metadata["title"] == "Exam Handbook"
            return "Hall tickets are distributed after attendance and fee compliance is confirmed. [S1]"

    monkeypatch.setattr(langchain_service, "ChatOpenAI", FakeLLM)
    monkeypatch.setattr(
        langchain_service,
        "create_stuff_documents_chain",
        lambda llm, prompt, document_prompt, document_separator: FakeChain(),
    )

    with app.app_context():
        app.config["LLM_API_KEY"] = "demo-key"
        chunks = [
            {
                "chunk": SimpleNamespace(content="Hall tickets are distributed after attendance and fee compliance is confirmed.", id=1),
                "document": SimpleNamespace(title="Exam Handbook", id=1),
                "score": 0.88,
            }
        ]
        history = [{"role": "user", "content": "How are hall tickets distributed?"}]

        result = build_langchain_grounded_answer("How are hall tickets distributed?", chunks, history)

    assert result == "Hall tickets are distributed after attendance and fee compliance is confirmed. [S1]"


def test_voice_config_reports_disabled_when_feature_is_off(app, client):
    app.config["VOICE_ENABLED"] = False

    response = client.get("/api/voice/config")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["enabled"] is False
    assert "turned off" in payload["disabled_reason"].lower()

    app.config["VOICE_ENABLED"] = True


def test_voice_config_requires_key_for_openai_provider(app, client):
    app.config["VOICE_PROVIDER"] = "openai"
    app.config["VOICE_API_KEY"] = ""

    response = client.get("/api/voice/config")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["enabled"] is False
    assert payload["provider"] == "openai"
    assert "api key" in payload["disabled_reason"].lower()

    app.config["VOICE_PROVIDER"] = "stub"


def test_stub_voice_routes_transcribe_and_speak(client):
    transcribe_response = client.post(
        "/api/voice/transcribe",
        data={
            "audio": (BytesIO(b"TRANSCRIPT:What is the admission process?"), "question.webm", "audio/webm"),
            "duration_ms": "1200",
        },
        content_type="multipart/form-data",
    )
    transcribe_payload = transcribe_response.get_json()

    assert transcribe_response.status_code == 200
    assert transcribe_payload["provider"] == "stub"
    assert transcribe_payload["transcript"] == "What is the admission process?"

    speak_response = client.post(
        "/api/voice/speak",
        json={"text": "The admission process requires an application form and document verification.", "route": "faq_direct"},
    )

    assert speak_response.status_code == 200
    assert speak_response.mimetype == "audio/wav"
    assert len(speak_response.data) > 100


def test_voice_transcript_can_flow_into_grounded_chat_answer(client):
    transcribe_response = client.post(
        "/api/voice/transcribe",
        data={
            "audio": (BytesIO(b"TRANSCRIPT:What is the admission process?"), "question.webm", "audio/webm"),
            "duration_ms": "1100",
        },
        content_type="multipart/form-data",
    )
    transcript = transcribe_response.get_json()["transcript"]

    chat_response = client.post("/api/chat", json={"message": transcript})
    chat_payload = chat_response.get_json()

    assert transcribe_response.status_code == 200
    assert chat_response.status_code == 200
    assert chat_payload["route"] == "faq_direct"
    assert chat_payload["topic"] == "admissions"
