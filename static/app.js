// static/app.js
let mediaRecorder = null;
let chunks = [];
let sessionId = null;
let transcript = []; // store full conversation locally
let currentAudio = null; // for stop-audio / barge-in
let currentVoiceId = null; // if you later add data-voice to agent cards

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const stopAudioBtn = document.getElementById("stopAudioBtn");
const downloadBtn = document.getElementById("downloadBtn");
const clearBtn = document.getElementById("clearBtn");
const chatEl = document.getElementById("chat");
const metricsEl = document.getElementById("metrics");
const modeSelect = document.getElementById("mode");
const textInput = document.getElementById("textInput");
const sendTextBtn = document.getElementById("sendTextBtn");
const agentCards = document.querySelectorAll(".agent-card");
const buyCaseBtn = document.getElementById("buyCaseBtn");
const noBuyCaseBtn = document.getElementById("noBuyCaseBtn");
const investBanner = document.getElementById("investBanner");

let sequenceCancelled = false; // to stop multi-chunk playback

function setMetrics(m) {
  if (!m) {
    metricsEl.textContent = "Waiting for first interaction…";
    return;
  }
  metricsEl.textContent =
    `ASR: ${m.asr_ms} ms | LLM: ${m.llm_ms} ms | TTS: ${m.tts_ms} ms | Total: ${m.total_ms} ms`;
}

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  const span = document.createElement("span");
  span.textContent = text;
  div.appendChild(span);
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;

  transcript.push({ role, text });

  if (transcript.length > 0) {
    downloadBtn.disabled = false;
  }
}

function stopCurrentAudio() {
  sequenceCancelled = true;
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio = null;
  }
  stopAudioBtn.disabled = true;
}

function playAudioFromBase64List(b64List) {
  if (!b64List || b64List.length === 0) return;

  sequenceCancelled = false;
  let index = 0;

  const playNext = () => {
    if (sequenceCancelled || index >= b64List.length) {
      stopAudioBtn.disabled = true;
      currentAudio = null;
      return;
    }

    const b64 = b64List[index];
    const byteChars = atob(b64);
    const byteNums = new Array(byteChars.length);
    for (let i = 0; i < byteChars.length; i++) {
      byteNums[i] = byteChars.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNums);
    const audioBlob = new Blob([byteArray], { type: "audio/mpeg" });
    const url = URL.createObjectURL(audioBlob);
    const audio = new Audio(url);
    currentAudio = audio;
    stopAudioBtn.disabled = false;

    audio.onended = () => {
      URL.revokeObjectURL(url);
      if (!sequenceCancelled) {
        index += 1;
        playNext();
      } else {
        stopAudioBtn.disabled = true;
        currentAudio = null;
      }
    };

    audio.play().catch(err => {
      console.error("Audio play failed", err);
      URL.revokeObjectURL(url);
      // Try to continue with next chunk
      index += 1;
      playNext();
    });
  };

  playNext();
}

function downloadTranscript() {
  if (transcript.length === 0) {
    alert("No transcript available yet.");
    return;
  }

  const lines = transcript.map(
    (m) => `${m.role.toUpperCase()}: ${m.text}`
  );
  const blob = new Blob([lines.join("\n\n")], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "voice_agent_transcript.txt";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function clearConversation() {
  sessionId = null;
  transcript = [];
  chatEl.innerHTML = "";
  setMetrics(null);
  downloadBtn.disabled = true;
  stopCurrentAudio();
}

// INVEST BANNER VISIBILITY
function updateInvestBanner() {
  if (modeSelect.value === "invest") {
    investBanner.classList.add("visible");
  } else {
    investBanner.classList.remove("visible");
  }
}

// ---- AGENT CARDS (multiple personas) ----
function setActiveAgent(card) {
  agentCards.forEach(c => c.classList.remove("active"));
  card.classList.add("active");

  const mode = card.dataset.mode || "assistant";
  const voice = card.dataset.voice || null;

  modeSelect.value = mode;
  currentVoiceId = voice;
  updateInvestBanner();
}

// init first agent as default
if (agentCards.length > 0) {
  setActiveAgent(agentCards[0]);
}

agentCards.forEach(card => {
  card.addEventListener("click", () => setActiveAgent(card));
});

// Also update banner when mode select changes manually
modeSelect.addEventListener("change", updateInvestBanner);

// ---- RECORDING / VOICE TURN ----
async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    chunks = [];
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: "audio/webm"
    });

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { type: "audio/webm" });
      await sendAudio(blob);
      stream.getTracks().forEach(t => t.stop());
    };

    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;
    setMetrics(null);
  } catch (err) {
    console.error(err);
    alert("Microphone error: " + err.message);
  }
}

