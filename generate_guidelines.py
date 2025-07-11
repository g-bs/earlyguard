# generate_guidelines.py

from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GUIDELINE_FILE = "guideline_store.json"

if os.path.exists(GUIDELINE_FILE):
    with open(GUIDELINE_FILE, "r") as f:
        guideline_store = json.load(f)
else:
    guideline_store = {}

def generate_guidelines(disaster_type, location=None, description=None):
    disaster_type = disaster_type.lower()

    if disaster_type in guideline_store:
        return guideline_store[disaster_type]

    # Include extra context if provided
    context = f"Disaster: {disaster_type}"
    if location or description:
        context += f"\nLocation: {location}\nReport: {description}"

    prompt = f"""
You are a disaster safety expert.

Give 2 short safety tips for this situation:

{context}

Format:
DURING: <tip>.
AFTER: <tip>.
"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result = response.choices[0].message.content.strip()
    tips = {"raw": result}

    # Store to file
    guideline_store[disaster_type] = tips
    with open(GUIDELINE_FILE, "w") as f:
        json.dump(guideline_store, f, indent=2)

    return tips
