const historyData = JSON.parse(document.getElementById("chat-history-data").textContent);
const chatFeed = document.getElementById("chat-feed");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const suggestionButtons = document.querySelectorAll(".suggestion-chip");
const voicePanel = document.getElementById("voice-panel");
const voiceRecordButton = document.getElementById("voice-record-button");
const voiceRecordLabel = document.getElementById("voice-record-label");
const voiceCancelButton = document.getElementById("voice-cancel-button");
const voiceAutoplay = document.getElementById("voice-autoplay");
const voiceStatus = document.getElementById("voice-status");
const voiceDisclosure = document.getElementById("voice-disclosure");
const voiceTranscriptPreview = document.getElementById("voice-transcript-preview");
const voiceTranscriptText = document.getElementById("voice-transcript-text");
const voiceSubmitButton = document.getElementById("voice-submit-button");
const voiceResetButton = document.getElementById("voice-reset-button");
const voiceReadyPill = document.getElementById("voice-ready-pill");

const routeLabels = {
  faq_direct: "Direct FAQ",
  retrieve_docs: "Verified Docs",
  clarify: "Needs Clarity",
  fallback: "Not Enough Data",
};

const voiceState = {
  enabled: false,
  browserSupported: Boolean(window.MediaRecorder && navigator.mediaDevices?.getUserMedia),
  mode: "idle",
  config: null,
  transcript: "",
  mediaRecorder: null,
  mediaStream: null,
  mimeType: "",
  chunks: [],
  startedAt: 0,
  timerId: null,
  durationMs: 0,
  discardNextRecording: false,
  isChatBusy: false,
  currentAudio: null,
  currentAudioButton: null,
};

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatText(value = "") {
  return escapeHtml(value).replaceAll("\n", "<br>");
}

function routeLabel(meta = {}) {
  return routeLabels[meta.route] || (meta.mode === "faq" ? "Direct FAQ" : "Assistant");
}

function confidenceText(confidence) {
  if (typeof confidence !== "number") {
    return "";
  }
  return `${Math.round(confidence * 100)}% confidence`;
}

function renderSources(sources = []) {
  if (!sources.length) {
    return "";
  }

  return `
    <div class="source-list">
      ${sources
        .map((source) => {
          const scoreMarkup =
            typeof source.score === "number"
              ? `<span class="source-score">${Math.round(source.score * 100)}% match</span>`
              : "";

          return `
            <article class="source-card">
              <div class="source-card-head">
                <span class="source-label">${escapeHtml(source.source_label || "Source")}</span>
                ${scoreMarkup}
              </div>
              <strong>${escapeHtml(source.title || "Untitled source")}</strong>
              <p>${formatText(source.excerpt || "")}</p>
            </article>
          `;
        })
        .join("")}
    </div>
  `;
}

