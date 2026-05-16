from __future__ import annotations

import math
import re
import struct
import wave
from io import BytesIO
from pathlib import Path

import requests
from flask import current_app


PUBLIC_AUDIO_TYPES = ["audio/webm", "audio/wav", "audio/mp4"]
MIME_TYPE_ALIASES = {
    "audio/webm": ("audio/webm", "webm"),
    "audio/wav": ("audio/wav", "wav"),
    "audio/x-wav": ("audio/wav", "wav"),
    "audio/wave": ("audio/wav", "wav"),
    "audio/mp4": ("audio/mp4", "mp4"),
    "audio/m4a": ("audio/mp4", "m4a"),
}


class VoiceServiceError(Exception):
    status_code = 400


class VoiceDisabledError(VoiceServiceError):
    pass


class VoiceValidationError(VoiceServiceError):
    pass


class VoiceProviderRequestError(VoiceServiceError):
    status_code = 502


class BaseVoiceProvider:
    provider_name = "base"

    def availability(self) -> tuple[bool, str | None]:
        return True, None

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str, language: str, filename: str) -> str:
        raise NotImplementedError

    def synthesize_speech(self, text: str, voice_id: str, language: str) -> tuple[bytes, str]:
        raise NotImplementedError


class StubVoiceProvider(BaseVoiceProvider):
    provider_name = "stub"

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str, language: str, filename: str) -> str:
        if not audio_bytes:
            raise VoiceValidationError("Please record a short voice message before sending it.")

        decoded = audio_bytes.decode("utf-8", errors="ignore").strip()
        if decoded.upper().startswith("TRANSCRIPT:"):
            transcript = decoded.split(":", 1)[1].strip()
            if transcript:
                return transcript

        return current_app.config["VOICE_STUB_TRANSCRIPT"]

    def synthesize_speech(self, text: str, voice_id: str, language: str) -> tuple[bytes, str]:
        spoken_text = text.strip() or "I am ready."
        return build_preview_wave(spoken_text), "audio/wav"


class OpenAIVoiceProvider(BaseVoiceProvider):
    provider_name = "openai"

    def __init__(self) -> None:
        self.base_url = current_app.config["LLM_BASE_URL"].rstrip("/")
        self.api_key = current_app.config["VOICE_API_KEY"] or current_app.config["LLM_API_KEY"]
        self.stt_model = current_app.config["VOICE_STT_MODEL"] or "gpt-4o-mini-transcribe"
        self.tts_model = current_app.config["VOICE_TTS_MODEL"] or "gpt-4o-mini-tts"
        self.default_voice = current_app.config["VOICE_TTS_VOICE_ID"] or "marin"

    def availability(self) -> tuple[bool, str | None]:
        if not self.api_key:
            return False, "Add a voice or OpenAI-compatible API key to enable browser voice."
        return True, None

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str, language: str, filename: str) -> str:
        response = self._post_multipart(
            "/audio/transcriptions",
            files={"file": (filename, audio_bytes, mime_type)},
            data={
                "model": self.stt_model,
                "response_format": "json",
                "language": language,
            },
        )
        text = (response.get("text") or "").strip()
        if not text:
            raise VoiceProviderRequestError("The voice provider returned an empty transcript.")
        return text

    def synthesize_speech(self, text: str, voice_id: str, language: str) -> tuple[bytes, str]:
        payload = {
            "model": self.tts_model,
            "input": text,
            "voice": voice_id or self.default_voice,
            "response_format": "mp3",
        }
        if language:
            payload["language"] = language
        if self.tts_model.startswith("gpt-4o"):
            payload["instructions"] = "Speak clearly, warmly, and briefly for a student support assistant."

        response = self._post_json("/audio/speech", payload, accept="audio/mpeg")
        return response.content, response.headers.get("Content-Type", "audio/mpeg")

    def _post_multipart(self, path: str, files: dict, data: dict) -> dict:
        response = requests.post(
            f"{self.base_url}{path}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            files=files,
            data={key: value for key, value in data.items() if value not in {None, ""}},
            timeout=90,
        )
        return parse_json_response(response)

    def _post_json(self, path: str, payload: dict, *, accept: str) -> requests.Response:
        response = requests.post(
            f"{self.base_url}{path}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": accept,
            },
            json=payload,
            timeout=90,
        )
        raise_for_voice_error(response)
        return response


