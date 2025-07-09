# voice_handler.py

import os
import base64
import whisper

# Load Whisper model only once
model_whisper = whisper.load_model("base")

'''def transcribe_voice(file_name: str, base64_data: str) -> str:
    """
    Transcribe voice input (Base64 encoded) using OpenAI Whisper.
    """
    os.makedirs("temp_audio", exist_ok=True)
    audio_path = os.path.join("temp_audio", file_name)

    # Decode and save audio
    with open(audio_path, "wb") as f:
        f.write(base64.b64decode(base64_data.split(",")[-1]))

    # Transcribe with Whisper
    result = model_whisper.transcribe(audio_path)
    return result["text"]'''
def transcribe_voice(file_name: str, base64_data: str, language: str = None) -> str:
    """
    Transcribe voice input (Base64 encoded) using OpenAI Whisper.
    Automatically translates to English if needed.
    Optional: You can pass a language code (e.g., 'hi' for Hindi).
    """
    os.makedirs("temp_audio", exist_ok=True)
    audio_path = os.path.join("temp_audio", file_name)

    # Decode and save audio
    with open(audio_path, "wb") as f:
        f.write(base64.b64decode(base64_data.split(",")[-1]))

    # Prepare transcription options
    options = {"fp16": False, "task": "translate"}
    if language:
        options["language"] = language  # Optional override

    result = model_whisper.transcribe(audio_path, **options)
    return result["text"]
