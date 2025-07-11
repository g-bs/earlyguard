from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_severity(text):
    prompt = f"""
Classify the severity of the following disaster report into one of: Low, Medium, or High.
Also explain the reasoning.

Report: "{text}"

Return in this format:
Severity: <Low|Medium|High>  
Status: <ACTIVE|RESOLVED|EXPIRED|IGNORED>  
Disaster Type: <Type>  
Explanation: <reason>
"""
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    response_text = response.choices[0].message.content.strip()

    # Parse fields
    disaster_type = severity = status = ""
    explanation_lines = []
    for line in response_text.splitlines():
        if line.startswith("Severity:"):
            severity = line.split(":", 1)[1].strip()
        elif line.startswith("Status:"):
            status = line.split(":", 1)[1].strip()
        elif line.startswith("Disaster Type:"):
            disaster_type = line.split(":", 1)[1].strip()
        elif line.startswith("Explanation:"):
            explanation_lines.append(line.split(":", 1)[1].strip())
        elif explanation_lines:
            explanation_lines.append(line.strip())

    explanation = "\n".join(explanation_lines)
    return disaster_type, severity, status, explanation
