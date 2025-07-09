import json
from datetime import datetime

def format_alert_report(text, severity, explanation):
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "report_text": text,
        "severity": severity,
        "explanation": explanation,
        "status": "ACTIVE",
        "source": "Groq LLM",
    }
    return report

