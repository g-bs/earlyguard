import streamlit as st
import json
import uuid
from pathlib import Path
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Join Alert Network", layout="centered")
st.title("📡 Join the Community Alert Network")

# JS: Get current location
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
    key="join_location"
)

location_default = ""
if coords and "latitude" in coords and "longitude" in coords:
    location_default = f"{coords['latitude']:.5f}, {coords['longitude']:.5f}"
elif coords and "error" in coords:
    st.warning(f"⚠ Location Error: {coords['error']}")
else:
    st.info("📍 Waiting for location permission...")

# --- Join Button ---
if "show_form" not in st.session_state:
    st.session_state.show_form = False

if not st.session_state.show_form:
    if st.button("🚀 Join Network"):
        st.session_state.show_form = True
else:
    with st.form("join_form"):
        name = st.text_input("👤 Full Name")
        phone = st.text_input("📱 Phone Number")
        role = st.selectbox("🎭 Your Role", ["Citizen", "Authority"])
        location = st.text_input("📍 Your Location (Lat, Long)", value=location_default)

        submit = st.form_submit_button("✅ Submit")

    if submit:
        # Prepare new entry
        entry = {
            "id": str(uuid.uuid4()),
            "name": name,
            "phone": phone,
            "role": role,
            "location": location
        }

        # Save to file
        file_path = Path("data/subscribers.json")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    members = json.load(f)
            except:
                members = []
        else:
            members = []

        members.append(entry)

        with open(file_path, "w") as f:
            json.dump(members, f, indent=4)

        st.success("🎉 You're now part of the community alert network!")
        st.balloons()
        st.session_state.show_form = False
