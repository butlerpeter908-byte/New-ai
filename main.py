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

st.set_page_config(page_title="Pro AI Fixed Video", layout="wide")

# Session State Storage
if "messages" not in st.session_state: st.session_state.messages = []

# ================= MODERN UI CSS =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }
    .stFileUploader { position: fixed; bottom: 32px; left: 20px; width: 40px !important; z-index: 2005; }
    .stFileUploader section { background-color: #FFD700 !important; border-radius: 50% !important; }
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .video-card { border: 2px solid #FFD700; border-radius: 10px; padding: 5px; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================

def speak(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("msg.mp3")
        with open("msg.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

def get_video_with_retry(url, retries=5):
    """Wait for video to be actually generated on Pollinations"""
    for i in range(retries):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200 and len(r.content) > 5000: # Check if file is not empty
                return r.content
        except: pass
        time.sleep(5) # 5 second wait before next try
    return None

# ================= MAIN APP =================
st.title("🤖 Pro AI: Zero Blank Fix")

with st.sidebar:
    size = st.radio("Format:", ["Mobile", "Desktop"])
    w, h = (720, 1280) if size == "Mobile" else (1280, 720)

# Buttons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="fixed_btn")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='fixed_mic')
st.markdown('</div>', unsafe_allow_html=True)

# Display Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "video_data" in m:
            st.video(m["video_data"])

# User Input
u_input = st.chat_input("Prompt: 'Red car racing in Navi Mumbai'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    v_data_save = None

    with st.chat_message("assistant"):
        india_tz = pytz.timezone('Asia/Kolkata')
        now_india = datetime.now(india_tz)

        # 1. SPECIAL COMMANDS
        if any(x in txt for x in ["date", "time", "weather", "tarikh"]):
            if "date" in txt or "tarikh" in txt:
                final_reply = f"Aaj ki tarikh hai {now_india.strftime('%d %B %Y')}."
            elif "time" in txt:
                final_reply = f"Navi Mumbai ka samay: {now_india.strftime('%I:%M %p')}."
            else:
                final_reply = "Navi Mumbai mein mausam 29°C aur mast hai!"

        # 2. VIDEO GENERATION WITH WAIT LOGIC
        elif any(x in txt for x in ["video", "generate", "banao"]):
            with st.spinner("⏳ AI video bana raha hai... (Blank nahi aayega is baar)"):
                seed = random.randint(1, 999999)
                v_url = f"https://pollinations.ai/p/{u_input.replace(' ', '%20')}?width={w}&height={h}&seed={seed}&model=video"
                
                v_data = get_video_with_retry(v_url)
                if v_data:
                    st.video(v_data)
                    st.download_button("📥 Download HD Video", data=v_data, file_name="ai_video.mp4", mime="video/mp4")
                    v_data_save = v_data
                    final_reply = "Bhai, video ekdam ready hai! Ab download karke dekho."
                else:
                    final_reply = "Bhai, server busy hai. Ek baar fir se 'Generate' bolo!"

        # 3. NORMAL CHAT
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # Save to history
    new_msg = {"role": "assistant", "content": final_reply}
    if v_data_save: new_msg["video_data"] = v_data_save
    st.session_state.messages.append(new_msg)
    st.rerun()
    
