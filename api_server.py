# api_server.py
from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
from formatter import format_alert_report
from report_classify import classify_severity_and_type
from voice_handler import transcribe_voice

app = FastAPI()

class VoiceNote(BaseModel):
    file_name: str
    file_type: str
    base64_data: str

class ReportInput(BaseModel):
    text: Optional[str] = None
    location: str
    voice_note: Optional[VoiceNote] = None

'''@app.post("/classify")
def classify_disaster(report: ReportInput):
    # If text not given, transcribe from voice
    if not report.text and report.voice_note:
        report.text = transcribe_voice(
            file_name=report.voice_note.file_name,
            base64_data=report.voice_note.base64_data
        )

    if not report.text:
        return {"error": "No report text or voice note provided."}

    disaster_type, severity, status, explanation = classify_severity_and_type(report.text)

    report_json = format_alert_report(
        text=report.text,
        disaster_type=disaster_type,
        severity=severity,
        status=status,
        explanation=explanation,
        location=report.location
    )
    return report_json'''
@app.post("/classify")
def classify_disaster(report: ReportInput):
    # Fallback: Use voice transcription if no text provided
    if not report.text:
        if report.voice_note:
            report_text = transcribe_voice(
                report.voice_note.file_name,
                report.voice_note.base64_data
            )
        else:
            return {"error": "No report text or voice note provided."}
    else:
        report_text = report.text

    # Run classification
    disaster_type, severity, status, explanation = classify_severity_and_type(report_text)

    report_json = format_alert_report(
        text=report_text,
        disaster_type=disaster_type,
        severity=severity,
        status=status,
        explanation=explanation,
        location=report.location
    )
    return report_json