function renderSuggestedReplies(replies = []) {
  if (!replies.length) {
    return "";
  }

  return `
    <div class="follow-up-wrap">
      ${replies
        .map(
          (reply) => `
            <button class="follow-up-chip" type="button" data-prompt="${escapeHtml(reply)}">${escapeHtml(reply)}</button>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderVoiceAction(role) {
  if (role !== "assistant" || !voiceState.enabled) {
    return "";
  }

  return `
    <div class="message-tools">
      <button class="voice-play-button" type="button">Play Voice</button>
    </div>
  `;
}

function appendMessage(role, content, meta = {}) {
  const wrapper = document.createElement("article");
  wrapper.className = `message message-${role}`;

  const hasMeta =
    role === "assistant" &&
    (Boolean(meta.route) || typeof meta.confidence === "number" || Boolean(meta.topic_label));

  const metaBar =
    hasMeta
      ? `
        <div class="message-meta">
          <span class="route-chip route-${meta.route || "assistant"}">${escapeHtml(routeLabel(meta))}</span>
          ${confidenceText(meta.confidence) ? `<span class="confidence-chip">${escapeHtml(confidenceText(meta.confidence))}</span>` : ""}
          ${meta.topic_label ? `<span class="topic-chip">${escapeHtml(meta.topic_label)}</span>` : ""}
        </div>
      `
      : "";

  wrapper.innerHTML = `
    <div class="message-bubble">
      <span class="message-role">${role === "assistant" ? "Assistant" : "You"}</span>
      ${metaBar}
      <p>${formatText(content)}</p>
      ${role === "assistant" ? renderVoiceAction(role) : ""}
      ${role === "assistant" ? renderSources(meta.sources) : ""}
      ${role === "assistant" ? renderSuggestedReplies(meta.suggested_replies) : ""}
    </div>
  `;

  if (role === "assistant") {
    wrapper.dataset.voiceText = content;
    wrapper.dataset.topic = meta.topic || "";
    wrapper.dataset.route = meta.route || "";
  }

  chatFeed.appendChild(wrapper);
  chatFeed.scrollTop = chatFeed.scrollHeight;
  return wrapper;
}

function hydrateHistory() {
  if (!historyData.length) {
    appendMessage(
      "assistant",
      "Welcome to the student query desk. Ask a college question and I will answer from approved FAQs or verified documents whenever possible.",
      {
        suggested_replies: [
          "What is the admission process?",
          "What is the fee structure?",
          "When are exams conducted?",
        ],
        sources: [],
      },
    );
    return;
  }

  historyData.forEach((item) => {
    appendMessage(item.role, item.content, item);
  });
}

function setComposerState(isBusy) {
  voiceState.isChatBusy = isBusy;
  messageInput.disabled = isBusy;
  sendButton.disabled = isBusy;
  sendButton.textContent = isBusy ? "Checking Sources..." : "Send Question";
  refreshVoiceControls();
}

function setVoiceStatus(mode, message) {
  voiceState.mode = mode;
  voicePanel.dataset.voiceState = mode;
  voiceStatus.textContent = message;
  voiceStatus.dataset.state = mode;

  if (voiceReadyPill) {
    voiceReadyPill.hidden = false;
    const pillLabels = {
      idle: "Voice ready",
      recording: "Listening",
      transcribing: "Transcribing",
      ready: "Transcript ready",
      answering: "Answering",
      speaking: "Speaking",
      error: "Voice issue",
      disabled: "Voice unavailable",
    };
    voiceReadyPill.textContent = pillLabels[mode] || "Voice ready";
  }

  if (voiceRecordLabel) {
    voiceRecordLabel.textContent = mode === "recording" ? "Stop Recording" : "Start Voice Question";
  }

  refreshVoiceControls();
}

function refreshVoiceControls() {
  if (!voicePanel) {
    return;
  }

  const interactive = voiceState.enabled && voiceState.browserSupported;
  const isRecording = voiceState.mode === "recording";
  const isWorking = ["transcribing", "answering"].includes(voiceState.mode) || voiceState.isChatBusy;
  const hasPreview = !voiceTranscriptPreview.hidden;

  voiceRecordButton.disabled = !interactive || isWorking;
  voiceRecordButton.dataset.state = isRecording ? "recording" : "idle";
  voiceCancelButton.hidden = !(isRecording || hasPreview);
  voiceCancelButton.disabled = isWorking && !isRecording;
  voiceAutoplay.disabled = !interactive;
}

function resetTranscriptPreview({ preserveInput = false } = {}) {
  voiceState.transcript = "";
  voiceTranscriptText.textContent = "";
  voiceTranscriptPreview.hidden = true;
  if (!preserveInput) {
    messageInput.value = "";
  }
  refreshVoiceControls();
}

function stopActiveAudio({ keepStatus = false } = {}) {
  if (voiceState.currentAudio) {
    voiceState.currentAudio.pause();
    voiceState.currentAudio.currentTime = 0;
  }

  if (voiceState.currentAudioButton) {
    voiceState.currentAudioButton.textContent = "Play Voice";
    voiceState.currentAudioButton.dataset.state = "idle";
  }

  voiceState.currentAudio = null;
  voiceState.currentAudioButton = null;

  if (!keepStatus && voiceState.enabled) {
    setVoiceStatus("idle", "Voice ready. Record a question or play an answer.");
  }
}

function preferredRecordingMimeType() {
  const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/wav"];
  return candidates.find((candidate) => !MediaRecorder.isTypeSupported || MediaRecorder.isTypeSupported(candidate)) || "";
}

function audioExtensionForMime(mimeType = "") {
  const normalized = mimeType.split(";")[0].trim();
  if (normalized === "audio/wav" || normalized === "audio/x-wav") {
    return "wav";
  }
  if (normalized === "audio/mp4") {
    return "mp4";
  }
  return "webm";
}

function updateRecordingTimer() {
  if (!voiceState.startedAt) {
    return;
  }

  const elapsedMs = Date.now() - voiceState.startedAt;
  voiceState.durationMs = elapsedMs;
  const seconds = Math.max(1, Math.round(elapsedMs / 1000));
  setVoiceStatus("recording", `Listening... tap again to stop (${seconds}s)`);
}

async function startVoiceRecording() {
  if (!voiceState.enabled || !voiceState.browserSupported) {
    const fallbackMessage = voiceState.config?.disabled_reason || "Voice input is not available in this browser right now.";
    setVoiceStatus("disabled", fallbackMessage);
    return;
  }

  resetTranscriptPreview();
  stopActiveAudio({ keepStatus: true });

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = preferredRecordingMimeType();
    const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

    voiceState.mediaStream = stream;
    voiceState.mediaRecorder = recorder;
    voiceState.mimeType = mimeType || recorder.mimeType || "audio/webm";
    voiceState.chunks = [];
    voiceState.discardNextRecording = false;
    voiceState.startedAt = Date.now();
    voiceState.durationMs = 0;

    recorder.addEventListener("dataavailable", (event) => {
      if (event.data && event.data.size > 0) {
        voiceState.chunks.push(event.data);
      }
    });

    recorder.addEventListener("stop", async () => {
      clearInterval(voiceState.timerId);
      voiceState.timerId = null;

      if (voiceState.mediaStream) {
        voiceState.mediaStream.getTracks().forEach((track) => track.stop());
      }

      const shouldDiscard = voiceState.discardNextRecording;
      const blob = new Blob(voiceState.chunks, { type: voiceState.mimeType || "audio/webm" });
      voiceState.mediaRecorder = null;
      voiceState.mediaStream = null;
      voiceState.chunks = [];

      if (shouldDiscard) {
        voiceState.discardNextRecording = false;
        setVoiceStatus("idle", "Voice ready. Record a question or play an answer.");
        return;
      }

      await transcribeRecordedAudio(blob, voiceState.mimeType, voiceState.durationMs);
    });

    recorder.start();
    setVoiceStatus("recording", "Listening... tap again to stop.");
    voiceState.timerId = window.setInterval(updateRecordingTimer, 1000);
  } catch (error) {
    setVoiceStatus("error", "Microphone access was blocked. Please allow audio recording and try again.");
  }
}

