import streamlit as st
import json
from blockchain import SimpleBlockchain
from pathlib import Path

# Load the blockchain
blockchain = SimpleBlockchain("data/blockchain.json")
chain = blockchain.get_chain()

st.set_page_config(page_title="Community Feed", layout="centered")
st.title("🌐 Community Disaster Reports")

# ----------------------
# Session State for Votes
# ----------------------
if "upvotes" not in st.session_state:
    st.session_state.upvotes = {}

if "downvotes" not in st.session_state:
    st.session_state.downvotes = {}

# ----------------------
# Display Reports
# ----------------------
for block in reversed(chain[1:]):  # Skip genesis block
    report = block["data"]
    report_id = block["hash"][:10]  # Use hash prefix as unique ID

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
            st.image(
                f"data:image/jpeg;base64,{report['photo_base64']}",
                caption="📷 Submitted Photo",
                use_column_width=True
            )

        # If not verified, allow voting
        if not report.get("verified"):
            upvotes = st.session_state.upvotes.get(report_id, 0)
            downvotes = st.session_state.downvotes.get(report_id, 0)

            col_up, col_down = st.columns(2)

            with col_up:
                if st.button(f"👍 Upvote ({upvotes})", key=f"up_{report_id}"):
                    st.session_state.upvotes[report_id] = upvotes + 1

            with col_down:
                if st.button(f"👎 Downvote ({downvotes})", key=f"down_{report_id}"):
                    st.session_state.downvotes[report_id] = downvotes + 1

        st.markdown("---")
