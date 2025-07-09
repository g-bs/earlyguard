import streamlit as st
import json
import base64
from pathlib import Path

# ---------------------
# Page Setup
# ---------------------
st.set_page_config(page_title="Community Feed", layout="wide")
st.title("📋 Community Feed")
st.markdown("Browse disaster incident reports submitted by community members.")

# ---------------------
# Load Reports
# ---------------------
data_path = Path("data/reports.json")

if not data_path.exists() or data_path.stat().st_size == 0:
    st.warning("No community reports found yet.")
else:
    with open(data_path, "r") as f:
        try:
            reports = json.load(f)
        except json.JSONDecodeError:
            st.error("Error reading reports. Please check file format.")
            reports = []

    # Reverse to show newest first
    for report in reversed(reports):
        st.markdown("---")
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"**🧍 {report['username']}**  reported a **{report['disaster_type']}**")
                st.markdown(f"📍 **Location**: {report['location']}")
                st.markdown(f"🕒 **Time**: {report['timestamp']}")
                st.markdown(f"📝 **Description**: {report['description']}")
                st.markdown(f"🆔 Report ID: `{report['report_id']}`")

            with col2:
                if report.get("photo_base64"):
                    try:
                        img_data = base64.b64decode(report["photo_base64"])
                        st.image(img_data, caption="Attached Photo", use_column_width=True)
                    except:
                        st.error("📷 Image could not be displayed.")
