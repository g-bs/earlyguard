from fastapi import FastAPI
from pydantic import BaseModel
from formatter import format_alert_report
from report_classify import classify_severity

app = FastAPI()

class ReportInput(BaseModel):
    text: str

@app.post("/classify")
def classify_disaster(report: ReportInput):
    # Run classification + explanation using your existing module
    severity, explanation = classify_severity(report.text)
    
    # Format the report as JSON using your formatter
    report_json = format_alert_report(
        text=report.text,
        severity=severity,
        explanation=explanation
    )
    
    return report_json