function stopVoiceRecording() {
  if (!voiceState.mediaRecorder || voiceState.mediaRecorder.state === "inactive") {
    return;
  }

  if (voiceState.timerId) {
    clearInterval(voiceState.timerId);
    voiceState.timerId = null;
  }

  setVoiceStatus("transcribing", "Transcribing your question...");
  voiceState.mediaRecorder.stop();
}

function cancelVoiceFlow() {
  if (voiceState.mode === "recording" && voiceState.mediaRecorder) {
    voiceState.discardNextRecording = true;
    voiceState.mediaRecorder.stop();
    return;
  }

  resetTranscriptPreview();
  setVoiceStatus("idle", "Voice ready. Record a question or play an answer.");
}

async function transcribeRecordedAudio(blob, mimeType, durationMs) {
  const extension = audioExtensionForMime(mimeType);
  const formData = new FormData();
  formData.append("audio", blob, `question.${extension}`);
  formData.append("duration_ms", String(durationMs || 0));

  try {
    const response = await fetch("/api/voice/transcribe", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "The transcript could not be created.");
    }

    voiceState.transcript = payload.transcript || "";
    if (!voiceState.transcript) {
      throw new Error("The transcript came back empty.");
    }

    voiceTranscriptText.textContent = voiceState.transcript;
    voiceTranscriptPreview.hidden = false;
    messageInput.value = voiceState.transcript;
    messageInput.focus();
    setVoiceStatus("ready", "Transcript ready. Review it or send it now.");
  } catch (error) {
    setVoiceStatus("error", error.message || "The voice transcript failed. Please try again.");
  }
}

