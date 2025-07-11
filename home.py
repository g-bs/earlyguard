# home.py
import streamlit as st
from datetime import datetime
import json
from pathlib import Path

# ----------------------
# Page Setup
# ----------------------
st.set_page_config(page_title="Early Guard++", layout="wide")

st.title("🛡️ Early Guard++")
st.subheader("Community-Driven Disaster Early Warning System")
st.markdown("---")

# ----------------------
# Load Blockchain Data
# ----------------------
alerts = []
blockchain_path = Path("data/blockchain.json")

if blockchain_path.exists():
    with open(blockchain_path, "r") as f:
        chain = json.load(f)

        for block in reversed(chain):  # Newest first
            data = block.get("data", {})
            severity = data.get("severity", "Unknown")
            alerts.append({
                "type": data.get("disaster_type", "Unknown"),
                "severity": severity,
                "status": data.get("status", "Unknown"),
                "location": data.get("location", "Unknown"),
                "time": data.get("timestamp", "Unknown"),
                "color": {
                    "High": "red",
                    "Medium": "orange",
                    "Low": "green"
                }.get(severity, "gray")
            })
else:
    st.warning("⚠ No alerts found. Submit an incident to see live updates.")

# ----------------------
# Live Alerts Section
# ----------------------
st.header("🚨 Live Alerts")

if alerts:
    for alert in alerts:
        st.markdown(
            f"""
            <div style='
                background-color:{'lightcoral' if alert['color']=='red' else 'gold' if alert['color']=='orange' else "#11d22b"};
                padding:15px; 
                border-left: 5px solid {alert['color']}; 
                border-radius:8px;
                margin-bottom:10px;
            '>
                <strong>{alert['type']}</strong><br>
                <small>
                🔥 <strong>Severity:</strong> {alert['severity']} | 
                📌 <strong>Status:</strong> {alert['status']} | 
                📍 {alert['location']} | 
                🕒 {alert['time']}
                </small>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No active disaster alerts yet.")

# ----------------------
# Quick Actions
# ----------------------
st.markdown("---")
st.subheader("🧭 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link("pages/report.py", label="📤 Report Incident", icon="📝")

with col2:
    st.info("📋 Community Feed (Coming soon...)")

# ----------------------
# Footer
# ----------------------
st.markdown("---")
st.caption("Made with ❤️ for Infosys Global Hackathon 2025")
