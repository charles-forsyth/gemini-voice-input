# Gemini Voice Input

## Project Overview
`gemini-voice-input` is a Python-based utility that enables voice-to-text input directly to the system clipboard using the Gemini API. It records audio from the microphone until a period of silence is detected, transcribes the speech using the `gemini-1.5-flash` model via the `google-generativeai` SDK, and automatically copies the transcribed text to the clipboard (supporting both Wayland via `wl-copy` and X11 via `xclip`).

The project uses `uv` for modern Python dependency management and includes bash scripts for seamless integration with desktop environments (e.g., binding to a global keyboard shortcut).

**Core Technologies:**
*   **Python:** >= 3.12
*   **Package Manager:** `uv`
*   **Audio Recording:** `sounddevice`, `numpy`, `scipy`
*   **Transcription:** `google-generativeai` (Gemini 1.5 Flash)
*   **System Integration:** Bash, `wl-clipboard` / `xclip`, `notify-send`, `paplay`

## Building and Running

### Prerequisites
*   Ensure `uv` is installed on your system.
*   Ensure you have either `wl-clipboard` (for Wayland) or `xclip` (for X11) installed for clipboard support.
*   A valid Google API Key is required.

### Running the Agent Directly
You can run the core Python script directly using `uv`. Make sure to provide your API key:
```bash
export GOOGLE_API_KEY="your_api_key_here"
uv run python voice_agent.py
```

### Using the Trigger Scripts
The project provides two bash scripts intended to be bound to system keyboard shortcuts:

1.  **`voice_trigger.sh` (Recommended for Desktop Integration):**
    This script is designed for UI feedback. It ensures only one instance is running, sends desktop notifications using `notify-send` when listening starts and when the transcription is ready to be pasted.
    ```bash
    ./voice_trigger.sh
    ```

2.  **`run_voice.sh`:**
    A simpler alternative that logs output to `/tmp/voice_debug.log` and plays audio cues (`paplay`) on success or failure instead of visual notifications.
    ```bash
    ./run_voice.sh
    ```

## Architecture and Flow
1.  **Activation:** The script is triggered (e.g., via a keyboard shortcut executing `voice_trigger.sh`).
2.  **Recording:** `voice_agent.py` listens to the microphone using `sounddevice`, dynamically waiting for speech to begin and automatically stopping after a defined period of silence (`1.5` seconds by default).
3.  **Local Processing:** The audio array is saved temporarily to `/tmp/voice_input.wav`.
4.  **Cloud Transcription:** The WAV file is uploaded to the Gemini API and processed by the `gemini-1.5-flash` model, which is instructed to output the raw text transcription without conversational filler.
5.  **Output:** The resulting text is copied to the system clipboard, ready to be pasted into any application.

## Development Conventions
*   **Dependency Management:** All dependencies are declared in `pyproject.toml` and locked in `uv.lock`. Use `uv add <package>` to introduce new dependencies.
*   **Model Selection:** The project explicitly uses `gemini-1.5-flash` for transcription as it provides the optimal balance of speed and accuracy for simple audio transcription tasks.
*   **Environment Variables:** While the bash scripts currently contain hardcoded `GOOGLE_API_KEY` exports for local convenience, the underlying Python script `voice_agent.py` respects standard environment variables (`GOOGLE_API_KEY` or `GEMINI_API_KEY`).