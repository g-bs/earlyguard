'''from groq import Groq
import os
from formatter import format_alert_report
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Access the key
api_key = os.getenv("GROQ_API_KEY")

# Use with Groq client
client = Groq(api_key=api_key)

def classify_severity(text):
    prompt = f"""
Classify the severity of the following disaster report into one of: Low, Medium, or High.

Report: "{text}"

Severity:
"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",  # or mixtral, gemma, etc.
        messages=[{"role": "user", "content": prompt}],
        temperature=0  # Deterministic output
    )

    return response.choices[0].message.content.strip()

# Example usage
#print(classify_severity("Floods have washed away several homes and roads are blocked."))
llm_response = classify_severity("Floods have washed away several homes and roads are blocked.")
first_line, *rest = llm_response.strip().split("\n", 1)
severity = first_line.strip().split()[-1].replace(".", "")
explanation = rest[0].strip() if rest else "No explanation provided."

json_report = format_alert_report(
    text="Floods have washed away several homes and roads are blocked.",
    severity=severity,
    explanation=explanation
)

print(json_report)'''
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

Return format:
Severity: <Low|Medium|High>
Explanation: <reason>
"""
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    response_text = response.choices[0].message.content.strip()

    # Parse the response
    severity_line = next((line for line in response_text.splitlines() if line.startswith("Severity:")), "")
    explanation_line = "\n".join([line for line in response_text.splitlines() if not line.startswith("Severity:")])

    severity = severity_line.replace("Severity:", "").strip()
    explanation = explanation_line.replace("Explanation:", "").strip()

    return severity, explanation


