from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_severity_and_type(text):
    prompt = f"""
You are a disaster alert classification assistant.

Classify the following disaster report into these fields **strictly**:

1. Severity: Low, Medium, or High  
2. Status: Choose only one of:
   - ACTIVE: The disaster is currently happening or needs attention  
   - RESOLVED: The disaster has been dealt with or recovery is underway  
   - EXPIRED: The event is outdated or no longer relevant  
   - IGNORED: The report is irrelevant, spam, or clearly false  
3. Disaster Type: e.g., Flood, Earthquake, Fire, etc.  
4. Explanation: Give detailed reasoning for each classification.

**IMPORTANT: Follow this exact output format**  

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

    # Initialize variables
    disaster_type = ""
    severity = ""
    status = ""
    explanation_lines = []

    for line in response_text.splitlines():
        if line.startswith("Severity:"):
            severity = line.replace("Severity:", "").strip()
        elif line.startswith("Status:"):
            status = line.replace("Status:", "").strip()
        elif line.startswith("Disaster Type:"):
            disaster_type = line.replace("Disaster Type:", "").strip()
        elif line.startswith("Explanation:"):
            explanation_lines.append(line.replace("Explanation:", "").strip())
        elif explanation_lines:
            explanation_lines.append(line.strip())

    explanation = "\n".join(explanation_lines)

    return disaster_type, severity, status, explanation
