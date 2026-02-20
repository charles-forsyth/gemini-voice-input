# 🎙️ Gemini Voice Input

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Speech--to--Text-4285F4?logo=googlecloud&logoColor=white)
![uv](https://img.shields.io/badge/managed_by-uv-purple)
![Linux Support](https://img.shields.io/badge/OS-Linux-FCC624?logo=linux&logoColor=black)

`gemini-voice-input` is a lightning-fast, Python-based utility that brings high-accuracy voice-to-text directly to your Linux clipboard. By leveraging the **Google Cloud Speech-to-Text V2 API (Chirp Model)**, it seamlessly converts spoken audio into text and automatically copies it to your clipboard for instant pasting anywhere.

---

## ✨ Features
- **Hands-Free Transcription:** Automatically stops recording after detecting a period of silence.
- **State-of-the-Art Accuracy:** Powered by Google's `chirp` foundation model.
- **Universal Clipboard Support:** Automatically detects and supports both **Wayland** (`wl-copy`) and **X11** (`xclip`).
- **Desktop Integration:** Includes bash scripts to trigger recordings via keyboard shortcuts with beautiful desktop notifications (`notify-send`) and audio cues.
- **Modern Python:** Managed by `uv` for blistering fast dependency resolution and environment isolation.

## 🚀 Quick Start

### 1. System Prerequisites
Ensure you have `uv` installed and one of the following clipboard managers:
```bash
# Debian/Ubuntu (X11)
sudo apt install xclip

# Debian/Ubuntu (Wayland)
sudo apt install wl-clipboard
```

### 2. Authentication
You must authenticate with Google Cloud to use the Speech-to-Text API. Ensure the Speech-to-Text V2 API is enabled in your Google Cloud Project.
```bash
gcloud auth application-default login
```
*(If your credentials do not automatically resolve the project ID, export it: `export GOOGLE_CLOUD_PROJECT="your-project-id"`)*

### 3. Usage
Run the core Python script directly:
```bash
uv run python voice_agent.py
```

## ⌨️ Desktop Shortcuts
To make this tool truly awesome, bind one of the provided scripts to a global keyboard shortcut (e.g., `Super + V`):

* **`voice_trigger.sh`** *(Recommended)*: Prevents overlapping recordings and sends rich desktop notifications when recording starts and finishes.
* **`run_voice.sh`**: A stealthier alternative that plays audio cues (`paplay`) on success or failure instead of visual notifications.

## 🧠 Architecture
1. **Trigger:** You press your shortcut key (`voice_trigger.sh`).
2. **Listen:** `voice_agent.py` wakes up, detects when you start speaking, and stops after `1.5s` of silence.
3. **Process:** Audio is temporarily buffered to `/tmp/voice_input.wav`.
4. **Cloud Inference:** Uploaded securely to `us-central1-speech.googleapis.com` for rapid Chirp 3 transcription.
5. **Paste:** The text lands directly in your system clipboard.

## 🛠️ Development & Testing
Follows the **Skywalker Development Workflow**.
* **Dependencies:** `pyproject.toml` managed by `uv`.
* **Tests:** `uv run pytest`
* **Linting/Formatting:** `uv run ruff check .` / `uv run ruff format .`
* **Types:** `uv run mypy src`
