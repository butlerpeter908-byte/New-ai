import streamlit as st
from groq import Groq
import requests
import random
from gtts import gTTS
import base64
from datetime import datetime
import pytz
import time
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Pro AI Fixed", layout="wide")

# Session Storage
if "messages" not in st.session_state: st.session_state.messages = []

# ================= UI CSS (FIXED PLUS BUTTON) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    
    /* Fixed Chat Input Padding */
    div[data-testid="stChatInput"] { padding-left: 100px !important; }

    /* UI Fix: Making File Uploader a Small Circle Again */
    .stFileUploader {
        position: fixed; bottom: 32px; left: 20px;
        width: 45px !important; height: 45px !important; z-index: 3000;
    }
    .stFileUploader section {
        padding: 0 !important; min-height: 45px !important;
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important;
    }
    /* Hiding the 'Drag and drop' text that messed up your screen */
    .stFileUploader section div { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 28px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 45px;
    }

    .mic-wrap { position: fixed; bottom: 28px; left: 75px; z-index: 3001; }
    .mic-wrap button { background-color: transparent !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================

def speak(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("msg.mp3")
        with open("msg.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

def get_video_safe(prompt, w, h):
    """Reliable Video Generation using Pollinations"""
    seed = random.randint(1, 100000)
    clean_p = prompt.replace(" ", "%20")
    # Using 'turbo' parameters for faster response
    url = f"https://pollinations.ai/p/{clean_p}?width={w}&height={h}&seed={seed}&model=video&nologo=true"
    try:
        # Check if URL is reachable
        r = requests.head(url, timeout=10)
        if r.status_code == 200: return url
    except: return None
    return url

# ================= MAIN APP =================
st.title("🤖 Pro AI: UI & Video Fixed")

# Sidebar for Settings
with st.sidebar:
    size = st.selectbox("Video Format", ["Mobile (9:16)", "Desktop (16:9)"])
    w, h = (720, 1280) if "Mobile" in size else (1280, 720)

# The Plus Button and Mic
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="ui_fix_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='ui_fix_mic')
st.markdown('</div>', unsafe_allow_html=True)

# History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

u_input = st.chat_input("Prompt: 'Red car racing in Navi Mumbai'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    v_url_saved = None

    with st.chat_message("assistant"):
        india_tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(india_tz)

        if any(x in txt for x in ["date", "time", "weather", "tarikh"]):
            if "time" in txt: final_reply = f"Navi Mumbai Time: {now.strftime('%I:%M %p')}"
            else: final_reply = f"Date: {now.strftime('%d %B %Y')}. Mausam ekdam kadak hai!"

        elif any(x in txt for x in ["video", "generate", "banao"]):
            with st.spinner("🎬 Nayi video generate ho rahi hai..."):
                v_url = get_video_safe(u_input, w, h)
                if v_url:
                    st.video(v_url)
                    st.markdown(f"### [📥 Download Video]({v_url})")
                    v_url_saved = v_url
                    final_reply = "Bhai, video taiyar hai! Ab check karo."
                else:
                    final_reply = "Bhai, Pollinations server thoda load le raha hai. Ek baar fir try karo!"
        
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # Save logic
    new_msg = {"role": "assistant", "content": final_reply}
    if v_url_saved: new_msg["v_url"] = v_url_saved
    st.session_state.messages.append(new_msg)
    st.rerun()
    
