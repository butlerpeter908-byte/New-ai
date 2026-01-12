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

# --- CSS: UI STABILITY & WHITE LINE REMOVAL ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 2rem;}
    
    /* Remove white lines/empty containers */
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

if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False
if "img_data" not in st.session_state: st.session_state.img_data = None
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None

st.title("🚀 Pro AI")

# --- MENU BUTTON ---
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

# --- MENU CONTENT (ENGLISH) ---
if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    
    # 1. About Us
    st.subheader("📖 About Pro AI")
    st.write("""
    Pro AI is an advanced artificial intelligence assistant powered by cutting-edge Vision and Voice technology. 
    By leveraging state-of-the-art models like Llama 3.2 Vision and Whisper, this platform provides intelligent 
    responses to text, images, and voice commands. Our mission is to offer a seamless personal assistant 
    capable of analyzing complex visuals and providing real-time information with high efficiency.
    """)

    # 2. Privacy Policy
    st.subheader("🔒 Privacy Policy")
    st.write("""
    Your privacy is our utmost priority. Pro AI is designed to be a privacy-first platform; we do not store, 
    save, or share any of your personal data, chat history, or uploaded images on our servers. 
    All processing occurs within temporary sessions, and all data is immediately purged once the session ends 
    or the chat is cleared. We do not use third-party tracking or sell user information to any external entities.
    """)

    # 3. Terms & Conditions
    st.subheader("⚖️ Terms & Conditions")
    st.write("""
    By using this application, you agree to use the platform solely for lawful and ethical purposes. 
    Any attempt to upload harmful, abusive, or illegal content is strictly prohibited. 
    Please note that while our AI is highly advanced, responses may not always be 100% accurate; 
    users should verify critical information independently. Pro AI reserves the right to modify 
    or terminate services at any time without prior notice.
    """)

    st.divider()
    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.session_state.img_data = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PHOTO HANDLING ---
st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
new_photo = st.file_uploader("", type=["jpg", "png", "jpeg"], key="camera_uploader", label_visibility="collapsed")

if new_photo:
    st.session_state.img_data = new_photo.getvalue()

if st.session_state.img_data:
    st.image(st.session_state.img_data, caption="Captured Image", width=250)
    if st.button("❌ Remove Image"):
        st.session_state.img_data = None
        st.rerun()

# --- CHAT AREA ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- MIC ---
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')
st.markdown('</div>', unsafe_allow_html=True)

voice_prompt = None
if audio_data and st.session_state.last_audio_id != audio_data['id']:
    st.session_state.last_audio_id = audio_data['id']
    with st.spinner("Listening..."):
        try:
            with open("temp.wav", "wb") as f: f.write(audio_data['bytes'])
            with open("temp.wav", "rb") as f:
                transcription = client.audio.transcriptions.create(file=("temp.wav", f.read()), model="whisper-large-v3", response_format="text")
            voice_prompt = transcription
        except: st.error("Mic issue.")

user_input = voice_prompt if voice_prompt else st.chat_input("Ask me anything...")

if user_input:
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    cur_time, cur_date = now.strftime("%I:%M %p"), now.strftime("%d/%m/%Y")

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    try:
        # Vision-Ready content format
        content_list = [{"type": "text", "text": f"System Time: {cur_time}, Date: {cur_date}. User Question: {user_input}"}]
        
        if st.session_state.img_data:
            base64_image = base64.b64encode(st.session_state.img_data).decode('utf-8')
            content_list.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })

        with st.chat_message("assistant"):
            full_res = ""
            res_box = st.empty()
            # Fixed Vision Model
            comp = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{"role": "user", "content": content_list}],
                stream=True
            )
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
        
