import whisper
model = whisper.load_model("base")
result = model.transcribe("test_disaster_report.mp3")
print(result["text"])
