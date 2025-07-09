from fastapi import FastAPI
from pydantic import BaseModel
from formatter import format_alert_report
from report_classify import classify_severity_and_type

app = FastAPI()

class ReportInput(BaseModel):
    text: str
    location: str 

@app.post("/classify")
def classify_disaster(report: ReportInput):
    disaster_type, severity, status, explanation = classify_severity_and_type(report.text)

    # Status needs to be parsed too — modify your classify function to return it
    # e.g., return disaster_type, severity, status, explanation
    report_json = format_alert_report(
        text=report.text,
        disaster_type=disaster_type,
        severity=severity,
        status=status,
        explanation=explanation,
        location=report.location
    )
    return report_json


