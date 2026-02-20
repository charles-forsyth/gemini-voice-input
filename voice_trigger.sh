#!/bin/bash

# Configuration
PROJECT_DIR="$HOME/Projects/gemini-voice-input"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
SCRIPT="$PROJECT_DIR/voice_agent.py"

# Export the API key explicitly

# Safety Check: Kill any already-running instances of the python script
if pgrep -f "$SCRIPT" > /dev/null; then
    pkill -f "$SCRIPT"
    notify-send -t 2000 -i audio-input-microphone "Gemini Voice" "Previous recording aborted. Starting fresh."
    sleep 0.5
fi

# Notify user we are listening
notify-send -t 2000 -i audio-input-microphone "Gemini Voice" "Listening... Speak now."

# Run the python script and capture output to log for debugging.
# If it exits with 0 (success), show the final notification.
if $PYTHON_BIN $SCRIPT > /tmp/gemini_voice.log 2>&1; then
    # Notify ready
    notify-send -t 3000 -i edit-paste "Gemini Voice" "Transcription ready!\nPress Ctrl+V to paste."
else
    # It failed or was killed. Do not show the ready notification.
    # We can check if it was due to missing API key specifically:
    if grep -q "Error: Could not determine project ID" /tmp/gemini_voice.log; then
        notify-send -t 4000 -i dialog-error "Gemini Voice Error" "API Key missing."
    else
        notify-send -t 4000 -i dialog-error "Gemini Voice Error" "Transcription or clipboard copy failed. Check /tmp/gemini_voice.log for details."
    fi
fi
