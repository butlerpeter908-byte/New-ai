import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz 
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP (KEY INTEGRATED) =================
# Bhai, maine aapki key yahan paste kar di hai
GROQ_KEY = "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"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ API Error! Please check your key.")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= CSS: PLUS ICON, MIC & UI FIXES =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    .block-container {padding-bottom: 160px; padding-top: 2rem;}
    hr {border: none !important; display: none !important;}
    
    /* Plus Icon Styling */
    .plus-container {
        position: fixed;
        bottom: 58px;
        left: 80px;
        z-index: 1001;
    }
    
    /* Chat Input Adjustments for Plus Icon */
    div[data-testid="stChatInput"] { 
        margin-left: 100px !important; 
        z-index: 1000; 
        border: none !important; 
    }

    /* Mic Position Adjustment */
    .mic-fixed-container { position: fixed; bottom: 53px; left: 15px; z-index: 9999 !important; }
    .mic-fixed-container button {
        background-color: #FF4B4B !important;
        border-radius: 50% !important;
        width: 52px !important; height: 52px !important;
        border: 2px solid white !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5) !important;
    }

    .menu-card { background-color: #121212; padding: 25px; border-radius: 15px; border: 1px solid #FF4B4B; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None
if "last_audio_content" not in st.session_state: st.session_state.last_audio_content = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False

st.title("🚀 Pro AI")

# ================= MENU SECTION =================
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("🎬 AI Video Generator")
    v_prompt = st.text_input("Describe video:")
    if st.button("Generate Video"):
        st.info("Video generation logic is ready for integration.")
    st.divider()
    st.subheader("📖 About Pro AI")
    st.info("Professional Multimodal AI Assistant.")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ================= PLUS ICON & MIC =================
st.markdown('<div class="mic-fixed-container">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🌊", key='final_verified_mic_v24')
st.markdown('</div>', unsafe_allow_html=True)

# Plus Icon for uploads
with st.container():
    st.markdown('<div class="plus-container">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(" ", type=["png", "jpg", "jpeg", "mp4"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    st.toast(f"File uploaded: {uploaded_file.name}", icon="📎")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me anything...")

# ================= VOICE & RESPONSE LOGIC =================
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
    curr_date = datetime.datetime.now(IST).strftime("%d %B, %Y")
    
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        full_res = ""
        box = st.empty()
        sys_msg = f"You are Pro AI. Date: {curr_date}. Time: {curr_time}. Respond professionally."
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
    if st.button("🔈 Hear Response"):
        st.audio(st.session_state.last_audio_content, format="audio/mp3", autoplay=True)
        
