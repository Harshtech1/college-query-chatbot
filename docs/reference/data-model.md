# Data Model Reference

## `AdminUser`

Purpose:
Stores local admin credentials for the dashboard.

Key fields:

- `id`
- `username`
- `password_hash`
- `created_at`

Notes:

- Used only when admin functionality is enabled
- created automatically in local mode if no admin record exists

## `FaqEntry`

Purpose:
Stores curated, high-confidence answers that can bypass document retrieval.

Key fields:

- `id`
- `question`
- `answer`
- `category`
- `keywords`
- `priority`
- `is_active`
- `created_at`
- `updated_at`

Role in answering:

- checked before document retrieval
- highest-confidence path for repeated institutional questions

## `KnowledgeDocument`

Purpose:
Represents an uploaded or seeded knowledge source.

Key fields:

- `id`
- `title`
- `filename`
- `content_type`
- `source_kind`
- `status`
- `summary`
- `chunk_count`
- `created_at`
- `updated_at`

Typical `source_kind` values:

- `upload`
- `seed`

## `KnowledgeChunk`

Purpose:
Stores chunked document content for retrieval and grounding.

Key fields:

- `id`
- `document_id`
- `chunk_index`
- `content`
- `token_count`
- `embedding`
- `created_at`

Role in answering:

- scored against the user query
- top matches are passed to grounded answer generation

## `ChatLog`

Purpose:
Stores a record of user questions and assistant answers.

Key fields:

- `id`
- `session_id`
- `user_message`
- `assistant_message`
- `answer_mode`
- `sources_json`
- `created_at`

Role in operations:

- visible in admin monitoring
- useful for reviewing answer quality and repeated gaps in knowledge coverage
