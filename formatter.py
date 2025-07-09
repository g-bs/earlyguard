from datetime import datetime

'''def format_alert_report(text, disaster_type, severity, explanation):
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "report_text": text,
        "disaster_type": disaster_type,
        "severity": severity,
        "explanation": explanation,
        "location": location, 
        "status": "ACTIVE",
        "source": "Groq LLM",
    }
    return report'''
from datetime import datetime

def format_alert_report(text, disaster_type, severity, status, explanation,location):
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "report_text": text,
        "disaster_type": disaster_type,
        "severity": severity,
        "status": status,
        "explanation": explanation,
        "location": location, 
        "source": "Groq LLM",
    }
    return report

