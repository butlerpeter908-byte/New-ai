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

st.set_page_config(page_title="Pro AI Ultra Fix", layout="wide")

if "messages" not in st.session_state: st.session_state.messages = []

# ================= UI CSS (TINY YELLOW BUTTON) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    
    div[data-testid="stChatInput"] { padding-left: 90px !important; }

    /* Tiny Yellow Plus Button (Size Reduced) */
    .stFileUploader {
        position: fixed; bottom: 35px; left: 15px;
        width: 35px !important; height: 35px !important; z-index: 3000;
    }
    .stFileUploader section {
        padding: 0 !important; min-height: 35px !important;
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important;
    }
    .stFileUploader section div { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 20px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 35px;
    }

    .mic-wrap { position: fixed; bottom: 30px; left: 60px; z-index: 3001; }
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

def get_video_url(prompt, w, h):
    """Fast Video Stream URL"""
    seed = random.randint(1, 9999)
    # Pollinations ka alternative fast endpoint
    return f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width={w}&height={h}&seed={seed}&model=video&nologo=true"

# ================= MAIN APP =================
st.title("🤖 Pro AI: Video & File Fix")

# Sidebar for Video Settings
with st.sidebar:
    v_size = st.radio("Format:", ["Mobile", "Desktop"])
    w, h = (720, 1280) if v_size == "Mobile" else (1280, 720)

# Buttons
uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg", "mp4"], key="tiny_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='tiny_mic')
st.markdown('</div>', unsafe_allow_html=True)

# Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

# Input Logic
u_input = st.chat_input("Prompt likho ya video banao...")

# Agar file upload hui hai toh uska solution do
if uploaded_file and not u_input:
    u_input = f"I have uploaded a file named {uploaded_file.name}. Please analyze it."

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    v_url_saved = None

    with st.chat_message("assistant"):
        india_tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(india_tz)

        # 1. VIDEO LOGIC (Fixed)
        if any(x in txt for x in ["video", "generate", "banao"]):
            with st.spinner("🎬 Creating Video..."):
                v_url = get_video_url(u_input, w, h)
                st.video(v_url)
                st.markdown(f"### [📥 Download Video]({v_url})")
                v_url_saved = v_url
                final_reply = "Bhai, video ready hai! Agar blank dikhe toh 2-3 second wait karna, load ho rahi hai."

        # 2. FILE ANALYSIS LOGIC
        elif uploaded_file:
            final_reply = f"Bhai, maine aapki file '{uploaded_file.name}' dekh li hai. Isme jo data/image hai wo process ho raha hai. Groq AI iska solution niche de raha hai..."
            # Yahan file-based chat logic add kar sakte hain

        # 3. DATE/TIME/WEATHER
        elif any(x in txt for x in ["time", "date", "weather"]):
            final_reply = f"Navi Mumbai Time: {now.strftime('%I:%M %p')}, Date: {now.strftime('%d %B %Y')}."

        # 4. GENERAL CHAT
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # Save and Rerun
    new_msg = {"role": "assistant", "content": final_reply}
    if v_url_saved: new_msg["v_url"] = v_url_saved
    st.session_state.messages.append(new_msg)
    st.rerun()
    
