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

st.set_page_config(page_title="AI Video Pro Fix", layout="wide")

# Persistent Storage
if "messages" not in st.session_state: st.session_state.messages = []

# ================= UI CSS (ULTRA MINIMAL) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    
    div[data-testid="stChatInput"] { padding-left: 80px !important; }

    /* Tiny Minimal Plus Button */
    .stFileUploader {
        position: fixed; bottom: 35px; left: 15px;
        width: 32px !important; height: 32px !important; z-index: 3000;
    }
    .stFileUploader section {
        padding: 0 !important; min-height: 32px !important;
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important;
    }
    .stFileUploader section div { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 18px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 32px;
    }

    .mic-wrap { position: fixed; bottom: 32px; left: 55px; z-index: 3001; }
    .mic-wrap button { background-color: transparent !important; border: none !important; }
    
    /* Video Box Fix */
    .stVideo { border: 2px solid #FFD700; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# ================= CORE FUNCTIONS =================

def speak(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("msg.mp3")
        with open("msg.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

@st.cache_data(show_spinner=False)
def fetch_video_bytes(url):
    """Wait and download video bytes to avoid broken player"""
    max_retries = 5
    for i in range(max_retries):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200 and len(r.content) > 10000: # Check if file is real
                return r.content
        except: pass
        time.sleep(6) # Wait 6 seconds for rendering
    return None

# ================= MAIN APP =================
st.title("🤖 Pro Generative AI")

# Display History First
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_bytes" in m:
            st.video(m["v_bytes"])

# Inputs
uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg", "mp4"], key="ultra_v2")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='ultra_mic_v2')
st.markdown('</div>', unsafe_allow_html=True)

u_input = st.chat_input("Prompt: 'Cinematic red car in Mumbai rain'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    video_to_save = None

    with st.chat_message("assistant"):
        india_tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(india_tz)

        # 🕒 COMMANDS
        if any(x in txt for x in ["time", "date", "weather"]):
            final_reply = f"Navi Mumbai Time: {now.strftime('%I:%M %p')}, Date: {now.strftime('%d %B %Y')}."

        # 🎬 VIDEO LOGIC (ZERO BROKEN)
        elif any(x in txt for x in ["video", "generate", "banao"]):
            with st.status("🧠 AI is Creating Video (This may take 30s)...") as status:
                seed = random.randint(1, 999999)
                # Direct video generation link
                v_url = f"https://pollinations.ai/p/{u_input.replace(' ', '%20')}?width=720&height=1280&seed={seed}&model=video"
                
                # AB HUM BYTES DOWNLOAD KARENGE BINA BROKEN PLAYER KE
                video_data = fetch_video_bytes(v_url)
                
                if video_data:
                    st.video(video_data)
                    st.download_button("📥 Save to Gallery", data=video_data, file_name="ai_video.mp4")
                    video_to_save = video_data
                    status.update(label="✅ Success!", state="complete")
                    final_reply = "Bhai, video taiyar hai! Ab ye hategi nahi."
                else:
                    status.update(label="❌ Server Busy", state="error")
                    final_reply = "Bhai, server thoda slow hai. Ek baar fir try karo!"

        # 🧠 CHAT
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # Persistence Save
    msg_data = {"role": "assistant", "content": final_reply}
    if video_to_save: msg_data["v_bytes"] = video_to_save
    st.session_state.messages.append(msg_data)
    st.rerun()
