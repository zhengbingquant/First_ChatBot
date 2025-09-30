import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
import os
from gtts import gTTS
import base64
import time

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="Physics & Maths Solver", page_icon="🤖", layout="wide")

# Google API key (use st.secrets for security)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Initialize model
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("Adjust chatbot options below.")
    st.markdown("---")

    # File uploader toggle
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

    if st.session_state.show_uploader:
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded image", use_column_width=True)

# ---------------------------
# CHAT HISTORY
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------
# BOTTOM BAR: 📎 + 🔊 + Input
# ---------------------------
with st.container():
    col1, col2, col3 = st.columns([0.07, 0.07, 0.86])

    with col1:
        if st.button("📎", help="Upload image"):
            st.session_state.show_uploader = not st.session_state.show_uploader
            st.rerun()

    with col2:
        enable_tts = st.checkbox("🔊", value=True, key="tts_toggle", help="Enable text-to-speech")

    with col3:
        prompt = st.chat_input("Ask me a physics or maths question...")

# ---------------------------
# HANDLE PROMPT
# ---------------------------
if prompt:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Gemini API
    response = model.generate_content(prompt)
    reply = response.text

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

        # Text-to-Speech
        if enable_tts:
            tts = gTTS(reply)
            tts.save("reply.mp3")
            audio_file = open("reply.mp3", "rb")
            audio_bytes = audio_file.read()
            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
            st.markdown(
                f'<audio autoplay="true" controls><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>',
                unsafe_allow_html=True,
            )