async function fetchVoiceConfig() {
  voicePanel.hidden = false;

  if (!voiceState.browserSupported) {
    voiceState.enabled = false;
    voiceState.config = {
      enabled: false,
      autoplay_default: false,
      disclosure: "Spoken replies use an AI-generated voice.",
      disabled_reason: "This browser does not support microphone capture for the demo.",
    };
    voiceDisclosure.hidden = false;
    voiceDisclosure.textContent = voiceState.config.disclosure;
    setVoiceStatus("disabled", voiceState.config.disabled_reason);
    return;
  }

  try {
    const response = await fetch("/api/voice/config");
    const payload = await response.json();
    voiceState.config = payload;
    voiceState.enabled = Boolean(payload.enabled);
    voiceAutoplay.checked = Boolean(payload.autoplay_default);
    voiceDisclosure.hidden = !payload.disclosure;
    voiceDisclosure.textContent = payload.disclosure || "";

    if (voiceState.enabled) {
      setVoiceStatus("idle", "Voice ready. Record a question or play an answer.");
    } else {
      setVoiceStatus("disabled", payload.disabled_reason || "Voice mode is not configured yet.");
    }
  } catch (error) {
    voiceState.enabled = false;
    voiceState.config = {
      enabled: false,
      autoplay_default: false,
      disclosure: "Spoken replies use an AI-generated voice.",
      disabled_reason: "The voice assistant could not load its setup.",
    };
    voiceDisclosure.hidden = false;
    voiceDisclosure.textContent = voiceState.config.disclosure;
    setVoiceStatus("error", "Voice setup could not be loaded. Text chat still works normally.");
  }
}

async function speakAssistantReply(messageElement, { auto = false } = {}) {
  if (!voiceState.enabled || !messageElement) {
    return;
  }

  const button = messageElement.querySelector(".voice-play-button");
  if (!button) {
    return;
  }

  if (voiceState.currentAudioButton === button && voiceState.currentAudio) {
    if (voiceState.currentAudio.paused) {
      await voiceState.currentAudio.play();
      button.textContent = "Pause Voice";
      button.dataset.state = "playing";
      setVoiceStatus("speaking", "Playing the assistant's spoken reply...");
    } else {
      stopActiveAudio();
    }
    return;
  }

  stopActiveAudio({ keepStatus: true });
  button.disabled = true;
  button.textContent = auto ? "Auto-playing..." : "Loading Voice...";

  try {
    let audioUrl = messageElement.dataset.audioUrl;
    if (!audioUrl) {
      const response = await fetch("/api/voice/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: messageElement.dataset.voiceText || "",
          topic: messageElement.dataset.topic || "",
          route: messageElement.dataset.route || "",
        }),
      });

      if (!response.ok) {
        let errorMessage = "The spoken reply could not be generated.";
        try {
          const payload = await response.json();
          errorMessage = payload.error || errorMessage;
        } catch (error) {
          // Ignore JSON parsing failures for raw audio endpoints.
        }
        throw new Error(errorMessage);
      }

      const audioBlob = await response.blob();
      audioUrl = URL.createObjectURL(audioBlob);
      messageElement.dataset.audioUrl = audioUrl;
    }

    const audio = new Audio(audioUrl);
    voiceState.currentAudio = audio;
    voiceState.currentAudioButton = button;

    button.textContent = "Pause Voice";
    button.dataset.state = "playing";
    button.disabled = false;
    setVoiceStatus("speaking", auto ? "Playing the assistant's spoken reply..." : "Speaking the selected answer...");

    audio.addEventListener(
      "ended",
      () => {
        stopActiveAudio();
      },
      { once: true },
    );

    audio.addEventListener(
      "error",
      () => {
        stopActiveAudio({ keepStatus: true });
        setVoiceStatus("error", "Audio playback failed, but the text answer is still available.");
      },
      { once: true },
    );

    await audio.play();
  } catch (error) {
    button.disabled = false;
    button.textContent = "Play Voice";
    button.dataset.state = "idle";
    setVoiceStatus("error", error.message || "The spoken reply could not be generated.");
  }
}

