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
except:
    st.error("Groq Connection Error!")

st.set_page_config(page_title="Pro AI Final", layout="wide")

# ================= UI CSS (All Buttons) =================
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
    """Voice generator and autoplay"""
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("msg.mp3")
        with open("msg.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio src="data:audio/mp3;base64,{b64}" autoplay></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except: pass

def get_video(query):
    """Relatable video from Pexels"""
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        r = requests.get(url, headers=headers).json()
        return r['videos'][0]['video_files'][0]['link']
    except: return None

# ================= MAIN APP =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🚀 Pro AI Ultra v4")

# Buttons (Plus, Mic)
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="v4_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='v4_mic')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Pucho: Time kya hai? ya Video dikhao...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    reply = ""

    with st.chat_message("assistant"):
        # 1. TIME LOGIC
        if "time" in txt or "samay" in txt or "waqt" in txt:
            reply = f"Bhai, abhi ka sahi samay hai: {datetime.now().strftime('%I:%M %p')}"
        
        # 2. WEATHER LOGIC
        elif "weather" in txt or "mausam" in txt:
            reply = "Bhai, mausam ekdam suhana hai, bahar ghoomne layak din hai!"
            
        # 3. VIDEO LOGIC (Trigger only if specifically asked)
        elif "video" in txt or "dikhao" in txt:
            q = txt.replace("video","").replace("dikhao","").strip()
            v_url = get_video(q if q else "nature")
            if v_url: st.video(v_url, loop=True)
            reply = f"Ye rahi aapki {q} ki video!"

        # 4. CHAT LOGIC (General)
        else:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": u_input}]
            )
            reply = res.choices[0].message.content
        
        # Show Reply & Speak
        st.write(reply)
        speak(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    
