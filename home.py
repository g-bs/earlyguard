import streamlit as st
from datetime import datetime

# ----------------------
# Mock live alerts data
# ----------------------
alerts = [
    {
        "type": "Flood Warning",
        "severity": "Severe",
        "location": "Alappuzha",
        "time": datetime.now().strftime("%I:%M %p"),
        "color": "red"
    },
    {
        "type": "Heavy Rain Alert",
        "severity": "Moderate",
        "location": "Wayanad",
        "time": datetime.now().strftime("%I:%M %p"),
        "color": "orange"
    },
    {
        "type": "Landslide Risk",
        "severity": "Mild",
        "location": "Idukki",
        "time": datetime.now().strftime("%I:%M %p"),
        "color": "green"
    }
]

# ----------------------
# Page Setup
# ----------------------
st.set_page_config(page_title="Early Guard++", layout="wide")

# ----------------------
# Header
# ----------------------
st.title("🛡️ Early Guard++")
st.subheader("Community-Driven Disaster Early Warning System")

st.markdown("---")

# ----------------------
# Live Alerts Section
# ----------------------
st.header("🚨 Live Alerts")

for alert in alerts:
    with st.container():
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
                <small>{alert['severity']} | {alert['location']} | {alert['time']}</small>
            </div>
            """,
            unsafe_allow_html=True
        )

# ----------------------
# Quick Actions
# ----------------------
st.markdown("---")
st.subheader("🧭 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📤 Report Incident"):
        st.info("Navigate to the Report Incident page (TODO: Add routing logic or sidebar link).")




with col2:
    if st.button("📋 Community Feed"):
        st.info("Community activity feed under development.")

# ----------------------
# Footer
# ----------------------
st.markdown("---")
st.caption("Made with ❤️ for Infosys Global Hackathon 2025")