async function submitPrompt(message, options = {}) {
  appendMessage("user", message);
  messageInput.value = "";
  setComposerState(true);

  if (options.origin === "voice") {
    setVoiceStatus("answering", "Sending your transcript through the grounded chat engine...");
    voiceTranscriptPreview.hidden = true;
  }

  const typing = document.createElement("article");
  typing.className = "message message-assistant";
  typing.innerHTML = `
    <div class="message-bubble typing-bubble">
      <span class="message-role">Assistant</span>
      <div class="message-meta">
        <span class="route-chip route-retrieve_docs">Checking Context</span>
      </div>
      <p>Reviewing the best verified answer for your question.</p>
    </div>
  `;
  chatFeed.appendChild(typing);
  chatFeed.scrollTop = chatFeed.scrollHeight;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const payload = await response.json();
    typing.remove();

    if (!response.ok) {
      appendMessage("assistant", payload.error || "Something went wrong while answering your question.", {
        mode: "rag",
        route: "fallback",
        confidence: 0,
        sources: [],
        suggested_replies: [],
      });
      if (options.origin === "voice") {
        setVoiceStatus("error", payload.error || "The question could not be answered.");
      }
      return;
    }

    const assistantMessage = appendMessage("assistant", payload.answer, {
      mode: payload.mode,
      route: payload.route,
      confidence: payload.confidence,
      topic: payload.topic,
      topic_label: payload.topic_label,
      needs_clarification: payload.needs_clarification,
      suggested_replies: payload.suggested_replies || [],
      sources: payload.sources || [],
    });

    if (options.origin === "voice") {
      if (voiceState.enabled && voiceAutoplay.checked) {
        speakAssistantReply(assistantMessage, { auto: true });
      } else {
        setVoiceStatus("idle", "Voice ready. Record another question or play this answer.");
      }
    }
  } catch (error) {
    typing.remove();
    appendMessage("assistant", "I could not reach the server just now. Please try again.", {
      mode: "rag",
      route: "fallback",
      confidence: 0,
      sources: [],
      suggested_replies: [],
    });

    if (options.origin === "voice") {
      setVoiceStatus("error", "The voice request reached the browser, but the server could not be reached.");
    }
  } finally {
    setComposerState(false);
    messageInput.focus();
  }
}

async function submitVoiceTranscript() {
  const transcript = messageInput.value.trim() || voiceState.transcript;
  if (!transcript) {
    setVoiceStatus("error", "The transcript is empty. Please record again.");
    return;
  }

  await submitPrompt(transcript, { origin: "voice" });
  resetTranscriptPreview({ preserveInput: true });
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }

  await submitPrompt(message);
});

suggestionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.prompt || "";
    messageInput.focus();
  });
});

chatFeed.addEventListener("click", async (event) => {
  const followUpButton = event.target.closest(".follow-up-chip");
  if (followUpButton) {
    const prompt = followUpButton.dataset.prompt || "";
    if (prompt) {
      await submitPrompt(prompt);
    }
    return;
  }

  const voiceButton = event.target.closest(".voice-play-button");
  if (voiceButton) {
    const messageElement = voiceButton.closest(".message");
    await speakAssistantReply(messageElement);
  }
});

voiceRecordButton.addEventListener("click", async () => {
  if (voiceState.mode === "recording") {
    stopVoiceRecording();
    return;
  }

  await startVoiceRecording();
});

voiceCancelButton.addEventListener("click", () => {
  cancelVoiceFlow();
});

voiceSubmitButton.addEventListener("click", async () => {
  await submitVoiceTranscript();
});

voiceResetButton.addEventListener("click", () => {
  resetTranscriptPreview();
  setVoiceStatus("idle", "Voice ready. Record a question or play an answer.");
});

async function bootstrap() {
  await fetchVoiceConfig();
  hydrateHistory();
}

bootstrap();
