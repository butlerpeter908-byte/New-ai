import streamlit as st
from groq import Groq
import requests
import random
from gtts import gTTS
import os
import base64
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
PEXELS_API_KEY = "KepM3s6J4wl9TaIjAFuso1aU2wJStlw06hKNACJnRbYmh831W0r01rmi"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq Error! Key check karein.")

st.set_page_config(page_title="Pro Talking AI - All Features", layout="wide")

# ================= FULL UI CSS (WITH ALL BUTTONS) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 1rem; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }
    
    /* Yellow Plus Button */
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

    /* Mic Button */
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= UTILITY FUNCTIONS =================

def get_pexels_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['videos']:
                return random.choice(data['videos'])['video_files'][0]['link']
    except:
        return None
    return None

def text_to_speech_autoplay(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("speech.mp3")
        with open("speech.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# ================= MAIN APP FLOW =================
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🚀 Pro AI (Full Features)")

# --- SABHI BUTTONS (PLUS, MIC, FILE) ---
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="full_plus_btn")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='full_mic_btn')
st.markdown('</div>', unsafe_allow_html=True)

# History Dikhao
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input Box
u_input = st.chat_input("Prompt likho ya video maango...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"):
        st.markdown(u_input)

    with st.chat_message("assistant"):
        # 1. Groq Response (Brain)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": u_input}],
            stream=False
        )
        full_res = completion.choices[0].message.content
        st.write(full_res)
        
        # 2. Voice Sync (Bolna shuru kare)
        text_to_speech_autoplay(full_res)

        # 3. Video Handle Karo (Relatable Visual)
        if any(x in u_input.lower() for x in ["video", "dikhao", "show", "car", "nature", "bottle"]):
            with st.spinner("🎬 Searching for matching video..."):
                search_q = u_input.lower().replace("video", "").replace("show", "").strip()
                v_url = get_pexels_video(search_q if search_q else "abstract")
                if v_url:
                    st.video(v_url, loop=True)
                else:
                    st.info("Visual matching prompt not found, but I am speaking!")

        st.session_state.messages.append({"role": "assistant", "content": full_res})
        
