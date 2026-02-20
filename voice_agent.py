import sys
import wave
import numpy as np
import sounddevice as sd
import subprocess
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
import google.auth

# Configuration
THRESHOLD = 0.015  # Silence threshold (RMS amplitude) - Lowered for sensitivity
SILENCE_LIMIT = 1.5  # Seconds of silence before stopping
MAX_WAIT_TIME = 10.0  # Maximum seconds to wait for speech to start
SAMPLE_RATE = 16000
CHANNELS = 1
TEMP_WAV = "/tmp/voice_input.wav"


def record_until_silence():
    print("🎙️ Listening... (Speak now)", file=sys.stderr)
    q = []
    silent_chunks = 0
    chunk_size = int(SAMPLE_RATE * 0.1)  # 100ms chunks
    silence_chunks_limit = int(SILENCE_LIMIT / 0.1)
    max_wait_chunks = int(MAX_WAIT_TIME / 0.1)
    waited_chunks = 0

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

                waited_chunks += 1
                if waited_chunks > max_wait_chunks:
                    print("⏱️ Timed out waiting for speech.", file=sys.stderr)
                    sys.exit(0)

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

    print("⏳ Processing audio with Google Cloud Speech (Chirp 3)...", file=sys.stderr)
    audio_data = np.concatenate(q, axis=0)
    audio_data_int16 = np.int16(audio_data * 32767)

    with wave.open(TEMP_WAV, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_data_int16.tobytes())


def transcribe_audio():
    try:
        credentials, project_id = google.auth.default()
    except Exception:
        print(
            "Error: Could not load Application Default Credentials. Run 'gcloud auth application-default login'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not project_id:
        print(
            "Error: Could not determine project ID from Application Default Credentials. Set GOOGLE_CLOUD_PROJECT.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Chirp model requires a regional endpoint
    client = SpeechClient(
        client_options={"api_endpoint": "us-central1-speech.googleapis.com"}
    )

    with open(TEMP_WAV, "rb") as f:
        audio_content = f.read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="chirp",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{project_id}/locations/us-central1/recognizers/_",
        config=config,
        content=audio_content,
    )

    try:
        response = client.recognize(request=request)
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "
        return transcript.strip()
    except Exception as e:
        print(f"Transcription failed: {e}", file=sys.stderr)
        sys.exit(1)


def copy_to_clipboard(text):
    try:
        subprocess.run(["wl-copy"], input=text.encode("utf-8"), check=True)
        print("📋 Copied to clipboard!", file=sys.stderr)
    except Exception:
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
            sys.exit(1)


if __name__ == "__main__":
    record_until_silence()
    text = transcribe_audio()
    if text:
        print(f"\n[Transcribed]: {text}\n")
        copy_to_clipboard(text)
