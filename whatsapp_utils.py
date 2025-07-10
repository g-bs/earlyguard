import os
import json
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
whatsapp_sender = "whatsapp:+14155238886"  # Twilio sandbox sender number

client = Client(account_sid, auth_token)

def send_whatsapp(to, message):
    print(f"📤 Attempting to send WhatsApp message to {to}...")
    try:
        msg = client.messages.create(
            body=message,
            from_=whatsapp_sender,
            to=to
        )
        print(f"✅ Sent to {to} | SID: {msg.sid}")
        return {"to": to, "status": "sent", "sid": msg.sid}
    except Exception as e:
        print(f"❌ Failed to send to {to} | Error: {str(e)}")
        return {"to": to, "status": "failed", "error": str(e)}

def broadcast_alert_whatsapp(report):
    print("🚨 Broadcasting WhatsApp alert to all subscribers...")
    
    # Load subscribers
    try:
        with open("subscribers.json", "r") as f:
            subscribers = json.load(f)
    except FileNotFoundError:
        print("❌ subscribers.json file not found.")
        return []

    # Format timestamp
    try:
        dt = datetime.fromisoformat(report["timestamp"].replace("Z", "+00:00"))
        time_str = dt.strftime("%B %d, %I:%M %p UTC")
    except Exception:
        time_str = report["timestamp"]

    # Construct message
    message = (
        f"🚨 URGENT: {report['severity']}-severity {report['disaster_type']} reported!\n"
        f"📍 Location: {report['location']}\n"
        f"🕒 Time: {time_str}\n"
        f"📝 Summary: {report['report_text']}\n"
    )
    if report.get("explanation"):
        message += f"📌 Additional Info: {report['explanation']}\n"

    message += "\nPlease stay alert and follow safety instructions."

    # Send to all subscribers
    results = []
    for user in subscribers:
        name = user.get("name", "User")
        phone = user.get("phone", "").strip()

        # ✅ Normalize phone number (add '+' if missing)
        if not phone.startswith("+"):
            phone = "+" + phone

        full_whatsapp_number = f"whatsapp:{phone}"
        personalized_msg = f"Hi {name},\n{message}"
        result = send_whatsapp(full_whatsapp_number, personalized_msg)
        results.append(result)

    return results
