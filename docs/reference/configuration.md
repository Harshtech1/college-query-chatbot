# Configuration Reference

## Core runtime

- `SECRET_KEY`
  Session and flash-message signing key.
- `DATABASE_URL`
  SQLAlchemy connection string. If unset, the app uses SQLite in the runtime instance directory.
- `DEMO_MODE`
  Enables hosted demo behavior. Defaults to `1` on Vercel and `0` locally.
- `ADMIN_USERNAME`
  Default admin username for local mode.
- `ADMIN_PASSWORD`
  Default admin password for local mode.

## AI and retrieval

- `LLM_BASE_URL`
  Base URL for the OpenAI-compatible API.
- `LLM_API_KEY`
  Chat and embedding provider key.
- `LLM_MODEL`
  Chat model name.
- `EMBEDDING_MODEL`
  Embedding model name.
- `USE_LANGCHAIN_PIPELINE`
  Enables the LangChain grounded-answer layer when set truthy.
- `USE_REMOTE_EMBEDDINGS`
  Enables provider embeddings instead of local fallback embeddings.
- `CHAT_HISTORY_LIMIT`
  Number of stored turns per session.
- `RETRIEVAL_TOP_K`
  Maximum retrieved chunks for grounded answers.
- `FAQ_MATCH_THRESHOLD`
  Minimum score for a direct FAQ answer.
- `RAG_MATCH_THRESHOLD`
  Minimum score for a document chunk to be considered relevant.

## Voice

- `VOICE_ENABLED`
  Enables browser voice features.
- `VOICE_PROVIDER`
  `stub`, `openai`, or `elevenlabs`.
- `VOICE_API_KEY`
  Voice provider API key.
- `VOICE_LANGUAGE`
  Spoken language code, currently `en` by default.
- `VOICE_STT_MODEL`
  Speech-to-text model identifier.
- `VOICE_TTS_MODEL`
  Text-to-speech model identifier.
- `VOICE_TTS_VOICE_ID`
  Voice identifier for the chosen provider.
- `VOICE_MAX_SECONDS`
  Maximum allowed recording duration.
- `VOICE_AUTOPLAY_DEFAULT`
  Whether hosted/local UI should auto-play spoken answers by default.
- `VOICE_STUB_TRANSCRIPT`
  Demo transcript returned by the stub provider when not embedding a transcript string directly.

## Hosted preview behavior

When running on Vercel:

- runtime data goes to a temporary instance directory
- hosted demo mode defaults on unless explicitly disabled
- admin pages and admin APIs are intentionally blocked in hosted demo mode
- seeded/sample knowledge remains available for the public chat

## Public routes

- `GET /`
- `POST /api/chat`
- `GET /api/voice/config`
- `POST /api/voice/transcribe`
- `POST /api/voice/speak`
- `GET /admin/login`
- `GET /admin`

In hosted demo mode, admin routes return an unavailable message instead of exposing live management features.
