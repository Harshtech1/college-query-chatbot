from __future__ import annotations

import hashlib
import math
import re
from collections import Counter


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "where",
    "which",
}


def normalize_text(text: str) -> str:
    return " ".join(TOKEN_PATTERN.findall(text.lower()))


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOP_WORDS]


def keyword_overlap_score(query: str, candidate: str | list[str]) -> float:
    query_tokens = set(tokenize(query))
    if isinstance(candidate, list):
        flattened: list[str] = []
        for item in candidate:
            flattened.extend(tokenize(item))
        candidate_tokens = set(flattened)
    else:
        candidate_tokens = set(tokenize(candidate))
    if not query_tokens or not candidate_tokens:
        return 0.0
    return len(query_tokens & candidate_tokens) / len(query_tokens | candidate_tokens)


def token_coverage_score(query: str, candidate: str | list[str]) -> float:
    query_tokens = set(tokenize(query))
    if isinstance(candidate, list):
        flattened: list[str] = []
        for item in candidate:
            flattened.extend(tokenize(item))
        candidate_tokens = set(flattened)
    else:
        candidate_tokens = set(tokenize(candidate))
    if not query_tokens or not candidate_tokens:
        return 0.0
    return len(query_tokens & candidate_tokens) / len(query_tokens)


def cosine_similarity(left: list[float] | None, right: list[float] | None) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def local_embedding(text: str, dimensions: int = 64) -> list[float]:
    tokens = tokenize(text)
    if not tokens:
        return [0.0] * dimensions

    counts = Counter(tokens)
    vector = [0.0] * dimensions
    for token, weight in counts.items():
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=4).digest()
        slot = int.from_bytes(digest[:2], "big") % dimensions
        sign = 1.0 if digest[2] % 2 else -1.0
        vector[slot] += sign * float(weight)

    norm = math.sqrt(sum(value * value for value in vector))
    if not norm:
        return vector
    return [value / norm for value in vector]


def chunk_text(text: str, target_words: int = 90, overlap_words: int = 18) -> list[str]:
    words = text.split()
    if not words:
        return []
    if len(words) <= target_words:
        return [" ".join(words)]

    chunks: list[str] = []
    step = max(target_words - overlap_words, 1)
    for start in range(0, len(words), step):
        end = start + target_words
        chunk = " ".join(words[start:end]).strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(words):
            break
    return chunks


def excerpt(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."
