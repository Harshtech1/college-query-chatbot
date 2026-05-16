const historyData = JSON.parse(document.getElementById("chat-history-data").textContent);
const suggestedPromptsData = JSON.parse(
  document.getElementById("suggested-prompts-data")?.textContent || "[]",
);
const chatFeed = document.getElementById("chat-feed");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sendButton = document.getElementById("send-button");
const suggestionButtons = document.querySelectorAll(".suggestion-chip");
const voiceRecordButton = document.getElementById("voice-record-button");
const voiceRecordLabel = document.getElementById("voice-record-label");
const voiceCancelButton = document.getElementById("voice-cancel-button");
const voiceAutoplay = document.getElementById("voice-autoplay");
const voiceToggleLabel = voiceAutoplay.closest("label");
const voiceStatus = document.getElementById("voice-status");
const voiceDisclosure = document.getElementById("voice-disclosure");
const voiceTranscriptPreview = document.getElementById("voice-transcript-preview");
const voiceTranscriptText = document.getElementById("voice-transcript-text");
const voiceSubmitButton = document.getElementById("voice-submit-button");
const voiceResetButton = document.getElementById("voice-reset-button");
const voiceReadyPill = document.getElementById("voice-ready-pill");

const routeLabels = {
  faq_direct: "Official Answer",
  retrieve_docs: "From University Documents",
  clarify: "Need One Detail",
  fallback: "Not Yet Verified",
};

const quickLinkPrompts = [
  {
    label: "Timetables",
    prompt: "Where is the official exam timetable published?",
  },
  {
    label: "Fee Circulars",
    prompt: "Where can I find the latest fee circular?",
  },
  {
    label: "PDFs",
    prompt: "Which official PDF notices are available for students?",
  },
];

const departmentDirectory = {
  admissions: {
    name: "Admissions Office",
    email: "admissions@university.edu",
    summary:
      "Use this for eligibility, application steps, document verification, or admission confirmation.",
    notices: [
      {
        label: "Admission Checklist PDF",
        title: "Admissions Checklist",
        fileName: "admissions-checklist.pdf",
        lines: [
          "Required documents should be confirmed against the latest admission notice.",
          "Keep mark sheets, identity proof, photographs, and category certificates ready where applicable.",
        ],
      },
      {
        label: "Verification Notice PDF",
        title: "Admissions Verification Notice",
        fileName: "admissions-verification-notice.pdf",
        lines: [
          "Document verification timelines are issued by the admissions office.",
          "Students should rely on the latest published notice for submission windows and exceptions.",
        ],
      },
    ],
  },
  exams: {
    name: "Examination Cell",
    email: "exams@university.edu",
    summary:
      "Use this for hall tickets, exam schedules, internal assessment notices, or timetable confirmation.",
    notices: [
      {
        label: "Exam Timetable PDF",
        title: "Examination Timetable Notice",
        fileName: "exam-timetable-notice.pdf",
        lines: [
          "Timetables should be cross-checked with the latest examination notice.",
          "Hall-ticket and venue updates are released separately when required.",
        ],
      },
      {
        label: "Hall Ticket Advisory PDF",
        title: "Hall Ticket Advisory",
        fileName: "hall-ticket-advisory.pdf",
        lines: [
          "Hall tickets are issued only after fee and attendance compliance is confirmed.",
          "Students should contact the examination cell for urgent verification requests.",
        ],
      },
    ],
  },
  accounts: {
    name: "Accounts Office",
    email: "accounts@university.edu",
    summary:
      "Use this for fee dues, payment confirmation, refund status, or the latest payable circular.",
    notices: [
      {
        label: "Fee Circular PDF",
        title: "Fee Circular",
        fileName: "fee-circular.pdf",
        lines: [
          "The payable amount depends on program and semester.",
          "Students should rely on the latest fee circular before making payment.",
        ],
      },
      {
        label: "Payment Advisory PDF",
        title: "Accounts Payment Advisory",
        fileName: "accounts-payment-advisory.pdf",
        lines: [
          "Payment support is available through the accounts office during working hours.",
          "Students should keep transaction references ready for reconciliation.",
        ],
      },
    ],
  },
  attendance: {
    name: "Attendance Department",
    email: "attendance@university.edu",
    summary:
      "Use this for minimum attendance, shortage review, justification records, or attendance corrections.",
    notices: [
      {
        label: "Attendance Policy PDF",
        title: "Attendance Policy",
        fileName: "attendance-policy.pdf",
        lines: [
          "Minimum attendance thresholds should be checked against the current academic policy.",
          "Any shortage review depends on departmental review and approved justifications.",
        ],
      },
      {
        label: "Shortage Review PDF",
        title: "Attendance Shortage Review Note",
        fileName: "attendance-shortage-review.pdf",
        lines: [
          "Shortage cases require supporting records and timely department follow-up.",
          "Students should contact the attendance department for case-specific confirmation.",
        ],
      },
    ],
  },
};

