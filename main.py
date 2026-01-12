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
    st.error("API Key missing! Please check your Streamlit secrets.")

st.set_page_config(page_title="Pro AI", layout="wide")

# --- CSS: FIXED UI (No White Lines) ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 2rem;}
    div[data-testid="stVerticalBlock"] > div:empty {display: none !important;}
    
    div.stButton > button:first-child { 
        margin-top: -40px !important; 
        background-color: #FF4B4B !important; 
        color: white !important;
    }
    div[data-testid="stChatInput"] { margin-left: 110px !important; }
    
    .plus-icon-container { 
        position: fixed; bottom: 32px; left: 15px; 
        background-color: #FF4B4B; color: white; 
        border-radius: 50%; width: 42px; height: 42px; 
        display: flex; align-items: center; justify-content: center; 
        font-size: 25px; font-weight: bold; z-index: 1000; 
        border: 2px solid white; 
    }
    .mic-container { position: fixed; bottom: 32px; left: 65px; z-index: 1005 !important; }
    div[data-testid="stFileUploader"] { 
        position: fixed; bottom: 32px; left: 15px; 
        width: 42px; height: 42px; opacity: 0; 
        z-index: 1002; cursor: pointer; 
    }
    .menu-card { background-color: #121212; padding: 25px; border-radius: 15px; border: 1px solid #FF4B4B; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False
if "img_data" not in st.session_state: st.session_state.img_data = None
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None

st.title("🚀 Pro AI")

# --- MENU BUTTON & CONTENT (English) ---
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📖 About Pro AI")
    st.write("Pro AI is a multi-modal assistant using Llama 3.2 Vision and Whisper to handle text, voice, and visual data.")
    st.subheader("🔒 Privacy Policy")
    st.write("We do not store your data. Conversations are encrypted in transit and deleted after each session.")
    st.subheader("⚖️ Terms & Conditions")
    st.write("Use responsibly. AI accuracy is high but not absolute.")
    st.divider()
    st.subheader("📬 Feedback")
    fb = st.text_area("How can we improve?")
    if st.button("Submit"):
        try:
            r = requests.post(f"https://api.github.com/repos/{st.secrets['GITHUB_REPO']}/issues", 
                              json={"title": "Feedback", "body": fb}, 
                              headers={"Authorization": f"token {st.secrets['GITHUB_TOKEN']}"})
            if r.status_code == 201: st.success("Sent!")
        except: st.error("Feedback error.")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages, st.session_state.img_data = [], None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PHOTO ---
st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
photo = st.file_uploader("", type=["jpg", "png", "jpeg"], key="cam", label_visibility="collapsed")
if photo: st.session_state.img_data = photo.getvalue()
if st.session_state.img_data:
    st.image(st.session_state.img_data, width=250)
    if st.button("❌ Remove"):
        st.session_state.img_data = None
        st.rerun()

# --- CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- MIC ---
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')
st.markdown('</div>', unsafe_allow_html=True)

user_query = st.chat_input("Ask me anything...")

if audio and st.session_state.last_audio_id != audio['id']:
    st.session_state.last_audio_id = audio['id']
    with st.spinner("Processing voice..."):
        try:
            trans = client.audio.transcriptions.create(file=("audio.wav", audio['bytes']), model="whisper-large-v3", response_format="text")
            user_query = trans
        except: st.error("Mic failed.")

if user_query:
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    ts = f"Time: {now.strftime('%I:%M %p')}, Date: {now.strftime('%d/%m/%Y')}."

    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"): st.markdown(user_query)

    try:
        # --- MODEL LOGIC: FIXING ERROR 400 ---
        if st.session_state.img_data:
            # Vision model ke liye content 'list' format mein hona chahiye
            b64 = base64.b64encode(st.session_state.img_data).decode('utf-8')
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{ts} User: {user_query}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }]
            model = "llama-3.2-11b-vision-preview"
        else:
            # Text model ke liye content 'string' hona chahiye
            messages = [{"role": "user", "content": f"{ts} User: {user_query}"}]
            model = "llama-3.3-70b-versatile"

        with st.chat_message("assistant"):
            full_res, res_box = "", st.empty()
            stream = client.chat.completions.create(model=model, messages=messages, stream=True)
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            tts = gTTS(text=full_res, lang='hi', tld='com.au')
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
            st.rerun()
    except Exception as e:
        st.error(f"Groq API Error: {e}")

if st.session_state.last_audio:
    if st.button("🔈 Hear Response"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
        
