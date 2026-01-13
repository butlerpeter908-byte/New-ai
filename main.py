import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz 
from streamlit_mic_recorder import mic_recorder

# API Key check
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing!")

st.set_page_config(page_title="Pro AI", layout="wide")

# --- CSS: MIC POSITION ADJUSTED (3cm Approx Down) ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 2rem;}
    div[data-testid="stVerticalBlock"] > div:empty {display: none !important;}
    
    /* Input Box margin to prevent overlap */
    div[data-testid="stChatInput"] { margin-left: 60px !important; }
    
    /* Mic Position Fix: Moved Downward */
    .mic-container { 
        position: fixed; 
        bottom: 22px; /* Decreased from 37px to move it down */
        left: 20px; 
        z-index: 1005 !important; 
    }

    .mic-container button {
        background-color: #FF4B4B !important;
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        border: 2px solid white !important;
    }

    .menu-card { background-color: #121212; padding: 25px; border-radius: 15px; border: 1px solid #FF4B4B; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None
if "processing" not in st.session_state: st.session_state.processing = False

st.title("🚀 Pro AI")

# --- MENU ---
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📖 About Pro AI")
    st.write("Advanced voice-enabled assistant powered by Whisper & Llama 3.3.")
    st.subheader("🔒 Privacy Policy")
    st.write("Your data is never stored. All sessions are private.")
    st.subheader("⚖️ Terms & Conditions")
    st.write("Ethical use only. Accuracy may vary.")
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT DISPLAY ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- MIC BUTTON ---
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='fixed_recorder')
st.markdown('</div>', unsafe_allow_html=True)

user_query = st.chat_input("Ask Pro AI something...")

# --- FIXED LOGIC: PREVENT AUTO-REPLY ---
if audio:
    # Check if this is a NEW recording by comparing ID
    if st.session_state.last_audio_id != audio['id']:
        st.session_state.last_audio_id = audio['id']
        with st.spinner("Processing voice..."):
            try:
                # Transcription using Whisper
                trans = client.audio.transcriptions.create(
                    file=("audio.wav", audio['bytes']), 
                    model="whisper-large-v3", 
                    response_format="text"
                )
                if trans and len(trans.strip()) > 0:
                    user_query = trans
                else:
                    user_query = None # Prevent empty strings from triggering AI
            except Exception as e:
                st.error(f"Mic error: {e}")
                user_query = None

# --- PROCESS RESPONSE ---
if user_query:
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    ts = f"Time: {now.strftime('%I:%M %p')}, Date: {now.strftime('%d/%m/%Y')}."

    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"): st.markdown(user_query)

    try:
        with st.chat_message("assistant"):
            full_res, res_box = "", st.empty()
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "user", "content": f"{ts} User: {user_query}. Respond in Hindi-English mix."}], 
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            # Text to Speech
            tts = gTTS(text=full_res, lang='hi', tld='com.au')
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

if st.session_state.last_audio:
    if st.button("🔈 Hear Response"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
        
