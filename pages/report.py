import streamlit as st
from datetime import datetime
import base64
import uuid
import json
from pathlib import Path
import streamlit.components.v1 as components

st.set_page_config(page_title="Report Incident", layout="centered")
st.title("📤 Report a Disaster Incident")

# -------------- Incident Form --------------
with st.form("incident_form"):
    username = st.text_input("👤 Your Name", placeholder="Eg: Anjali")
    disaster_type = st.selectbox("🔸 Type of Disaster", ["Flood", "Fire", "Landslide", "Other"])
    location = st.text_input("📍 Location", placeholder="Eg: Kuttanad")
    description = st.text_area("📝 Description")
    photo = st.file_uploader("📷 Upload Photo", type=["jpg", "jpeg", "png"])

    # 🎙️ Voice Recorder (inline)
    st.markdown("🎙️ **Instant Voice Recorder** (No download, just record and listen)")

    voice_recorder_html = """
    <!DOCTYPE html>
    <html>
      <body>
        <button id="record">🎤 Start Recording</button>
        <button id="stop" disabled>⏹️ Stop</button>
        <br><br>
        <audio id="player" controls></audio>

        <script>
          let mediaRecorder;
          let audioChunks = [];

          document.getElementById("record").onclick = async () => {
            audioChunks = [];
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = event => {
              if (event.data.size > 0) audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
              const blob = new Blob(audioChunks);
              const url = URL.createObjectURL(blob);
              const audio = document.getElementById("player");
              audio.src = url;
            };

            mediaRecorder.start();
            document.getElementById("record").disabled = true;
            document.getElementById("stop").disabled = false;
          };

          document.getElementById("stop").onclick = () => {
            mediaRecorder.stop();
            document.getElementById("record").disabled = false;
            document.getElementById("stop").disabled = true;
          };
        </script>
      </body>
    </html>
    """

    components.html(voice_recorder_html, height=300)

    submit = st.form_submit_button("📤 Submit Report")

# -------------- Form Submission --------------
if submit:
    # Step 1: Generate metadata
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_id = str(uuid.uuid4())
    photo_data = base64.b64encode(photo.read()).decode() if photo else None

    # Step 2: Create report object
    report = {
        "report_id": report_id,
        "username": username,
        "disaster_type": disaster_type,
        "location": location,
        "description": description,
        "timestamp": timestamp,
        "photo_base64": photo_data,
        "status": "pending"
        # NOTE: Voice is not stored yet, only played in-browser
    }

    # Step 3: Save to reports.json
    report_file = Path("data/reports.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    if report_file.exists() and report_file.stat().st_size > 0:
        with open(report_file, "r") as f:
            try:
                reports = json.load(f)
            except json.JSONDecodeError:
                reports = []
    else:
        reports = []

    reports.append(report)

    with open(report_file, "w") as f:
        json.dump(reports, f, indent=4)

    # Step 4: Confirmation
    st.success(f"✅ Report submitted successfully! Your Report ID is `{report_id}`")
    st.balloons()
    st.json(report)
