from gtts import gTTS
import streamlit as st
import os

st.set_page_config(page_title="Voice Alerts")
st.title("🔊 Voice Alerts")

language = st.selectbox("🌐 Select Language", ["English", "Hindi", "Malayalam"])

alerts = {
    "English": "Warning: Heavy rainfall expected. Please move to a safer place.",
    "Hindi": "चेतावनी: भारी वर्षा की संभावना है। कृपया ऊँचाई वाले क्षेत्र में जाएं।",
    "Malayalam": "മുന്നറിയിപ്പ്: ശക്തമായ മഴ പ്രതീക്ഷിക്കുന്നു. ദയവായി സുരക്ഷിതമായ സ്ഥലത്തേക്ക് നീങ്ങുക."
}

text = alerts[language]
lang_code = {"English": "en", "Hindi": "hi", "Malayalam": "ml"}[language]

if st.button("📣 Play Alert"):
    tts = gTTS(text=text, lang=lang_code)
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as f:
        st.audio(f.read(), format="audio/mp3")
    os.remove("temp.mp3")