const topicEscalationMap = {
  admissions: ["admissions"],
  fees: ["accounts"],
  exams: ["exams"],
  attendance: ["attendance"],
  timetable: ["exams"],
  courses: ["admissions"],
  faculty: ["exams"],
  policy: ["admissions", "exams"],
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
  return routeLabels[meta.route] || (meta.mode === "faq" ? "Official Answer" : "Academic Service Interface");
}

function confidenceText(confidence) {
  if (typeof confidence !== "number") {
    return "";
  }
  return `${Math.round(confidence * 100)}% confidence`;
}

function sourceLabel(source = {}) {
  if (source.kind === "faq") {
    return "Official FAQ";
  }
  if (source.kind === "document" && source.source_label) {
    return `University Document ${source.source_label}`;
  }
  return source.source_label || "University Source";
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
                <span class="source-label">${escapeHtml(sourceLabel(source))}</span>
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

function renderQuickLinks() {
  return `
    <div class="quick-link-row">
      <span>Quick links</span>
      <div class="quick-link-pills">
        ${quickLinkPrompts
          .map(
            (item) => `
              <button class="quick-link-chip" type="button" data-prompt="${escapeHtml(item.prompt)}">${escapeHtml(item.label)}</button>
            `,
          )
          .join("")}
      </div>
    </div>
  `;
}

function renderFeedbackWidget() {
  return `
    <div class="feedback-row" data-feedback-state="idle">
      <span>Was this helpful?</span>
      <div class="feedback-actions">
        <button class="feedback-button" type="button" data-feedback="yes">Yes</button>
        <button class="feedback-button" type="button" data-feedback="no">No</button>
      </div>
      <span class="feedback-response" hidden>Thanks for the feedback.</span>
    </div>
  `;
}

function serializeNotice(notice) {
  return escapeHtml(encodeURIComponent(JSON.stringify(notice)));
}

function resolveEscalations(meta = {}) {
  if (!["clarify", "fallback"].includes(meta.route)) {
    return [];
  }

  const mappedKeys = topicEscalationMap[meta.topic] || [];
  if (mappedKeys.length) {
    return mappedKeys.map((key) => departmentDirectory[key]).filter(Boolean);
  }

  if (meta.route === "clarify" || meta.route === "fallback") {
    return Object.values(departmentDirectory);
  }

  return [];
}

function renderEscalationCards(meta = {}) {
  const cards = resolveEscalations(meta);
  if (!cards.length) {
    return "";
  }

  return `
    <section class="escalation-grid" aria-label="Department escalation options">
      ${cards
        .map((card) => {
          const notices = card.notices
            .map((notice) => {
              const noticePayload = {
                ...notice,
                department: card.name,
              };
              return `
                <a
                  class="notice-chip"
                  href="#"
                  data-notice="${serializeNotice(noticePayload)}"
                >${escapeHtml(notice.label)}</a>
              `;
            })
            .join("");

          return `
            <article class="escalation-card">
              <div class="escalation-card-head">
                <span>Department Escalation</span>
                <strong>${escapeHtml(card.name)}</strong>
              </div>
              <p>${escapeHtml(card.summary)}</p>
              <div class="department-actions">
                <a
                  class="contact-link"
                  href="mailto:${escapeHtml(card.email)}?subject=${encodeURIComponent(`Student Query - ${card.name}`)}"
                >Contact Department</a>
              </div>
              <div class="department-notices">
                ${notices}
              </div>
            </article>
          `;
        })
        .join("")}
    </section>
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
      <span class="message-role">${role === "assistant" ? "Academic Service Interface" : "You"}</span>
      ${metaBar}
      <p>${formatText(content)}</p>
      ${role === "assistant" ? renderVoiceAction(role) : ""}
      ${role === "assistant" ? renderSources(meta.sources) : ""}
      ${role === "assistant" ? renderSuggestedReplies(meta.suggested_replies) : ""}
      ${role === "assistant" ? renderEscalationCards(meta) : ""}
      ${role === "assistant" ? renderQuickLinks() : ""}
      ${role === "assistant" ? renderFeedbackWidget() : ""}
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

function welcomePrompts() {
  if (suggestedPromptsData.length) {
    return suggestedPromptsData.slice(0, 2);
  }

  return [
    "What is the admission process?",
    "What is the fee structure?",
  ];
}

function hydrateHistory() {
  if (!historyData.length) {
    appendMessage(
      "assistant",
      "Welcome to the Academic Service Interface. Ask about admissions, fees, examinations, attendance, timetables, or official notices, and I will answer from approved FAQs or university documents whenever possible.",
      {
        suggested_replies: welcomePrompts(),
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
  sendButton.textContent = isBusy ? "Verifying..." : "Submit";
  refreshVoiceControls();
}

function setVoiceStatus(mode, message) {
  voiceState.mode = mode;
  voiceStatus.textContent = message;
  voiceStatus.dataset.state = mode;

  if (voiceReadyPill) {
    if (mode === "disabled" || !voiceState.enabled) {
      voiceReadyPill.hidden = true;
    } else {
      voiceReadyPill.hidden = false;
      const pillLabels = {
        idle: "Voice ready",
        recording: "Listening",
        transcribing: "Transcribing",
        ready: "Transcript ready",
        answering: "Checking answer",
        speaking: "Voice reply",
        error: "Voice issue",
      };
      voiceReadyPill.textContent = pillLabels[mode] || "Voice ready";
    }
  }

  if (voiceRecordLabel) {
    voiceRecordLabel.textContent = mode === "recording" ? "Stop" : "Voice";
  }

  refreshVoiceControls();
}

function refreshVoiceControls() {
  const interactive = voiceState.enabled && voiceState.browserSupported;
  const isRecording = voiceState.mode === "recording";
  const isWorking = ["transcribing", "answering"].includes(voiceState.mode) || voiceState.isChatBusy;
  const hasPreview = !voiceTranscriptPreview.hidden;

  voiceRecordButton.disabled = !interactive || isWorking;
  voiceRecordButton.dataset.state = isRecording ? "recording" : "idle";
  voiceCancelButton.hidden = !(isRecording || hasPreview);
  voiceCancelButton.disabled = isWorking && !isRecording;
  voiceAutoplay.disabled = !interactive;
  if (voiceToggleLabel) {
    voiceToggleLabel.hidden = !voiceState.enabled;
    voiceToggleLabel.style.display = voiceState.enabled ? "" : "none";
  }
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
    setVoiceStatus("idle", "Voice ready. Record a question or continue typing.");
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
        setVoiceStatus("idle", "Voice ready. Record a question or continue typing.");
        return;
      }

      await transcribeRecordedAudio(blob, voiceState.mimeType, voiceState.durationMs);
    });

    recorder.start();
    setVoiceStatus("recording", "Listening... tap again to stop.");
    voiceState.timerId = window.setInterval(updateRecordingTimer, 1000);
  } catch (error) {
    setVoiceStatus("error", "Microphone access was blocked. Please allow recording and try again.");
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
  setVoiceStatus("idle", "Voice ready. Record a question or continue typing.");
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
  if (!voiceState.browserSupported) {
    voiceState.enabled = false;
    voiceState.config = {
      enabled: false,
      autoplay_default: false,
      disclosure: "Spoken replies use an AI-generated voice.",
      disabled_reason: "This browser does not support microphone capture for the current session.",
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
      setVoiceStatus("idle", "Voice ready. Record a question or continue typing.");
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
      setVoiceStatus("speaking", "Playing the spoken reply...");
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
    setVoiceStatus("speaking", auto ? "Playing the spoken reply..." : "Speaking the selected answer...");

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
    setVoiceStatus("answering", "Checking approved FAQs and official documents...");
    voiceTranscriptPreview.hidden = true;
  }

  const typing = document.createElement("article");
  typing.className = "message message-assistant";
  typing.innerHTML = `
    <div class="message-bubble typing-bubble">
      <span class="message-role">Academic Service Interface</span>
      <div class="message-meta">
        <span class="route-chip route-retrieve_docs">Reviewing Records</span>
      </div>
      <p>Checking approved FAQs and official documents for the most reliable answer.</p>
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
      appendMessage(
        "assistant",
        payload.error || "I could not verify that request just now. Please try again in a moment.",
        {
          mode: "rag",
          route: "fallback",
          confidence: 0,
          sources: [],
          suggested_replies: welcomePrompts(),
        },
      );
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
    appendMessage(
      "assistant",
      "I could not reach the service just now. Please try again, or contact the relevant department if the matter is urgent.",
      {
        mode: "rag",
        route: "fallback",
        confidence: 0,
        sources: [],
        suggested_replies: welcomePrompts(),
      },
    );

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

function handleFeedbackSelection(button) {
  const row = button.closest(".feedback-row");
  if (!row) {
    return;
  }

  const selected = button.dataset.feedback || "";
  const buttons = row.querySelectorAll(".feedback-button");
  const response = row.querySelector(".feedback-response");

  buttons.forEach((item) => {
    item.dataset.state = item === button ? "selected" : "idle";
    item.disabled = true;
  });

  row.dataset.feedbackState = selected;
  if (response) {
    response.hidden = false;
    response.textContent =
      selected === "yes"
        ? "Thanks. We will keep this answer style."
        : "Thanks. We will use that to improve future replies.";
  }
}

function escapePdfText(value = "") {
  return String(value)
    .replaceAll("\\", "\\\\")
    .replaceAll("(", "\\(")
    .replaceAll(")", "\\)");
}

function buildNoticePdf(notice) {
  const lines = [
    notice.title || "Official Notice",
    `Department: ${notice.department || "University Office"}`,
    "",
    ...(notice.lines || []),
  ];

  const streamLines = ["BT", "/F1 18 Tf", "72 750 Td"];
  lines.forEach((line, index) => {
    if (index > 0) {
      streamLines.push("0 -24 Td");
    }
    streamLines.push(`(${escapePdfText(line)}) Tj`);
  });
  streamLines.push("ET");

  const stream = streamLines.join("\n");
  const objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    "<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
    `<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`,
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
  ];

  let pdf = "%PDF-1.4\n";
  const offsets = [0];

  objects.forEach((body, index) => {
    offsets[index + 1] = pdf.length;
    pdf += `${index + 1} 0 obj\n${body}\nendobj\n`;
  });

  const xrefOffset = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += "0000000000 65535 f \n";
  for (let index = 1; index <= objects.length; index += 1) {
    pdf += `${String(offsets[index]).padStart(10, "0")} 00000 n \n`;
  }
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;

  return new Blob([pdf], { type: "application/pdf" });
}

function downloadNoticePdf(notice) {
  const blob = buildNoticePdf(notice);
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = notice.fileName || "official-notice.pdf";
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
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
  const followUpButton = event.target.closest(".follow-up-chip, .quick-link-chip");
  if (followUpButton) {
    const prompt = followUpButton.dataset.prompt || "";
    if (prompt) {
      await submitPrompt(prompt);
    }
    return;
  }

  const feedbackButton = event.target.closest(".feedback-button");
  if (feedbackButton) {
    handleFeedbackSelection(feedbackButton);
    return;
  }

  const noticeButton = event.target.closest(".notice-chip");
  if (noticeButton) {
    event.preventDefault();
    const rawNotice = noticeButton.dataset.notice || "";
    if (rawNotice) {
      downloadNoticePdf(JSON.parse(decodeURIComponent(rawNotice)));
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
  setVoiceStatus("idle", "Voice ready. Record a question or continue typing.");
});

async function bootstrap() {
  await fetchVoiceConfig();
  hydrateHistory();
}

bootstrap();
