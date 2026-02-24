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
    st.error("❌ Groq Error!")

st.set_page_config(page_title="Pro Talking AI", layout="wide")

# ================= CSS (DARK MODE) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 1rem; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }
    
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
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= UTILITY FUNCTIONS =================

def get_pexels_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    # Sirf main keywords nikalna search ke liye
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['videos']:
                return data['videos'][0]['video_files'][0]['link']
    except:
        return None
    return None

def text_to_speech_autoplay(text):
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

# ================= MAIN APP =================
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🚀 Pro Talking AI")

# Icons Setup
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="talk_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='talk_mic')
st.markdown('</div>', unsafe_allow_html=True)

# Display History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# User Input
u_input = st.chat_input("Mujhse kuch bhi bulwao...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"):
        st.markdown(u_input)

    low_input = u_input.lower()

    with st.chat_message("assistant"):
        # 🎬 1. Video Handle Karo
        with st.spinner("🎬 Creating visual..."):
            # Simple keyword extraction for video search
            search_query = u_input.replace("video", "").replace("show", "").replace("create", "").strip()
            v_url = get_pexels_video(search_query if search_query else "abstract")
            if v_url:
                st.video(v_url, loop=True)
            else:
                st.info("Pexels par video nahi mili, par meri awaz suno!")

        # 💬 2. Chat & Voice Handle Karo
        full_res = ""
        box = st.empty()
        
        # Get AI Response from Groq
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": u_input}],
            stream=False # Voice ke liye streaming off rakhi hai taaki pura text ek sath mile
        )
        full_res = completion.choices[0].message.content
        box.markdown(full_res)
        
        # 🎙️ Generate Voice and Autoplay
        with st.spinner("🎙️ AI is speaking..."):
            text_to_speech_autoplay(full_res)
        
        st.session_state.messages.append({"role": "assistant", "content": full_res})
        
