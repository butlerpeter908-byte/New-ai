import streamlit as st
from groq import Groq
import requests
import random
from gtts import gTTS
import base64

# ================= SETTINGS =================
GROQ_KEY = "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"
PEXELS_KEY = "53301252102819537432009265263651"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Final AI Fix", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI (TINY BUTTON) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; background-color: #0E1117;}
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
    </style>
""", unsafe_allow_html=True)

# ================= LOGIC =================
def get_video(query):
    # Pehle Pexels check karo (Stable)
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        if data['videos']:
            return data['videos'][0]['video_files'][0]['link']
    except: pass
    # Backup Pollinations
    seed = random.randint(1, 9999)
    return f"https://pollinations.ai/p/{query.replace(' ', '%20')}?width=720&height=1280&seed={seed}&model=video"

# ================= APP =================
st.title("🎬 High-Speed AI Video")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

st.file_uploader("", type=["png", "jpg", "mp4"], key="f_up")
u_input = st.chat_input("Prompt: 'Red car racing'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    with st.chat_message("assistant"):
        if any(x in u_input.lower() for x in ["video", "banao", "generate"]):
            with st.spinner("Video load ho rahi hai..."):
                v_url = get_video(u_input)
                st.video(v_url)
                st.session_state.messages.append({"role": "assistant", "content": "Bhai, video taiyar hai!", "v_url": v_url})
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            reply = res.choices[0].message.content
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
