
<div align="center">

# 🎙️ **Falcon Voice Agent**

### *Real-Time Voice Assistant with Murf Falcon TTS, AssemblyAI ASR & Google Gemini LLM*

<img src="https://img.shields.io/badge/Backend-Python%2FFlask-blue?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-orange?style=for-the-badge"/>
<img src="https://img.shields.io/badge/TTS-Murf%20Falcon-green?style=for-the-badge"/>
<img src="https://img.shields.io/badge/ASR-AssemblyAI-yellow?style=for-the-badge"/>
<img src="https://img.shields.io/badge/LLM-Google%20Gemini-red?style=for-the-badge"/>

<br><br>

**A full voice-based AI system designed for the Murf Hackathon.
Speak → Transcribe → Think → Talk back — all in real-time.**

</div>

---

# 🚀 **Features**

### 🎤 **End-to-End Voice AI**

* Browser mic recording
* Real-time transcription (AssemblyAI)
* Gemini LLM smart responses
* Murf Falcon voice output
* Low-latency round-trip

### 🤖 **Multiple AI Personas**

| Persona                   | Purpose                              |
| ------------------------- | ------------------------------------ |
| Assistant                 | General helpful agent                |
| Language Coach            | Grammar correction, English learning |
| Support Agent             | Polite, structured customer support  |
| Storyteller               | Expressive narration                 |
| **Investment Consultant** | Deep stock analysis (10+ yrs exp)    |

### 📈 **Investment Consultant Mode**

* Understands short stock queries like `"Tata Motors"`, `"TSLA"`
* Returns **indexed professional analysis**
* Includes:

  * Company snapshot
  * Business model & moat
  * Growth drivers
  * Financial quality
  * Key risks
  * General investor suitability
  * Balanced decision helper
  * **NOT financial advice disclaimer**
* 📌 *BUY-case* & *DON’T-BUY-case* buttons
* ⚠️ **Investment banner auto-appears**

---

# 🔥 **Tech Stack**

| Layer         | Technology                |
| ------------- | ------------------------- |
| Frontend      | HTML5, CSS3, JavaScript   |
| Backend       | Python, Flask             |
| ASR           | AssemblyAI                |
| LLM Reasoning | Google Gemini             |
| TTS           | Murf Falcon TTS           |
| State         | In-Memory Session Manager |

---

# 🗂️ **Project Structure**

```
voice_agent/
├── app.py
├── config.py
├── requirements.txt
├── .env
├── routes/
│   └── voice.py
├── services/
│   ├── assemblyai_client.py
│   ├── google_llm.py
│   ├── murf_client.py
│   └── conversation_manager.py
└── static/
    ├── index.html
    └── app.js
```

---

# ⚙️ **Installation & Setup**

### 1️⃣ Clone Repo

```bash
git clone https://github.com/yourusername/voice-agent.git
cd voice-agent
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Create `.env` File

```
ASSEMBLYAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
MURF_API_KEY=your_key_here
MURF_VOICE_ID=your_default_voice_id
GEMINI_MODEL=gemini-2.5-flash
```

---

# ▶️ **Run the App**

```bash
python app.py
```

Open your browser:

> [http://127.0.0.1:5000](http://127.0.0.1:5000)

You must allow **microphone permissions**.

---

# 🎮 **How to Use**

### 🎙 Voice Mode

1. Click **Start Talking**
2. Speak naturally
3. Click **Stop & Send**
4. View:

   * ASR transcript
   * LLM reply
   * Murf TTS audio playback (multi-chunk)

### ⌨️ Text Mode

* Type in the message box
* Click **Send**

### 🎚 Persona Selection

Choose an AI persona:

* Support
* Coach
* Storyteller
* **Investment Consultant**
* Default Assistant

### 📈 Investment Tools

* **Buy-side view button**
* **Don’t-buy/Wait view button**
* Automatic stock analysis with disclaimers

### 🔊 Audio Features

* Multi-chunk TTS playback
* Stop audio mid-playback

### 📄 Transcript

* Download entire chat as `.txt`

### 🌗 Theme Toggle

* Light / Dark mode
* Stored in localStorage

---

# 🧠 **How It Works**

### 1. Frontend

* Records audio using `MediaRecorder`
* Sends audio blob to Flask backend
* Renders chat bubbles
* Plays TTS audio sequentially
* Handles persona switching + UI

### 2. Backend Pipeline

```
Audio → AssemblyAI → text
text + history → Gemini → response
response → chunk splitter → Murf TTS
Murf TTS → multi-part audio → frontend
```

### 3. Chunked TTS

* Murf limit = 3000 chars
* We chunk at **≤2800** characters
* Generate multiple audio clips
* Frontend plays them in order

---

# 🐞 **Common Issues & Fixes**

### ❌ ASR returns nothing

**Fix:** Speak slightly slower or longer
Try:

> “Explain Tata Motors stock for long-term investors.”

### ❌ Murf error: “Text too long”

You’re using old code.
Make sure chunking is enabled in `voice.py`.

### ❌ 404 favicon error

Harmless — browser asks for favicon.
Optional: add `static/favicon.ico`.

### ❌ No audio playback

Check browser console for:

```
Audio play failed
```

Often due to:

* Autoplay blocked → user needs to “click” somewhere on page
* Corrupted base64 → check backend logs

---

# 🔐 **API Keys**

| Service     | Purpose                 |
| ----------- | ----------------------- |
| AssemblyAI  | Speech-to-Text          |
| Gemini      | Reasoning + personality |
| Murf Falcon | High-quality TTS        |

Store them securely in `.env`.

---

# 🚀 **Deployment Guide**

## ⭐ Deploy on Render.com

1. Create new Web Service
2. Upload repo
3. Add environment variables
4. Use start command:

   ```bash
   python app.py
   ```
5. Enable "Always On"

## ⭐ Deploy on Railway.app

* Railway detects Python automatically
* Add your `.env` variables
* Deploy

## ⭐ Deploy on Replit (easy)

* Drop entire folder
* Set secrets
* Run

