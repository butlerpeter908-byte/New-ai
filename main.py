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

st.set_page_config(page_title="AI Video Permanent Fix", layout="wide")

# --- SABSE ZAROORI: Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
# Isme hum video ka data save karenge taaki rerun pe na hate
if "current_video" not in st.session_state:
    st.session_state.current_video = None

# ================= UI CSS (TINY YELLOW BUTTON) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    
    div[data-testid="stChatInput"] { padding-left: 70px !important; }

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

def get_pro_video(prompt):
    seed = random.randint(1, 999999)
    # Fast rendering engine
    return f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=720&height=1280&seed={seed}&model=video&enhance=true"

# ================= MAIN APP =================
st.title("🎬 Persistent AI Video Chat")

# --- 1. DISPLAY HISTORY ---
# Pehle purani saari videos aur chat dikhao taaki wo delete na lage
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m:
            st.video(m["v_url"])

# UI Buttons
uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg", "mp4"], key="p_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='p_mic')
st.markdown('</div>', unsafe_allow_html=True)

# --- 2. INPUT LOGIC ---
u_input = st.chat_input("Video banao: 'Red car in rain'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    v_url_to_save = None

    with st.chat_message("assistant"):
        # VIDEO GENERATION
        if any(x in txt for x in ["video", "generate", "banao"]):
            with st.status("🎬 Video Render Ho Rahi Hai...", expanded=True) as status:
                v_url = get_pro_video(u_input)
                time.sleep(3) # Wait for processing
                st.video(v_url)
                st.download_button("📥 Save Video", data=requests.get(v_url).content, file_name="ai_video.mp4")
                v_url_to_save = v_url # Link ko variable mein rakho
                status.update(label="✅ Ready!", state="complete")
                final_reply = "Bhai, ye rahi aapki video. Ab ye chat mein save rahegi!"
        
        # NORMAL CHAT
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # --- 3. SAVE TO MEMORY ---
    new_entry = {"role": "assistant", "content": final_reply}
    if v_url_to_save:
        new_entry["v_url"] = v_url_to_save
    
    st.session_state.messages.append(new_entry)
    st.rerun() # Page ko force-update karo taaki video fix ho jaye