class ElevenLabsVoiceProvider(BaseVoiceProvider):
    provider_name = "elevenlabs"

    def __init__(self) -> None:
        self.base_url = "https://api.elevenlabs.io"
        self.api_key = current_app.config["VOICE_API_KEY"]
        self.stt_model = current_app.config["VOICE_STT_MODEL"] or "scribe_v2"
        self.tts_model = current_app.config["VOICE_TTS_MODEL"] or "eleven_multilingual_v2"
        self.default_voice = current_app.config["VOICE_TTS_VOICE_ID"]

    def availability(self) -> tuple[bool, str | None]:
        if not self.api_key:
            return False, "Add an ElevenLabs API key to enable browser voice."
        if not self.default_voice:
            return False, "Set VOICE_TTS_VOICE_ID to a valid ElevenLabs voice ID."
        return True, None

    def transcribe_audio(self, audio_bytes: bytes, mime_type: str, language: str, filename: str) -> str:
        response = requests.post(
            f"{self.base_url}/v1/speech-to-text",
            headers={"xi-api-key": self.api_key},
            files={"file": (filename, audio_bytes, mime_type)},
            data={
                "model_id": self.stt_model,
                "language_code": language,
            },
            timeout=90,
        )
        payload = parse_json_response(response)
        text = (payload.get("text") or "").strip()
        if not text:
            raise VoiceProviderRequestError("The ElevenLabs transcript response was empty.")
        return text

    def synthesize_speech(self, text: str, voice_id: str, language: str) -> tuple[bytes, str]:
        response = requests.post(
            f"{self.base_url}/v1/text-to-speech/{voice_id or self.default_voice}",
            params={"output_format": "mp3_44100_128"},
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json={
                "text": text,
                "model_id": self.tts_model,
                "language_code": language,
            },
            timeout=90,
        )
        raise_for_voice_error(response)
        return response.content, response.headers.get("Content-Type", "audio/mpeg")


def get_voice_ui_config() -> dict:
    provider = build_voice_provider()
    enabled = bool(current_app.config["VOICE_ENABLED"])
    reason = None

    if not enabled:
        reason = "Voice mode is turned off for this project."
    else:
        enabled, reason = provider.availability()

    return {
        "enabled": enabled,
        "provider": provider.provider_name,
        "language": current_app.config["VOICE_LANGUAGE"],
        "voice_id": current_app.config["VOICE_TTS_VOICE_ID"] or getattr(provider, "default_voice", ""),
        "max_seconds": int(current_app.config["VOICE_MAX_SECONDS"]),
        "autoplay_default": bool(current_app.config["VOICE_AUTOPLAY_DEFAULT"]),
        "supported_mime_types": PUBLIC_AUDIO_TYPES,
        "disabled_reason": reason,
        "disclosure": "Spoken replies use an AI-generated voice.",
    }


def transcribe_audio_upload(audio_bytes: bytes, mime_type: str, filename: str, duration_ms: int | None = None) -> dict:
    config = get_voice_ui_config()
    if not config["enabled"]:
        raise VoiceDisabledError(config["disabled_reason"] or "Voice mode is not available right now.")

    canonical_mime, extension = normalize_audio_type(mime_type, filename)
    validate_audio_payload(audio_bytes, duration_ms)

    safe_filename = Path(filename or f"recording.{extension}").name or f"recording.{extension}"
    if "." not in safe_filename:
        safe_filename = f"{safe_filename}.{extension}"

    provider = build_voice_provider()
    transcript = provider.transcribe_audio(
        audio_bytes=audio_bytes,
        mime_type=canonical_mime,
        language=current_app.config["VOICE_LANGUAGE"],
        filename=safe_filename,
    )
    transcript = normalize_whitespace(transcript)
    if not transcript:
        raise VoiceProviderRequestError("The voice provider did not return a usable transcript.")

    return {
        "transcript": transcript,
        "provider": provider.provider_name,
        "mime_type": canonical_mime,
        "duration_ms": int(duration_ms or 0),
    }


