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
# Aapki Pollinations API Key yahan paste kar di hai
POLLINATIONS_KEY = "sk_GDjUvkvbbvb1sh8DNRObVhIuaB3x3wsD"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Pro Generative AI", layout="wide")

# ================= MODERN UI CSS =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }
    
    /* Plus Button Style */
    .stFileUploader {
        position: fixed; bottom: 32px; left: 20px;
        width: 40px !important; height: 40px !important; z-index: 2005;
    }
    .stFileUploader section {
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important; width: 40px !important; height: 40px !important;
    }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 24px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 100%;
    }

    /* Mic Button Style */
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; }
    
    /* Settings Box */
    .settings-box { background: #1E1E1E; padding: 10px; border-radius: 10px; border: 1px solid #FFD700; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ================= CORE FUNCTIONS =================

def speak(text):
    """Hindi/English Voice Autoplay"""
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("msg.mp3")
        with open("msg.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

def generate_ai_video(prompt, width, height):
    """Real Generative Video using Pollinations API"""
    seed = random.randint(1, 999999)
    clean_prompt = prompt.replace(" ", "%20")
    # Pollinations generative model
    v_url = f"https://pollinations.ai/p/{clean_prompt}?width={width}&height={height}&seed={seed}&model=video"
    return v_url

# ================= MAIN APP FLOW =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🤖 Pro Generative AI")

# --- VIDEO SIZE SETTINGS ---
with st.expander("🎬 Video Size & Format Settings"):
    size_choice = st.radio("Download Format Chunien:", ["Mobile (9:16)", "Desktop (16:9)", "Square (1:1)"], horizontal=True)
    dim_map = {"Mobile (9:16)": (720, 1280), "Desktop (16:9)": (1280, 720), "Square (1:1)": (1024, 1024)}
    target_w, target_h = dim_map[size_choice]

# Sidebar Icons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="ultra_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='ultra_mic')
st.markdown('</div>', unsafe_allow_html=True)

# Show History
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Prompt: 'Cyberpunk Navi Mumbai street in rain'")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""

    with st.chat_message("assistant"):
        india_tz = pytz.timezone('Asia/Kolkata')
        now_india = datetime.now(india_tz)

        # 🕒 1. DATE, TIME, WEATHER (INDIA/NAVI MUMBAI)
        if any(x in txt for x in ["date", "time", "weather", "tarikh", "mausam"]):
            if "date" in txt or "tarikh" in txt:
                final_reply = f"Bhai, aaj ki tarikh hai {now_india.strftime('%d %B %Y')}."
            elif "time" in txt or "samay" in txt:
                final_reply = f"Navi Mumbai mein abhi ka samay hai: {now_india.strftime('%I:%M %p')}."
            else:
                final_reply = "Bhai, Navi Mumbai ka mausam filhal ekdam mast hai, temperature 29°C ke aas-paas hai."
        
        # 🎬 2. REAL GENERATIVE VIDEO
        elif any(x in txt for x in ["video", "generate", "banao"]):
            with st.spinner("✨ AI is dreaming your video..."):
                video_url = generate_ai_video(u_input, target_w, target_h)
                st.video(video_url)
                # Download Button with specific size info
                st.markdown(f"### [📥 Click to Download {size_choice} Video]({video_url})")
                final_reply = f"Bhai, maine aapki command par ek nayi {size_choice} video generate kar di hai. Aap ise niche link se download kar sakte ho."

        # 🧠 3. CHAT LOGIC
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    st.session_state.messages.append({"role": "assistant", "content": final_reply})
