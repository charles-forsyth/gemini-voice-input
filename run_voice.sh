#!/bin/bash
cd /home/chuck/Projects/gemini-voice-input
export GOOGLE_API_KEY="AIzaSyDeweMLbYtvDpY2ALHloOgWkmhfC0vA_Ig"

# Log output so we can see what failed
/home/chuck/.local/bin/uv run python voice_agent.py > /tmp/voice_debug.log 2>&1
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || true
else
    # Play error sound
    paplay /usr/share/sounds/freedesktop/stereo/dialog-error.oga 2>/dev/null || true
fi