async function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    stopBtn.disabled = true;
  }
}

async function sendAudio(blob) {
  try {
    const formData = new FormData();
    formData.append("audio", blob, "audio.webm");
    if (sessionId) {
      formData.append("session_id", sessionId);
    }
    formData.append("mode", modeSelect.value);
    if (currentVoiceId) {
      formData.append("voice_id", currentVoiceId);
    }

    const resp = await fetch("/api/conversation/turn", {
      method: "POST",
      body: formData,
    });

    const data = await resp.json();
    console.log("voice turn response:", data);

    if (!resp.ok) {
      throw new Error(data.error || "Request failed");
    }

    sessionId = data.session_id;

    const userText =
  typeof data.user_text === "string" && data.user_text.trim().length > 0
    ? data.user_text
    : "[voice input – no text recognised]";

    const assistantText = data.assistant_text || "(no reply text)";

    addMessage("user", userText);
    addMessage("assistant", assistantText);
    setMetrics(data.metrics || null);

    const chunksArr =
      data.audio_base64_chunks && data.audio_base64_chunks.length
        ? data.audio_base64_chunks
        : data.audio_base64
        ? [data.audio_base64]
        : [];

    if (chunksArr.length > 0) {
      playAudioFromBase64List(chunksArr);
    }
  } catch (err) {
    console.error(err);
    alert("Error: " + err.message);
  } finally {
    startBtn.disabled = false;
  }
}

// ---- TEXT TURN HELPERS ----
async function sendTextToBackend(text) {
  setMetrics(null);

  try {
    const body = {
      text,
      mode: modeSelect.value,
    };
    if (sessionId) {
      body.session_id = sessionId;
    }
    if (currentVoiceId) {
      body.voice_id = currentVoiceId;
    }

    const resp = await fetch("/api/conversation/text-turn", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.error || "Request failed");
    }

    sessionId = data.session_id;
    addMessage("assistant", data.assistant_text);
    setMetrics(data.metrics);

    const chunksArr =
      data.audio_base64_chunks && data.audio_base64_chunks.length
        ? data.audio_base64_chunks
        : data.audio_base64
        ? [data.audio_base64]
        : [];

    if (chunksArr.length > 0) {
      playAudioFromBase64List(chunksArr);
    }
  } catch (err) {
    console.error(err);
    alert("Error: " + err.message);
  }
}

async function sendTextMessage() {
  const text = textInput.value.trim();
  if (!text) return;

  addMessage("user", text);
  textInput.value = "";
  await sendTextToBackend(text);
}

// ---- INVEST DECISION SCENARIOS ----
async function sendDecisionScenario(kind) {
  // Force into invest mode for this helper
  modeSelect.value = "invest";
  updateInvestBanner();

  let userVisibleMessage;
  let backendPrompt;

  if (kind === "buy") {
    userVisibleMessage = "Show me the BUY-side view for this stock.";
    backendPrompt =
      "Based on the stock we were just discussing, present an EDUCATIONAL BUY-side case only. " +
      "Explain why some long-term investors might consider buying, using this structure: " +
      "1) main positive thesis, 2) key supporting points, 3) what kind of generic investor profile this might appeal to. " +
      "Do NOT give personalised advice, do NOT say 'you should buy', and include a clear disclaimer that this is not a recommendation.";
  } else {
    userVisibleMessage = "Show me the DON’T-BUY / WAIT view for this stock.";
    backendPrompt =
      "Based on the stock we were just discussing, present an EDUCATIONAL DON'T-BUY / WAIT case only. " +
      "Explain why some investors might decide not to enter or prefer to wait, using this structure: " +
      "1) main concerns, 2) key risks or uncertainties, 3) what kind of generic investor profile might choose to avoid or wait. " +
      "Do NOT give personalised advice, and include a clear disclaimer that this is not a recommendation.";
  }

  addMessage("user", userVisibleMessage);
  await sendTextToBackend(backendPrompt);
}

// ---- EVENT LISTENERS ----
startBtn.addEventListener("click", startRecording);
stopBtn.addEventListener("click", stopRecording);
downloadBtn.addEventListener("click", downloadTranscript);
clearBtn.addEventListener("click", clearConversation);
stopAudioBtn.addEventListener("click", stopCurrentAudio);

sendTextBtn.addEventListener("click", sendTextMessage);
textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendTextMessage();
  }
});

buyCaseBtn.addEventListener("click", () => sendDecisionScenario("buy"));
noBuyCaseBtn.addEventListener("click", () => sendDecisionScenario("no-buy"));

// Initialize metrics & banner
setMetrics(null);
updateInvestBanner();
