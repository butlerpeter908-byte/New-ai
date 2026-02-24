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

# ================= ADVANCED CSS (YELLOW THEME & FUNCTIONAL PLUS) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    .block-container {padding-bottom: 120px; padding-top: 2rem;}

    /* Chat Input Adjustments */
    div[data-testid="stChatInput"] { 
        margin-left: 110px !important; 
        z-index: 1000; 
    }

    /* Professional Yellow Plus Icon Logic */
    .stFileUploader {
        position: fixed;
        bottom: 35px;
        left: 20px;
        width: 45px;
        height: 45px;
        z-index: 2005;
        overflow: hidden;
    }
    
    /* Making the uploader look like a Yellow Plus Button */
    .stFileUploader section {
        padding: 0 !important;
        background-color: #FFD700 !important; /* Gold/Yellow Theme */
        border-radius: 50% !important;
        border: 2px solid #000 !important;
        width: 45px !important;
        height: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Hide the default text of uploader */
    .stFileUploader label, .stFileUploader small { display: none !important; }
    .stFileUploader section > div { display: none !important; }
    
    /* Custom '+' symbol inside yellow circle */
    .stFileUploader section::before {
        content: '+';
        color: black;
        font-size: 30px;
        font-weight: bold;
        line-height: 45px;
    }

    /* Mic Position */
    .mic-wrap {
        position: fixed;
        bottom: 30px;
        left: 75px;
        z-index: 2001;
    }
    
    .mic-wrap button {
        background-color: transparent !important;
        border: none !important;
        font-size: 24px !important;
    }

    .menu-card { background-color: #121212; padding: 20px; border-radius: 12px; border: 1px solid #FFD700; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None
if "last_audio_content" not in st.session_state: st.session_state.last_audio_content = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False

st.title("🚀 Pro AI")

# ================= FUNCTIONAL COMPONENTS =================

# 1. Plus Icon (Yellow & Working)
uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg", "mp4"], key="plus_uploader")

# 2. Mic Icon
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='pro_mic_v25')
st.markdown('</div>', unsafe_allow_html=True)

# File logic
if uploaded_file:
    st.toast(f"✅ File Ready: {uploaded_file.name}", icon="📁")

# ================= MENU =================
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("🎬 Video Generator")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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
        sys_msg = "You are Pro AI, a helpful and professional assistant."
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
        
