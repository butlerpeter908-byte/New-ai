import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz # IST ke liye
from streamlit_mic_recorder import mic_recorder

# API Key check
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing!")

st.set_page_config(page_title="Pro AI", layout="wide")

# --- CSS: UI FIXES ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px;}
    div.stButton > button:first-child { margin-top: -40px !important; background-color: #FF4B4B !important; color: white !important;}
    div[data-testid="stChatInput"] { margin-left: 100px !important; }
    .plus-icon-container { position: fixed; bottom: 32px; left: 15px; background-color: #FF4B4B; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 25px; font-weight: bold; z-index: 1000; border: 2px solid white; }
    .mic-container { position: fixed; bottom: 32px; left: 65px; z-index: 1000; }
    div[data-testid="stFileUploader"] { position: fixed; bottom: 32px; left: 15px; width: 40px; height: 40px; opacity: 0; z-index: 1001; cursor: pointer; }
    .menu-card { background-color: #121212; padding: 20px; border-radius: 15px; border: 1px solid #FF4B4B; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None

st.title("🚀 Pro AI")

if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📖 Pro AI Control Panel")
    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    st.markdown("🔒 **Privacy:** No data saved. | ⚖️ **Terms:** Legal use only.")
    st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

voice_prompt = None
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')
st.markdown('</div>', unsafe_allow_html=True)

if audio_data:
    if st.session_state.last_audio_id != audio_data['id']:
        st.session_state.last_audio_id = audio_data['id']
        with st.spinner("Processing Voice..."):
            try:
                with open("temp.wav", "wb") as f: f.write(audio_data['bytes'])
                with open("temp.wav", "rb") as f:
                    transcription = client.audio.transcriptions.create(file=("temp.wav", f.read()), model="whisper-large-v3", response_format="text")
                voice_prompt = transcription
            except Exception as e: st.error(f"Mic Error: {e}")

user_input = voice_prompt if voice_prompt else st.chat_input("Yahan puchiye...")

if user_input:
    # --- IST TIME CONVERSION ---
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    cur_time = now.strftime("%I:%M %p")
    cur_date = now.strftime("%d/%m/%Y")

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    try:
        sys_info = f"Current Time: {cur_time}. Current Date: {cur_date}."
        instruction = "Professional AI. Use NUMERIC format for Time/Date (e.g. 02:30 PM). Never use words for numbers in time. Respond in Hindi/English mix."
        content = [{"type": "text", "text": f"{sys_info}\n{instruction}\nUser: {user_input}"}]
        
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            st.image(uploaded_file, width=150)

        with st.chat_message("assistant"):
            full_res = ""
            res_box = st.empty()
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": content}], stream=True)
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
    if st.button("🔈 Jawab Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
        
