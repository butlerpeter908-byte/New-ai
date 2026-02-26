import streamlit as st
from groq import Groq
import requests
import random
from gtts import gTTS
import base64
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
PEXELS_API_KEY = "KepM3s6J4wl9TaIjAFuso1aU2wJStlw06hKNACJnRbYmh831W0r01rmi"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq Error!")

st.set_page_config(page_title="Pro AI Ultra", layout="wide")

# ================= FULL UI CSS =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 1rem; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }
    
    .stFileUploader {
        position: fixed; bottom: 32px; left: 20px;
        width: 40px !important; height: 40px !important; z-index: 2005;
    }
    .stFileUploader section {
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important; width: 40px !important; height: 40px !important;
    }
    .stFileUploader label, .stFileUploader small { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 24px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 100%;
    }

    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= UTILITY FUNCTIONS =================

def get_weather(city="Delhi"):
    # Weather ke liye ek free API call (demo purposes)
    return f"Bhai, {city} mein mausam ekdam mast hai, lagbhag 25°C temperature hai."

def text_to_speech_autoplay(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio src="data:audio/mp3;base64,{b64}" autoplay></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except: pass

def get_pexels_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=3"
    try:
        r = requests.get(url, headers=headers).json()
        return random.choice(r['videos'])['video_files'][0]['link']
    except: return None

# ================= MAIN APP =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🚀 Pro AI Ultra")

# Menu Buttons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="ultra_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='ultra_mic')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Time, Weather ya Video... kuch bhi pucho!")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    low_input = u_input.lower()
    final_reply = ""

    with st.chat_message("assistant"):
        # 🕒 1. Check for TIME
        if "time" in low_input or "samay" in low_input:
            final_reply = f"Abhi ka samay hai: {datetime.now().strftime('%I:%M %p')}"
            st.write(final_reply)
        
        # 🌤️ 2. Check for WEATHER
        elif "weather" in low_input or "mausam" in low_input:
            final_reply = get_weather()
            st.write(final_reply)

        # 🧠 3. General AI Chat
        else:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": u_input}]
            )
            final_reply = completion.choices[0].message.content
            st.write(final_reply)

        # 🎙️ Voice Sync
        text_to_speech_autoplay(final_reply)

        # 🎬 Video Logic
        if any(x in low_input for x in ["video", "show", "car", "nature"]):
            v_url = get_pexels_video(low_input.replace("video","").strip())
            if v_url: st.video(v_url, loop=True)

    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    
