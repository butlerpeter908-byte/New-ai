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
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Pro Generative AI", layout="wide")

# ================= UI CSS =================
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

def generate_ai_video(prompt, width, height):
    """Real AI Video Generation (Pollinations)"""
    seed = random.randint(1, 99999)
    clean_p = prompt.replace(" ", "%20")
    # Ye URL naya video generate karta hai, purana uthata nahi
    v_url = f"https://pollinations.ai/p/{clean_p}?width={width}&height={height}&seed={seed}&model=video"
    return v_url

# ================= MAIN APP =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🤖 Real Generative AI")

# --- SETTINGS FOR DOWNLOAD SIZE ---
with st.expander("⚙️ Video Settings (Size Select)"):
    size_option = st.selectbox("Download Size Chunien:", ["Mobile (Vertical)", "Desktop (Widescreen)", "Square"])
    dim = {"Mobile (Vertical)": (720, 1280), "Desktop (Widescreen)": (1280, 720), "Square": (1024, 1024)}
    w, h = dim[size_option]

# Buttons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="gen_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='gen_mic')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Prompt: 'A glowing futuristic car driving in Navi Mumbai'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""

    with st.chat_message("assistant"):
        india_tz = pytz.timezone('Asia/Kolkata')
        now_india = datetime.now(india_tz)

        # 1. TIME/DATE/WEATHER LOGIC
        if any(x in txt for x in ["date", "time", "weather"]):
            if "date" in txt: final_reply = f"Aaj ki tarikh: {now_india.strftime('%d %B %Y')}"
            elif "time" in txt: final_reply = f"Time: {now_india.strftime('%I:%M %p')}"
            else: final_reply = "Navi Mumbai ka mausam mast 29°C hai!"
        
        # 2. REAL VIDEO GENERATION (NOT SEARCH)
        elif any(x in txt for x in ["video", "generate", "banao"]):
            with st.spinner("🧠 AI is creating a NEW video for you..."):
                v_url = generate_ai_video(u_input, w, h)
                st.video(v_url)
                # Download link
                st.markdown(f'[📥 Download {size_option} Video]({v_url})')
                final_reply = f"Bhai, maine aapke liye ek nayi {size_option} video generate ki hai!"

        # 3. CHAT
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    
