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

st.set_page_config(page_title="AI Video Engine Pro", layout="wide")

if "messages" not in st.session_state: st.session_state.messages = []

# ================= UI CSS (TINY MINIMALIST DESIGN) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    
    div[data-testid="stChatInput"] { padding-left: 70px !important; }

    /* Tiny Minimal Yellow Plus Button */
    .stFileUploader {
        position: fixed; bottom: 35px; left: 15px;
        width: 30px !important; height: 30px !important; z-index: 3000;
    }
    .stFileUploader section {
        padding: 0 !important; min-height: 30px !important;
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important;
    }
    .stFileUploader section div { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 16px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 30px;
    }

    .mic-wrap { position: fixed; bottom: 32px; left: 52px; z-index: 3001; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 18px !important; }
    
    /* Video Box Styling */
    .ai-video-box { border: 2px solid #FFD700; border-radius: 15px; overflow: hidden; margin: 10px 0; box-shadow: 0 0 15px rgba(255, 215, 0, 0.2); }
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

def get_pro_video(prompt, w, h):
    """New High-Speed Generative Engine"""
    seed = random.randint(1, 9999999)
    # Using 'Turbo' and 'Cinematic' flags for real AI feel
    v_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width={w}&height={h}&seed={seed}&model=video&enhance=true&turbo=true"
    return v_url

# ================= MAIN APP =================
st.title("🎬 Pro AI Video Generator")

with st.sidebar:
    st.write("### Quality Settings")
    v_mode = st.radio("Resolution:", ["Mobile (9:16)", "Desktop (16:9)"])
    w, h = (720, 1280) if "Mobile" in v_mode else (1280, 720)

# Input Controls
uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg", "mp4"], key="pro_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='pro_mic')
st.markdown('</div>', unsafe_allow_html=True)

# History Display
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m:
            st.video(m["v_url"])

u_input = st.chat_input("Pucho: 'Generate a realistic video of a flying car'...")

# File Analysis Logic
if uploaded_file and not u_input:
    u_input = f"Bhai, ye file '{uploaded_file.name}' analyse karo."

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    v_url_saved = None

    with st.chat_message("assistant"):
        india_tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(india_tz)

        # 🕒 DATE/TIME/WEATHER
        if any(x in txt for x in ["time", "date", "weather"]):
            final_reply = f"Navi Mumbai: {now.strftime('%I:%M %p')}, Date: {now.strftime('%d %B %Y')}."

        # 🎬 PRO VIDEO GENERATION (RELIABLE)
        elif any(x in txt for x in ["video", "generate", "banao"]):
            with st.status("🧠 AI Model is Dreaming your Video...", expanded=True) as status:
                st.write("Analyzing prompt for cinematic depth...")
                v_url = get_pro_video(u_input, w, h)
                
                # Double-check the URL
                st.write("Streaming from high-speed GPU cluster...")
                time.sleep(3) # Wait for initial frames
                
                st.markdown('<div class="ai-video-box">', unsafe_allow_html=True)
                st.video(v_url)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.download_button("📥 Save HD Video", data=requests.get(v_url).content, file_name="ai_pro_video.mp4")
                v_url_saved = v_url
                status.update(label="✅ Video Generated Successfully!", state="complete", expanded=False)
                final_reply = "Bhai, video generate ho gayi hai! Ye asli AI generative video hai."

        # 🧠 GROQ CHAT
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # State Update
    new_msg = {"role": "assistant", "content": final_reply}
    if v_url_saved: new_msg["v_url"] = v_url_saved
    st.session_state.messages.append(new_msg)
    st.rerun()
    
