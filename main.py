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

# ================= ADVANCED CSS (GEMINI STYLE) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    .block-container {padding-bottom: 100px; padding-top: 2rem;}
    
    /* Input Container Styling */
    div[data-testid="stChatInput"] {
        padding-left: 90px !important;
        padding-right: 50px !important;
    }

    /* Fixed Plus Button (Gemini Style) */
    .plus-btn-container {
        position: fixed;
        bottom: 34px;
        left: 30px;
        z-index: 2000;
        background: #1e1e1e;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #333;
    }

    /* Fixed Mic Button (Side of Chat) */
    .mic-wrap {
        position: fixed;
        bottom: 28px;
        left: 80px;
        z-index: 2001;
    }
    
    .mic-wrap button {
        background-color: transparent !important;
        border: none !important;
        font-size: 20px !important;
        color: #FF4B4B !important;
    }

    .menu-card { background-color: #121212; padding: 20px; border-radius: 12px; border: 1px solid #FF4B4B; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None
if "last_audio_content" not in st.session_state: st.session_state.last_audio_content = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False

st.title("🚀 Pro AI")

# ================= SIDE BUTTONS (PLUS & MIC) =================
# Plus Icon Overlay
st.markdown('<div class="plus-btn-container">➕</div>', unsafe_allow_html=True)
# Hidden file uploader that triggers on idea
with st.sidebar:
    uploaded_file = st.file_uploader("Upload Image/Video", type=["png", "jpg", "mp4"])

# Mic Overlay
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='gemini_style_mic')
st.markdown('</div>', unsafe_allow_html=True)

# ================= MENU =================
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("🎬 AI Video Gen")
    if st.button("Generate Sample Video"):
        st.info("Video API integration active.")
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
    IST = pytz.timezone('Asia/Kolkata')
    curr_time = datetime.datetime.now(IST).strftime("%I:%M %p")
    
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        full_res = ""
        box = st.empty()
        sys_msg = f"You are Pro AI. Time: {curr_time}. Respond like a premium AI assistant."
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
        
