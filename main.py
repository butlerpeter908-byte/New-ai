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
PEXELS_KEY = "53301252102819537432009265263651"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="AI Video Final Fix", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI CSS (TINY YELLOW BUTTON) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 60px !important; }
    .stFileUploader {
        position: fixed; bottom: 35px; left: 10px;
        width: 32px !important; height: 32px !important; z-index: 3000;
    }
    .stFileUploader section {
        padding: 0 !important; min-height: 32px !important;
        background-color: #FFD700 !important; border-radius: 50% !important; border: none !important;
    }
    .stFileUploader section div { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 18px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 32px;
    }
    .mic-wrap { position: fixed; bottom: 34px; left: 48px; z-index: 3001; }
    .mic-wrap button { background-color: transparent !important; border: none !important; transform: scale(0.8); }
    </style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================
def speak(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("msg.mp3")
        with open("msg.mp3", "rb") as f:
            b64 = base64.decode(f.read()).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

def get_video(query):
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        if data['videos']: return data['videos'][0]['video_files'][0]['link']
    except: pass
    seed = random.randint(1, 9999)
    return f"https://pollinations.ai/p/{query.replace(' ', '%20')}?width=720&height=1280&seed={seed}&model=video"

# ================= MAIN APP =================
st.title("🤖 Pro AI Video Engine")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="final_v")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='mic_final')
st.markdown('</div>', unsafe_allow_html=True)

u_input = st.chat_input("Prompt likho...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    with st.chat_message("assistant"):
        if any(x in u_input.lower() for x in ["video", "banao"]):
            v_url = get_video(u_input)
            st.video(v_url)
            st.session_state.messages.append({"role": "assistant", "content": "Bhai, video ready hai!", "v_url": v_url})
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            reply = res.choices[0].message.content
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
    
