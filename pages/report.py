# report.py
import streamlit as st
from datetime import datetime
import base64
import json
from pathlib import Path
import uuid
from streamlit_js_eval import streamlit_js_eval
import streamlit.components.v1 as components
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from blockchain import SimpleBlockchain

# Load authorized API keys
def load_authorized_users():
    try:
        with open("data/authorized_users.json", "r") as f:
            return json.load(f)
    except:
        return {}

AUTHORIZED_USERS = load_authorized_users()

# Blockchain setup
blockchain = SimpleBlockchain("data/blockchain.json")

st.set_page_config(page_title="Report Incident", layout="centered")
st.title("📤 Report a Disaster Incident")

# Unique user ID for the session
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# Geolocation (lat, long)
coords = streamlit_js_eval(
    js_expressions="""
    new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(
            (pos) => resolve({
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude
            }),
            (err) => resolve({ error: err.message })
        );
    })
    """,
    key="get_location"
)

location_default = ""
if coords and "latitude" in coords and "longitude" in coords:
    location_default = f"{coords['latitude']:.5f}, {coords['longitude']:.5f}"
elif coords and "error" in coords:
    st.warning(f"⚠ Location Error: {coords['error']}")
else:
    st.info("📍 Waiting for location permission...")

# ----------- Form -----------
with st.form("incident_form"):
    st.markdown(f"🆔 **User ID:** `{st.session_state.user_id}`")

    api_key = st.text_input("🔐 API Key (if you're a verified authority)", type="password")
    username = st.text_input("👤 Your Name", placeholder="Eg: NDMA")
    disaster_type = st.selectbox("🌪 Type of Disaster", ["Flood", "Fire", "Landslide", "Other"])
    location = st.text_input("📍 Location", value=location_default)
    description = st.text_area("📝 Description")
    photo = st.file_uploader("📷 Upload Photo", type=["jpg", "jpeg", "png"])

    # Voice Recorder (only playback)
    st.markdown("🎙️ **Instant Voice Recorder (Browser playback only)**")
    components.html("""
    <script>
      let mediaRecorder;
      let audioChunks = [];

      document.addEventListener("DOMContentLoaded", function() {
        const recordBtn = document.createElement("button");
        recordBtn.innerText = "🎤 Start Recording";
        document.body.appendChild(recordBtn);

        const stopBtn = document.createElement("button");
        stopBtn.innerText = "⏹️ Stop";
        stopBtn.disabled = true;
        document.body.appendChild(stopBtn);

        const player = document.createElement("audio");
        player.controls = true;
        document.body.appendChild(player);

        recordBtn.onclick = async () => {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaRecorder = new MediaRecorder(stream);
          audioChunks = [];

          mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) audioChunks.push(e.data);
          };

          mediaRecorder.onstop = () => {
            const blob = new Blob(audioChunks);
            player.src = URL.createObjectURL(blob);
          };

          mediaRecorder.start();
          recordBtn.disabled = true;
          stopBtn.disabled = false;
        };

        stopBtn.onclick = () => {
          mediaRecorder.stop();
          recordBtn.disabled = false;
          stopBtn.disabled = true;
        };
      });
    </script>
    """, height=300)

    submit = st.form_submit_button("📤 Submit Report")

# ----------- On Submit -----------
if submit:
    verified = api_key in AUTHORIZED_USERS
    submitted_by = AUTHORIZED_USERS.get(api_key, "Public User")

    photo_data = base64.b64encode(photo.read()).decode() if photo else None
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_data = {
        "user_id": st.session_state.user_id,
        "username": username,
        "submitted_by": submitted_by,
        "verified": verified,
        "api_key_used": api_key if verified else None,
        "disaster_type": disaster_type,
        "location": location,
        "description": description,
        "timestamp": timestamp,
        "photo_base64": photo_data,
        "status": "verified" if verified else "pending"
    }

    last_block = blockchain.get_last_block()
    new_block = blockchain.create_block(report_data, last_block["hash"])

    st.success("✅ Report submitted to blockchain successfully!")
    if verified:
        st.info(f"🛡 Verified by: {submitted_by}")
    else:
        st.warning("📨 Submitted by Public User (Unverified)")
    
    st.write(f"🧾 Block Index: `{new_block['index']}`")
    st.write(f"⛓️ Block Hash: `{new_block['hash'][:10]}...`")
    st.write(f"🕒 Timestamp: `{new_block['timestamp']}`")

# ----------- View Chain -----------
if st.checkbox("📚 View Blockchain"):
    for block in blockchain.get_chain():
        st.json(block)
