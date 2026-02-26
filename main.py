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

st.set_page_config(page_title="Pro AI Ultra Fix", layout="wide")

# ================= UI CSS (All Buttons & Dark Theme) =================
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
            md = f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except: pass

def get_video(query):
    """Relatable video from Pexels"""
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        r = requests.get(url, headers=headers).json()
        if r['videos']:
            return r['videos'][0]['video_files'][0]['link']
    except: return None
    return None

# ================= MAIN APP =================
if "messages" not in st.session_state: 
    st.session_state.messages = []

st.title("🚀 Pro AI Ultra Fix")

# Icons Setup (Plus & Mic)
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="fixed_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='fixed_mic')
st.markdown('</div>', unsafe_allow_html=True)

# History Display
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Pucho: 'Time kya hai?' ya 'Car ki video dikhao'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""

    with st.chat_message("assistant"):
        # --- 1. PRIORITY: TIME CHECK ---
        if any(x in txt for x in ["time", "samay", "waqt"]):
            final_reply = f"Bhai, abhi ka sahi samay hai: {datetime.now().strftime('%I:%M %p')}"
        
        # --- 2. PRIORITY: WEATHER CHECK ---
        elif any(x in txt for x in ["weather", "mausam", "temperature"]):
            final_reply = "Bhai, mausam ekdam mast hai, lagbhag 24°C temperature hai aur thandi hawa chal rahi hai!"

        # --- 3. PRIORITY: VIDEO CHECK ---
        elif any(x in txt for x in ["video", "dikhao", "show"]):
            q = txt.replace("video","").replace("dikhao","").replace("show","").strip()
            v_url = get_video(q if q else "nature")
            if v_url:
                st.video(v_url, loop=True)
                final_reply = f"Ye rahi aapki {q} ki video!"
            else:
                final_reply = "Sorry bhai, is topic par video nahi mili, par main bol raha hoon!"

        # --- 4. DEFAULT: CHAT WITH GROQ ---
        else:
            try:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": u_input}]
                )
                final_reply = res.choices[0].message.content
            except:
                final_reply = "Sorry bhai, Groq thoda busy hai, baad mein try karo."

        # Show Text and Start Voice Autoplay
        st.write(final_reply)
        speak(final_reply)

    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    
