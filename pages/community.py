import streamlit as st
import json
from blockchain import SimpleBlockchain
from pathlib import Path

# Load the blockchain
blockchain = SimpleBlockchain("data/blockchain.json")
chain = blockchain.get_chain()

st.set_page_config(page_title="Community Feed", layout="centered")
st.title("🌐 Community Disaster Reports")

# Initialize upvotes in session state
if "upvotes" not in st.session_state:
    st.session_state.upvotes = {}

# Display each block (except Genesis)
for block in reversed(chain[1:]):  # Skip genesis block
    report = block["data"]
    report_id = block["hash"][:10]  # Use hash prefix as ID

    with st.container():
        # Header
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.subheader(f"{report['disaster_type']} at {report['location']}")
        with col2:
            if report.get("verified"):
                st.markdown("🛡️ <span style='color:green'>**Verified**</span> ✔️", unsafe_allow_html=True)

        st.markdown(f"👤 **Reported by**: {report.get('username', 'Unknown')}")
        st.markdown(f"🕒 {report.get('timestamp')}")
        st.markdown(f"📝 {report.get('description') or '_No description provided_'}")

        if report.get("photo_base64"):
            st.image(f"data:image/jpeg;base64,{report['photo_base64']}", caption="📷 Submitted Photo", use_column_width=True)

        # If not verified, allow upvotes
        if not report.get("verified"):
            votes = st.session_state.upvotes.get(report_id, 0)
            if st.button(f"👍 Upvote ({votes})", key=report_id):
                st.session_state.upvotes[report_id] = votes + 1

        st.markdown("---")
