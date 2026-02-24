import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz 
import time
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP (KEYS INTEGRATED) =================
GROQ_KEY = "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"
# Bhai, aapki Replicate key yahan paste kar di hai
REPLICATE_TOKEN = "R8_IAbdjeQkoGq2XmgP9VBN11OpmC1qfAw1IVij9"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq API Error!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= PROFESSIONAL UI CSS =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    .block-container {padding-bottom: 120px; padding-top: 1rem;}

    /* Chat Input Padding for Icons */
    div[data-testid="stChatInput"] { padding-left: 95px !important; }

    /* Yellow Plus Icon (Functional) */
    .stFileUploader {
        position: fixed; bottom: 30px; left: 15px;
        width: 40px !important; height: 40px !important; z-index: 2005;
    }
    .stFileUploader section {
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: 2px solid #000 !important; width: 40px !important; height: 40px !important;
    }
    .stFileUploader label, .stFileUploader small { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 24px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 100%;
    }

    /* Mic Button Aligned */
    .mic-wrap { position: fixed; bottom: 25px; left: 62px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 22px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= APP LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🚀 Pro AI")

# Icons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="final_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='final_mic')
st.markdown('</div>', unsafe_allow_html=True)

# Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me or say 'Generate video of...'")

# ================= VIDEO GENERATION FUNCTION =================
def run_video_gen(prompt):
    headers = {
        "Authorization": f"Token {REPLICATE_TOKEN}",
        "Content-Type": "application/json"
    }
    # Using a popular text-to-video model on Replicate
    payload = {
        "version": "da727210-6c9b-4e0e-8c6e-827d0c7f766e", 
        "input": {"prompt": prompt}
    }
    try:
        response = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
        if response.status_code == 201:
            return "✅ Video generation started! Check your Replicate dashboard or wait a moment."
        else:
            return f"❌ Error: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return f"❌ Connection Error: {e}"

# ================= INPUT PROCESSING =================
if u_input:
    # Check if user wants video
    if any(word in u_input.lower() for word in ["video", "generate", "banao"]):
        with st.status("🎬 Summoning AI Video Engine...", expanded=True):
            status_text = run_video_gen(u_input)
            st.write(status_text)

    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        full_res = ""
        box = st.empty()
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": u_input}],
            stream=True
        )
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                box.markdown(full_res + "▌")
        box.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        st.rerun()
        
