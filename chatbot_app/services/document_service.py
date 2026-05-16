from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import docx2txt
from flask import current_app
from pypdf import PdfReader
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from chatbot_app.database import db
from chatbot_app.models import KnowledgeChunk, KnowledgeDocument
from chatbot_app.services.llm_service import OpenAICompatibleService
from chatbot_app.services.text_utils import chunk_text, excerpt, tokenize


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in current_app.config["ALLOWED_EXTENSIONS"]


def ingest_uploaded_file(file: FileStorage) -> KnowledgeDocument:
    if not file.filename:
        raise ValueError("Please choose a file to upload.")
    if not allowed_file(file.filename):
        raise ValueError("Only PDF, DOCX, and TXT files are supported.")

    upload_dir = Path(current_app.config["UPLOAD_DIR"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = secure_filename(file.filename)
    stored_name = f"{uuid4().hex}-{safe_name}"
    stored_path = upload_dir / stored_name
    file.save(stored_path)

    text = extract_text(stored_path)
    return ingest_text_content(
        title=Path(safe_name).stem.replace("_", " ").title(),
        filename=safe_name,
        text=text,
        content_type=file.mimetype or _content_type_from_suffix(stored_path.suffix.lower()),
        source_kind="upload",
    )


def ingest_text_content(
    *,
    title: str,
    filename: str,
    text: str,
    content_type: str,
    source_kind: str,
) -> KnowledgeDocument:
    clean_text = " ".join(text.split())
    if not clean_text:
        raise ValueError("The uploaded document does not contain readable text.")

    document = KnowledgeDocument(
        title=title,
        filename=filename,
        content_type=content_type,
        source_kind=source_kind,
        status="processing",
        summary=excerpt(clean_text, 220),
    )
    db.session.add(document)
    db.session.commit()

    try:
        persist_document_chunks(document, clean_text)
    except Exception as exc:
        document.status = "failed"
        document.summary = excerpt(f"Import failed: {exc}", 220)
        db.session.commit()
        raise

    return document


def persist_document_chunks(document: KnowledgeDocument, text: str) -> None:
    chunks = chunk_text(text)
    service = OpenAICompatibleService()
    embeddings = service.embed_texts(chunks)

    for index, chunk in enumerate(chunks):
        db.session.add(
            KnowledgeChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                token_count=len(tokenize(chunk)),
                embedding=embeddings[index] if index < len(embeddings) else None,
            )
        )

    document.chunk_count = len(chunks)
    document.status = "processed"
    db.session.commit()


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".docx":
        return docx2txt.process(str(path))
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    raise ValueError("Unsupported file type.")


def _content_type_from_suffix(suffix: str) -> str:
    return {
        ".txt": "text/plain",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pdf": "application/pdf",
    }.get(suffix, "application/octet-stream")
