import streamlit as st
from groq import Groq
import requests
import random
from gtts import gTTS
import base64
from datetime import datetime
import pytz
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
POLLINATIONS_KEY = "sk_GDjUvkvbbvb1sh8DNRObVhIuaB3x3wsD"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Pro AI Ultra Fix", layout="wide")

# ================= MODERN UI CSS =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }
    
    .stFileUploader {
        position: fixed; bottom: 32px; left: 20px;
        width: 40px !important; height: 40px !important; z-index: 2005;
    }
    .stFileUploader section {
        background-color: #FFD700 !important; border-radius: 50% !important;
        width: 40px !important; height: 40px !important;
    }
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; }
    
    /* Video Container Fix */
    .video-card { border: 2px solid #FFD700; border-radius: 15px; overflow: hidden; margin-top: 10px; }
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
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

def get_binary_video(url):
    """Video file ko direct download ke liye download karein"""
    try:
        response = requests.get(url, timeout=30)
        return response.content
    except: return None

# ================= MAIN APP =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🤖 Pro AI Fix: Video & Download")

# Settings Box
with st.expander("🎬 Video Settings"):
    size_choice = st.radio("Size:", ["Mobile (9:16)", "Desktop (16:9)"], horizontal=True)
    dim_map = {"Mobile (9:16)": (720, 1280), "Desktop (16:9)": (1280, 720)}
    target_w, target_h = dim_map[size_choice]

# Buttons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="fix_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='fix_mic')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Prompt: 'Generate a dancing robot'")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""

    with st.chat_message("assistant"):
        india_tz = pytz.timezone('Asia/Kolkata')
        now_india = datetime.now(india_tz)

        # 🕒 1. DATE, TIME, WEATHER
        if any(x in txt for x in ["date", "time", "weather", "mausam"]):
            if "date" in txt: final_reply = f"Aaj ki tarikh: {now_india.strftime('%d %B %Y')}"
            elif "time" in txt: final_reply = f"Samay: {now_india.strftime('%I:%M %p')}"
            else: final_reply = "Navi Mumbai ka mausam mast 29°C hai!"
        
        # 🎬 2. VIDEO GENERATION FIX
        elif any(x in txt for x in ["video", "generate", "banao"]):
            with st.spinner("✨ AI Video taiyar ho rahi hai..."):
                seed = random.randint(1, 999999)
                clean_p = u_input.replace(" ", "%20")
                v_url = f"https://pollinations.ai/p/{clean_p}?width={target_w}&height={target_h}&seed={seed}&model=video"
                
                # Direct Video Display using HTML
                st.markdown(f'''
                    <div class="video-card">
                        <video width="100%" controls autoplay loop muted>
                            <source src="{v_url}" type="video/mp4">
                            Browser video support nahi karta.
                        </video>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Direct Download Button (No external link)
                video_data = get_binary_video(v_url)
                if video_data:
                    st.download_button(
                        label=f"📥 Download {size_choice} Video",
                        data=video_data,
                        file_name="ai_video.mp4",
                        mime="video/mp4"
                    )
                final_reply = "Bhai, video generate ho gayi hai! Aap ise yahi dekh sakte hain aur direct download bhi kar sakte hain."

        # 🧠 3. CHAT
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    
