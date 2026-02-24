import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz 
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ API Error!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= FIXED CSS (ALIGNED UI) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    .block-container {padding-bottom: 100px; padding-top: 1rem;}

    /* Input Container Fix */
    div[data-testid="stChatInput"] { 
        padding-left: 95px !important; 
        z-index: 1000;
    }

    /* Fixed Yellow Plus Button - Inside/Beside Input */
    .stFileUploader {
        position: fixed;
        bottom: 30px;
        left: 15px;
        width: 40px !important;
        height: 40px !important;
        z-index: 2005;
    }
    
    .stFileUploader section {
        background-color: #FFD700 !important;
        border-radius: 50% !important;
        border: none !important;
        width: 40px !important;
        height: 40px !important;
        min-height: 40px !important;
    }

    .stFileUploader label, .stFileUploader small, .stFileUploader div[data-testid="stMarkdownContainer"] { display: none !important; }
    .stFileUploader section::before {
        content: '+';
        color: black;
        font-size: 24px;
        font-weight: bold;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }

    /* Mic Button - Perfectly Aligned */
    .mic-wrap {
        position: fixed;
        bottom: 25px;
        left: 62px;
        z-index: 2006;
    }
    
    .mic-wrap button {
        background-color: transparent !important;
        border: none !important;
        font-size: 22px !important;
    }

    .menu-card { background-color: #121212; padding: 15px; border-radius: 12px; border: 1px solid #FFD700; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ================= COMPONENTS =================
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None
if "last_audio_content" not in st.session_state: st.session_state.last_audio_content = None

st.title("🚀 Pro AI")

# Working Yellow Plus Icon
uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg", "mp4"], key="plus_v26")

# Mic Icon
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='fixed_mic_pro')
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    st.toast(f"📎 Attached: {uploaded_file.name}")

# ================= CHAT DISPLAY =================
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask Pro AI anything...")

# ================= LOGIC =================
if audio_data and st.session_state.last_audio_id != audio_data['id']:
    st.session_state.last_audio_id = audio_data['id']
    try:
        transcription = client.audio.transcriptions.create(
            file=("voice.wav", audio_data['bytes']),
            model="whisper-large-v3",
            response_format="text"
        )
        if transcription: u_input = transcription
    except: pass

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        full_res = ""
        box = st.empty()
        sys_msg = "You are Pro AI, a professional assistant."
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": u_input}],
            stream=True
        )
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                box.markdown(full_res + "▌")
        box.markdown(full_res)
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        
        tts = gTTS(text=full_res, lang='en', tld='com.au')
        tts.save("ans.mp3")
        with open("ans.mp3", "rb") as f: st.session_state.last_audio_content = f.read()
        st.rerun()

if st.session_state.last_audio_content:
    if st.button("🔈 Listen"):
        st.audio(st.session_state.last_audio_content, format="audio/mp3", autoplay=True)
        
