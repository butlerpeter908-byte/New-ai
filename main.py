import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz 
from streamlit_mic_recorder import mic_recorder
from io import BytesIO

# API Key check
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing!")

st.set_page_config(page_title="Pro AI", layout="wide")

# --- CSS: UI STABILITY ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 2rem;}
    
    div[data-testid="stVerticalBlock"] > div:empty {display: none !important;}
    .stEmpty { margin: 0px !important; padding: 0px !important; display: none; }
    
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

# Session State Initialization
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False
if "img_data" not in st.session_state: st.session_state.img_data = None
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None
if "mic_text" not in st.session_state: st.session_state.mic_text = None

st.title("🚀 Pro AI")

# --- MENU SECTION ---
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📖 About Pro AI")
    st.write("Pro AI is an advanced AI assistant using Llama 3.2 Vision and Whisper for seamless text, image, and voice interaction.")
    st.subheader("🔒 Privacy Policy")
    st.write("We prioritize your privacy. No data is stored; all interactions are temporary and deleted after the session.")
    st.subheader("⚖️ Terms & Conditions")
    st.write("Use this platform for lawful purposes. AI responses may not be 100% accurate.")
    st.divider()
    st.subheader("📬 GitHub Feedback")
    feedback_msg = st.text_area("Your thoughts?")
    if st.button("Submit Feedback"):
        try:
            token, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
            res = requests.post(f"https://api.github.com/repos/{repo}/issues", 
                                json={"title": "User Feedback", "body": feedback_msg}, 
                                headers={"Authorization": f"token {token}"})
            if res.status_code == 201: st.success("Sent!")
        except: st.error("Error sending feedback.")
    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages, st.session_state.img_data = [], None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PHOTO HANDLING ---
st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
new_photo = st.file_uploader("", type=["jpg", "png", "jpeg"], key="camera_uploader", label_visibility="collapsed")
if new_photo: st.session_state.img_data = new_photo.getvalue()
if st.session_state.img_data:
    st.image(st.session_state.img_data, width=250)
    if st.button("❌ Remove Photo"):
        st.session_state.img_data = None
        st.rerun()

# --- CHAT AREA ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- MIC LOGIC (FIXED) ---
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')
st.markdown('</div>', unsafe_allow_html=True)

if audio_data and st.session_state.last_audio_id != audio_data['id']:
    st.session_state.last_audio_id = audio_data['id']
    try:
        with st.spinner("Processing Voice..."):
            transcription = client.audio.transcriptions.create(
                file=("temp.wav", audio_data['bytes']), 
                model="whisper-large-v3", 
                response_format="text"
            )
            if transcription:
                st.session_state.mic_text = transcription
                st.rerun()
    except Exception as e:
        st.error(f"Mic Error: {e}")

# Process Input
user_input = st.session_state.mic_text if st.session_state.mic_text else st.chat_input("Ask me anything...")
st.session_state.mic_text = None # Clear after use

if user_input:
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    cur_time, cur_date = now.strftime("%I:%M %p"), now.strftime("%d/%m/%Y")

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    try:
        if st.session_state.img_data:
            img_b64 = base64.b64encode(st.session_state.img_data).decode('utf-8')
            content = [
                {"type": "text", "text": f"User: {user_input} (Time: {cur_time}, Date: {cur_date})"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
            model = "llama-3.2-11b-vision-preview"
        else:
            content = f"Time: {cur_time}, Date: {cur_date}. Question: {user_input}"
            model = "llama-3.3-70b-versatile"

        with st.chat_message("assistant"):
            full_res, res_box = "", st.empty()
            comp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": content}], stream=True)
            for chunk in comp:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state.last_audio:
    if st.button("🔈 Hear Response"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
        
