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

st.set_page_config(page_title="AI Video Live Fix", layout="wide")

if "messages" not in st.session_state: st.session_state.messages = []

# ================= UI CSS (TINY MINIMAL) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    
    div[data-testid="stChatInput"] { padding-left: 75px !important; }

    .stFileUploader {
        position: fixed; bottom: 35px; left: 15px;
        width: 28px !important; height: 28px !important; z-index: 3000;
    }
    .stFileUploader section {
        padding: 0 !important; min-height: 28px !important;
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important;
    }
    .stFileUploader section div { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 14px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 28px;
    }

    .mic-wrap { position: fixed; bottom: 34px; left: 50px; z-index: 3001; }
    .mic-wrap button { background-color: transparent !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================

def speak(text):
    try:
        tts = gTTS(text=text, lang='hi', slow=False)
        tts.save("msg.mp3")
        with open("msg.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

# ================= MAIN APP =================
st.title("🤖 Pro AI: Fast Video Engine")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

# Buttons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="live_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='live_mic')
st.markdown('</div>', unsafe_allow_html=True)

u_input = st.chat_input("Prompt: 'Red car racing'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    v_link_save = None

    with st.chat_message("assistant"):
        if any(x in txt for x in ["video", "generate", "banao"]):
            st.write("🎬 **AI is rendering...** Video niche load ho rahi hai.")
            seed = random.randint(1, 99999)
            # Live Stream URL (No waiting in code)
            v_url = f"https://pollinations.ai/p/{u_input.replace(' ', '%20')}?width=720&height=1280&seed={seed}&model=video"
            
            st.video(v_url)
            st.markdown(f"🔗 [Direct Video Link]({v_url})")
            v_link_save = v_url
            final_reply = "Bhai, video load ho rahi hai. Agar screen black dikhe toh 5-10 second wait karna, server piche render kar raha hai."
        
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # Save and Stay
    msg_data = {"role": "assistant", "content": final_reply}
    if v_link_save: msg_data["v_url"] = v_link_save
    st.session_state.messages.append(msg_data)
    st.rerun()
    
