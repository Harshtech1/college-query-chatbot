from __future__ import annotations

from typing import Iterable

import requests
from flask import current_app

from chatbot_app.services.text_utils import local_embedding


class OpenAICompatibleService:
    def __init__(self) -> None:
        self.base_url = current_app.config["LLM_BASE_URL"]
        self.api_key = current_app.config["LLM_API_KEY"]
        self.chat_model = current_app.config["LLM_MODEL"]
        self.embedding_model = current_app.config["EMBEDDING_MODEL"]
        self.use_remote_embeddings = current_app.config["USE_REMOTE_EMBEDDINGS"]

    @property
    def chat_enabled(self) -> bool:
        return bool(self.api_key and self.chat_model)

    @property
    def embedding_enabled(self) -> bool:
        return bool(self.api_key and self.embedding_model and self.use_remote_embeddings)

    def embed_text(self, text: str) -> list[float]:
        if not self.embedding_enabled:
            return local_embedding(text)

        payload = {"model": self.embedding_model, "input": text}
        response = self._post("/embeddings", payload)
        data = response.get("data", [])
        if not data:
            return local_embedding(text)
        return data[0].get("embedding", []) or local_embedding(text)

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        text_list = list(texts)
        if not text_list:
            return []
        if not self.embedding_enabled:
            return [local_embedding(text) for text in text_list]

        payload = {"model": self.embedding_model, "input": text_list}
        response = self._post("/embeddings", payload)
        data = sorted(response.get("data", []), key=lambda item: item.get("index", 0))
        if len(data) != len(text_list):
            return [local_embedding(text) for text in text_list]
        return [item.get("embedding", []) or local_embedding(text_list[index]) for index, item in enumerate(data)]

    def grounded_answer(self, question: str, sources: list[dict]) -> str | None:
        if not self.chat_enabled or not sources:
            return None

        context_lines = []
        for position, item in enumerate(sources, start=1):
            context_lines.append(f"[{position}] {item['title']}\n{item['content']}")

        system_prompt = (
            "You are a college information assistant. Answer only from the provided context. "
            "If the answer is not supported by the context, say you do not have enough verified information. "
            "Keep the answer concise and include citations like [1] or [2] for every factual statement."
        )
        user_prompt = (
            f"Question: {question}\n\n"
            f"Context:\n{'\n\n'.join(context_lines)}\n\n"
            "Return a short answer grounded only in the context."
        )

        payload = {
            "model": self.chat_model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        response = self._post("/chat/completions", payload)
        choices = response.get("choices", [])
        if not choices:
            return None
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
        return None

    def _post(self, path: str, payload: dict) -> dict:
        response = requests.post(
            f"{self.base_url}{path}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        return response.json()