def synthesize_spoken_reply(text: str, topic: str | None = None, route: str | None = None) -> tuple[bytes, str, str, str]:
    config = get_voice_ui_config()
    if not config["enabled"]:
        raise VoiceDisabledError(config["disabled_reason"] or "Voice mode is not available right now.")

    cleaned = build_spoken_reply_text(text, route=route, topic=topic)
    if not cleaned:
        raise VoiceValidationError("Please provide text to convert into speech.")

    provider = build_voice_provider()
    audio_bytes, content_type = provider.synthesize_speech(
        text=cleaned,
        voice_id=current_app.config["VOICE_TTS_VOICE_ID"],
        language=current_app.config["VOICE_LANGUAGE"],
    )
    if not audio_bytes:
        raise VoiceProviderRequestError("The voice provider returned empty audio.")
    return audio_bytes, content_type, cleaned, provider.provider_name


def build_spoken_reply_text(text: str, *, route: str | None = None, topic: str | None = None) -> str:
    cleaned = normalize_whitespace(re.sub(r"\[(?:S?\d+)\]", "", text or ""))
    if not cleaned:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    if route in {"clarify", "fallback"}:
        spoken = " ".join(sentences[:2]).strip()
    else:
        spoken = " ".join(sentences[:2]).strip() or cleaned

    if len(spoken) > 320:
        spoken = spoken[:317].rstrip(" ,;:") + "..."
    return spoken


def build_voice_provider() -> BaseVoiceProvider:
    provider_name = (current_app.config.get("VOICE_PROVIDER") or "stub").strip().lower()
    if provider_name == "elevenlabs":
        return ElevenLabsVoiceProvider()
    if provider_name == "openai":
        return OpenAIVoiceProvider()
    return StubVoiceProvider()


def validate_audio_payload(audio_bytes: bytes, duration_ms: int | None) -> None:
    if not audio_bytes:
        raise VoiceValidationError("Please record a short question before sending it.")

    max_size = int(current_app.config["MAX_CONTENT_LENGTH"])
    if len(audio_bytes) > max_size:
        raise VoiceValidationError("The recording is too large for this demo server.")

    if duration_ms and duration_ms > int(current_app.config["VOICE_MAX_SECONDS"]) * 1000:
        raise VoiceValidationError(
            f"Please keep voice questions under {int(current_app.config['VOICE_MAX_SECONDS'])} seconds."
        )


def normalize_audio_type(mime_type: str | None, filename: str | None = None) -> tuple[str, str]:
    raw_type = normalize_whitespace(mime_type or "").lower()
    if raw_type:
        base_type = raw_type.split(";", 1)[0].strip()
        if base_type in MIME_TYPE_ALIASES:
            return MIME_TYPE_ALIASES[base_type]

    extension = Path(filename or "").suffix.lower().lstrip(".")
    if extension == "webm":
        return "audio/webm", "webm"
    if extension == "wav":
        return "audio/wav", "wav"
    if extension in {"mp4", "m4a"}:
        return "audio/mp4", extension

    supported = ", ".join(PUBLIC_AUDIO_TYPES)
    raise VoiceValidationError(f"Unsupported audio format. Supported formats: {supported}.")


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def raise_for_voice_error(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = None
        try:
            payload = response.json()
            detail = payload.get("detail") or payload.get("message") or payload.get("error")
        except Exception:
            detail = response.text.strip() or None
        message = detail or "The voice provider request failed."
        raise VoiceProviderRequestError(message) from exc


def parse_json_response(response: requests.Response) -> dict:
    raise_for_voice_error(response)
    try:
        payload = response.json()
    except ValueError as exc:
        raise VoiceProviderRequestError("The voice provider returned an unreadable response.") from exc
    if not isinstance(payload, dict):
        raise VoiceProviderRequestError("The voice provider returned an unexpected response payload.")
    return payload


def build_preview_wave(text: str) -> bytes:
    # The stub provider returns a short playable waveform so the browser flow can be verified without a live API key.
    sample_rate = 22050
    duration = min(1.6, 0.45 + (len(text.split()) * 0.08))
    amplitude = 12000
    frequency = 392.0
    frames: list[bytes] = []

    for index in range(int(sample_rate * duration)):
        envelope = min(1.0, index / (sample_rate * 0.05))
        value = int(amplitude * envelope * math.sin((2.0 * math.pi * frequency * index) / sample_rate))
        frames.append(struct.pack("<h", value))

    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"".join(frames))
    return buffer.getvalue()
