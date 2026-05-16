from __future__ import annotations

import os
import tempfile
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parent.parent
    IS_VERCEL = bool(os.getenv("VERCEL"))
    DEMO_MODE = os.getenv("DEMO_MODE", "1" if IS_VERCEL else "0").lower() not in {"0", "false", "no"}
    INSTANCE_DIR = (Path(tempfile.gettempdir()) / "college_chatbot") if IS_VERCEL else (BASE_DIR / "instance")
    UPLOAD_DIR = INSTANCE_DIR / "uploads"
    ADMIN_ENABLED = not (IS_VERCEL and DEMO_MODE)
    SECRET_KEY = os.getenv("SECRET_KEY", "college-chatbot-dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{(INSTANCE_DIR / 'college_chatbot.db').as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    USE_LANGCHAIN_PIPELINE = os.getenv("USE_LANGCHAIN_PIPELINE", "1").lower() not in {"0", "false", "no"}
    USE_REMOTE_EMBEDDINGS = os.getenv("USE_REMOTE_EMBEDDINGS", "1").lower() not in {"0", "false", "no"}
    CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "12"))
    RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "4"))
    FAQ_MATCH_THRESHOLD = float(os.getenv("FAQ_MATCH_THRESHOLD", "0.42"))
    RAG_MATCH_THRESHOLD = float(os.getenv("RAG_MATCH_THRESHOLD", "0.10"))
    VOICE_ENABLED = os.getenv("VOICE_ENABLED", "0").lower() not in {"0", "false", "no"}
    VOICE_PROVIDER = os.getenv("VOICE_PROVIDER", "stub").strip().lower()
    VOICE_API_KEY = os.getenv("VOICE_API_KEY", "")
    VOICE_LANGUAGE = os.getenv("VOICE_LANGUAGE", "en").strip().lower() or "en"
    VOICE_STT_MODEL = os.getenv("VOICE_STT_MODEL", "").strip()
    VOICE_TTS_MODEL = os.getenv("VOICE_TTS_MODEL", "").strip()
    VOICE_TTS_VOICE_ID = os.getenv("VOICE_TTS_VOICE_ID", "").strip()
    VOICE_MAX_SECONDS = int(os.getenv("VOICE_MAX_SECONDS", "20"))
    VOICE_AUTOPLAY_DEFAULT = os.getenv("VOICE_AUTOPLAY_DEFAULT", "0").lower() not in {"0", "false", "no"}
    VOICE_STUB_TRANSCRIPT = os.getenv("VOICE_STUB_TRANSCRIPT", "What is the admission process?")
