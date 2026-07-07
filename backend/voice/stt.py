import tempfile
import os
import numpy as np

def transcribe_audio(audio_bytes: bytes, format: str = "webm") -> str:
    """Convert audio bytes to text using Whisper."""
    import whisper

    model = whisper.load_model("base")  # base is fast enough, good accuracy

    # Save to temp file
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=f".{format}"
    ) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path, language="en")
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    # Test with a real audio file
    with open("voice/test_audio.mp3", "rb") as f:
        audio = f.read()
    text = transcribe_audio(audio, format="mp3")
    print(f"Transcribed: {text}")