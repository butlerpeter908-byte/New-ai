import streamlit as st
from groq import Groq
import requests
import random
from gtts import gTTS
import os
import base64
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
# Groq handles the brain (Chat)
GROQ_KEY = "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"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq Connection Error!")

# Page configuration
st.set_page_config(page_title="Pro Talking AI v2", layout="wide")

# ================= MODERN UI CSS =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 1rem; background-color: #0E1117;}
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
    .stFileUploader label, .stFileUploader small { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 24px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 100%;
    }
    
    /* Mic Button Style */
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= AI ENGINES =================

def generate_video_url(prompt):
    """Generates a dynamic video based on user prompt using Pollinations."""
    seed = random.randint(1, 100000)
    # Prompt ko URL friendly banana
    clean_prompt = prompt.replace(" ", "%20")
    # Ye user ke prompt se nayi video create karta hai
    video_url = f"https://pollinations.ai/p/{clean_prompt}?width=1024&height=1024&seed={seed}&model=video"
    return video_url

def text_to_speech_autoplay(text):
    """Converts AI text to speech and plays it automatically."""
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            # Autoplay HTML tag
            md = f"""
                <audio autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Voice Error: {e}")

# ================= MAIN APP FLOW =================
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🚀 Pro Talking AI (Full Features)")

# Sidebar/Icons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="pro_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='pro_mic')
st.markdown('</div>', unsafe_allow_html=True)

# Display History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# User Input
u_input = st.chat_input("Prompt: 'Show a bottle talking about health benefits'")

if u_input:
    # User message save
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"):
        st.markdown(u_input)

    with st.chat_message("assistant"):
        # 🎬 Step 1: Video Generation (User ke prompt ke hisab se)
        with st.spinner("🎬 Creating your custom video..."):
            v_url = generate_video_url(u_input)
            st.video(v_url) # Pollinations creates it on the fly

        # 💬 Step 2: Groq Response (Brain)
        full_res = ""
        box = st.empty()
        
        with st.spinner("🧠 Thinking..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": u_input}],
                stream=False
            )
            full_res = completion.choices[0].message.content
            box.markdown(full_res)
        
        # 🎙️ Step 3: Voice Generation (Jo likha hai wahi bolega)
        with st.spinner("🎙️ Speaking..."):
            text_to_speech_autoplay(full_res)
        
        # Assistant message save
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        
