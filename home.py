# home.py
import streamlit as st
from datetime import datetime
import json
from pathlib import Path

# ----------------------
# Page Setup
# ----------------------
st.set_page_config(page_title="Early Guard++", layout="wide")

<<<<<<< HEAD
st.title("🛡 Early Guard++")
=======
st.title("🛡️ Early Guard++")
>>>>>>> 099791d9828762437cecde5a9ab595cc8790c8b6
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
<<<<<<< HEAD
    # Show sample alerts when blockchain.json doesn't exist
    st.info("📋 No blockchain data found. Showing sample alerts for demonstration.")
    alerts = [
        {
            "type": "Flood Warning",
            "severity": "High",
            "status": "Active",
            "location": "Alappuzha, Kerala",
            "time": "2025-07-11 16:30:00",
            "color": "red"
        },
        {
            "type": "Heavy Rain Alert",
            "severity": "Medium",
            "status": "Monitoring",
            "location": "Wayanad, Kerala",
            "time": "2025-07-11 15:45:00",
            "color": "orange"
        },
        {
            "type": "Landslide Risk",
            "severity": "Low",
            "status": "Watch",
            "location": "Idukki, Kerala",
            "time": "2025-07-11 14:20:00",
            "color": "green"
        },
        {
            "type": "Fire Warning",
            "severity": "High",
            "status": "Active",
            "location": "Thiruvananthapuram, Kerala",
            "time": "2025-07-11 13:15:00",
            "color": "red"
        }
    ]
=======
    st.warning("⚠ No alerts found. Submit an incident to see live updates.")
>>>>>>> 099791d9828762437cecde5a9ab595cc8790c8b6

# ----------------------
# Live Alerts Section
# ----------------------
st.header("🚨 Live Alerts")

if alerts:
<<<<<<< HEAD
    for i, alert in enumerate(alerts):
        # Create columns for alert content and button
        col1, col2 = st.columns([4, 1])
        
        with col1:
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
        
        with col2:
            # View Map button for each alert
            if st.button(f"📍 View Map", key=f"map_btn_{i}"):
                # Store alert data in session state
                st.session_state.focus_location = alert['location']
                st.session_state.focus_type = alert['type']
                st.session_state.focus_severity = alert['severity']
                st.session_state.focus_status = alert['status']
                st.session_state.focus_time = alert['time']
                
                # Set a default confidence score (you can modify this based on your logic)
                st.session_state.focus_confidence = 80 if alert['severity'] == 'High' else 60 if alert['severity'] == 'Medium' else 40
                
                # Navigate to Map page
                st.switch_page("pages/Map.py")
else:
    st.info("No active disaster alerts at the moment.")
=======
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
>>>>>>> 099791d9828762437cecde5a9ab595cc8790c8b6

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
<<<<<<< HEAD
st.caption("Made with ❤ for Infosys Global Hackathon 2025")
=======
st.caption("Made with ❤️ for Infosys Global Hackathon 2025")
>>>>>>> 099791d9828762437cecde5a9ab595cc8790c8b6
