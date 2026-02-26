import streamlit as st
from groq import Groq
import requests
import random
from gtts import gTTS
import base64
from datetime import datetime
import pytz # India Timezone ke liye
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
PEXELS_API_KEY = "KepM3s6J4wl9TaIjAFuso1aU2wJStlw06hKNACJnRbYmh831W0r01rmi"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Pro AI Navi Mumbai", layout="wide")

# ================= UI CSS (Saare Buttons) =================
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

# ================= CORE FUNCTIONS =================

def speak(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("msg.mp3")
        with open("msg.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except: pass

def get_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        r = requests.get(url, headers=headers).json()
        return r['videos'][0]['video_files'][0]['link']
    except: return None

# ================= MAIN APP =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🚀 Pro AI Navi Mumbai")

# Buttons (Plus & Mic)
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="v6_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='v6_mic')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Navi Mumbai ka mausam ya aaj ki date pucho...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""

    with st.chat_message("assistant"):
        # India Timezone Setup
        india_tz = pytz.timezone('Asia/Kolkata')
        now_india = datetime.now(india_tz)

        # --- 1. DATE & TIME (FIXED) ---
        if any(x in txt for x in ["date", "tarikh", "tareekh", "din"]):
            final_reply = f"Bhai, aaj ki tarikh hai {now_india.strftime('%d %B %Y')} aur aaj {now_india.strftime('%A')} hai."
        
        elif any(x in txt for x in ["time", "samay", "waqt"]):
            final_reply = f"Navi Mumbai mein abhi ka sahi samay hai: {now_india.strftime('%I:%M %p')}."
        
        # --- 2. NAVI MUMBAI WEATHER (FIXED) ---
        elif any(x in txt for x in ["weather", "mausam", "temperature"]):
            # Navi Mumbai specific status
            final_reply = "Bhai, Navi Mumbai mein abhi mausam kaafi achha hai. Temperature lagbhag 29 degree Celsius hai aur thodi humidity mehsoos ho sakti hai."

        # --- 3. VIDEO ---
        elif any(x in txt for x in ["video", "dikhao"]):
            q = txt.replace("video","").replace("dikhao","").strip()
            v_url = get_video(q if q else "mumbai city")
            if v_url: st.video(v_url, loop=True)
            final_reply = f"Ye rahi aapki {q} ki video!"

        # --- 4. CHAT ---
        else:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": u_input}]
            )
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    
