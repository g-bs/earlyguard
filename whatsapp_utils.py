import os
import json
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from math import radians, sin, cos, sqrt, atan2

# Load environment variables
load_dotenv()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
whatsapp_sender = "whatsapp:+14155238886"  # Twilio sandbox sender number

client = Client(account_sid, auth_token)

# ---------- Distance Helper ----------
def parse_location(loc_str):
    try:
        parts = loc_str.replace("Lat:", "").replace("Lon:", "").split(",")
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        return lat, lon
    except Exception:
        return None, None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# ---------- WhatsApp Send Logic ----------
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

# ---------- Broadcast WhatsApp Alerts ----------
def broadcast_alert_whatsapp(report, radius_km=5):
    print("🚨 Broadcasting WhatsApp alert to nearby subscribers...")

    try:
        with open("subscribers.json", "r") as f:
            subscribers = json.load(f)
    except FileNotFoundError:
        print("❌ subscribers.json file not found.")
        return []

    # Extract report location
    report_lat, report_lon = parse_location(report["location"])
    if None in (report_lat, report_lon):
        print("❌ Invalid report location.")
        return []

    # Format timestamp
    try:
        dt = datetime.fromisoformat(report["timestamp"].replace("Z", "+00:00"))
        time_str = dt.strftime("%B %d, %I:%M %p UTC")
    except Exception:
        time_str = report["timestamp"]

    # Construct message
    base_message = (
        f"🚨 URGENT: {report['severity']}-severity {report['disaster_type']} reported!\n"
        f"📍 Location: {report['location']}\n"
        f"🕒 Time: {time_str}\n"
        f"📝 Summary: {report['report_text']}\n"
    )
    if report.get("explanation"):
        base_message += f"📌 Additional Info: {report['explanation']}\n"
    base_message += "\nPlease stay alert and follow safety instructions."

    results = []
    for user in subscribers:
        name = user.get("name", "User")
        phone = user.get("phone", "").strip()
        user_lat, user_lon = parse_location(user.get("location", ""))

        if None in (user_lat, user_lon):
            print(f"⚠️ Skipping user {name} due to invalid location.")
            continue

        # Check distance
        distance = haversine(report_lat, report_lon, user_lat, user_lon)
        if distance > radius_km:
            print(f"ℹ️ Skipping {name} (outside {radius_km} km): {distance:.2f} km away.")
            continue

        # Format and send
        if not phone.startswith("+"):
            phone = "+" + phone
        full_whatsapp_number = f"whatsapp:{phone}"
        personalized_msg = f"Hi {name},\n{base_message}"
        result = send_whatsapp(full_whatsapp_number, personalized_msg)
        results.append(result)

    return results
