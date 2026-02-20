import os
import sys
import wave
import numpy as np
import sounddevice as sd
from google import genai
import subprocess

# Configuration
THRESHOLD = 0.02  # Silence threshold (RMS amplitude)
SILENCE_LIMIT = 1.5  # Seconds of silence before stopping
SAMPLE_RATE = 16000
CHANNELS = 1
TEMP_WAV = "/tmp/voice_input.wav"


def record_until_silence():
    print("🎙️ Listening... (Speak now)", file=sys.stderr)

    q = []
    silent_chunks = 0
    chunk_size = int(SAMPLE_RATE * 0.1)  # 100ms chunks
    silence_chunks_limit = int(SILENCE_LIMIT / 0.1)

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE, channels=CHANNELS, dtype="float32"
        ) as stream:
            # Wait for user to start speaking (skip initial silence)
            while True:
                data, overflowed = stream.read(chunk_size)
                rms = np.sqrt(np.mean(data**2))
                if rms > THRESHOLD:
                    q.append(data)
                    break

            # Record until silence
            while True:
                data, overflowed = stream.read(chunk_size)
                q.append(data)
                rms = np.sqrt(np.mean(data**2))

                if rms < THRESHOLD:
                    silent_chunks += 1
                else:
                    silent_chunks = 0

                if silent_chunks > silence_chunks_limit:
                    break

    except Exception as e:
        print(f"Audio device error: {e}", file=sys.stderr)
        sys.exit(1)

    print("⏳ Processing audio with Gemini...", file=sys.stderr)
    audio_data = np.concatenate(q, axis=0)

    # Convert float32 to int16 for WAV saving
    audio_data_int16 = np.int16(audio_data * 32767)

    with wave.open(TEMP_WAV, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data_int16.tobytes())


def transcribe_audio():
    # Ensure API key is set
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: API Key not found in environment.", file=sys.stderr)
        sys.exit(1)

    # The genai SDK prefers GEMINI_API_KEY
    if not os.environ.get("GEMINI_API_KEY") and api_key:
        os.environ["GEMINI_API_KEY"] = api_key

    client = genai.Client()

    # Use Gemini 3 as requested
    model_id = "gemini-3-pro-preview"

    try:
        audio_file = client.files.upload(file=TEMP_WAV)
        response = client.models.generate_content(
            model=model_id,
            contents=[
                "Transcribe the speech in this audio exactly as spoken. Do not add any conversational filler, markdown formatting, or quotation marks. Just output the raw transcribed text.",
                audio_file,
            ],
        )

        # Clean up
        client.files.delete(name=audio_file.name)

        return response.text.strip()
    except Exception as e:
        print(f"Transcription failed: {e}", file=sys.stderr)
        return ""


def copy_to_clipboard(text):
    try:
        # Use wl-copy for Wayland
        subprocess.run(["wl-copy"], input=text.encode("utf-8"), check=True)
        print("📋 Copied to clipboard!", file=sys.stderr)
    except FileNotFoundError:
        # Fallback to xclip if wl-copy isn't installed
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text.encode("utf-8"),
                check=True,
            )
            print("📋 Copied to clipboard!", file=sys.stderr)
        except Exception:
            print(
                "Could not copy to clipboard. Please install wl-clipboard or xclip.",
                file=sys.stderr,
            )


if __name__ == "__main__":
    record_until_silence()
    text = transcribe_audio()
    if text:
        print(f"\n[Transcribed]: {text}\n")
        copy_to_clipboard(text)
