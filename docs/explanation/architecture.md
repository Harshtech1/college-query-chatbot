# Architecture Explanation

## Overview

The project is a Flask web application that answers college questions through a trust-first pipeline:

1. detect topic and conversation context
2. try a curated FAQ answer first
3. retrieve relevant document chunks if no FAQ match exists
4. generate a grounded answer from approved context
5. fall back safely when verified information is missing

## Answering pipeline

### FAQ-first path

`FaqEntry` records are scored against the incoming question.
If a question matches strongly enough, the chatbot returns the curated answer immediately.

Why this matters:

- fastest answer path
- least hallucination risk
- best fit for repeated institutional questions

### Document-backed path

If no FAQ wins:

- the query is embedded
- `KnowledgeChunk` rows are scored for semantic and lexical relevance
- top chunks are packaged as sources
- the answer is generated through the LangChain layer when available, or a deterministic fallback path otherwise

Why this matters:

- preserves citations and trust
- lets the assistant answer from updated source material

### Clarify and fallback

If intent is too ambiguous:

- the chatbot asks one short clarifying question

If verified information is not available:

- the chatbot returns a constrained fallback instead of inventing facts

## Voice pipeline

Voice does not replace the text engine.
It is an input and output layer around the existing chat pipeline:

1. record audio in the browser
2. transcribe through the selected provider
3. send transcript to `POST /api/chat`
4. synthesize the text answer as speech
5. keep sources visible in the chat UI

Supported provider modes:

- `stub`
- `openai`
- `elevenlabs`

## Local vs hosted preview

### Local mode

- admin tools enabled
- local uploads enabled
- SQLite and uploads stored under `instance/`

### Hosted preview mode

- intended for student-facing demo use
- seeded/sample knowledge available
- admin tools blocked
- no promise of persistent SQLite or uploaded document storage
- runtime data stored in a temporary writable directory on Vercel

This split is intentional: the preview should demonstrate the public experience honestly without pretending to be a production-ready knowledge-management system.
