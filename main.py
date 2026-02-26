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
PEXELS_KEY = "53301252102819537432009265263651"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Pro Hybrid AI", layout="wide")

# Memory management
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI CSS (CLEAN FIX) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 60px !important; }

    /* Tiny Yellow Plus Button */
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
    
    .v-box { border: 2px solid #FFD700; border-radius: 12px; overflow: hidden; margin: 10px 0; }
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

def get_pexels_video(query):
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        if data['videos']:
            return data['videos'][0]['video_files'][0]['link']
    except: return None
    return None

# ================= MAIN APP =================
st.title("🤖 Pro Hybrid Video AI")

# Display History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m:
            st.video(m["v_url"])

# Controls
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="hybrid_v5")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='mic_v5')
st.markdown('</div>', unsafe_allow_html=True)

u_input = st.chat_input("Prompt: 'Red car racing in rain'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    v_url_to_save = None

    with st.chat_message("assistant"):
        if any(x in txt for x in ["video", "generate", "banao"]):
            with st.status("🎬 Hybrid Engine: Processing...") as status:
                # Engine 1: Pexels (Fast & HD)
                st.write("Searching HD Cinematic database...")
                v_url = get_pexels_video(u_input)
                
                # Engine 2: Pollinations (Generative Backup)
                if not v_url:
                    st.write("Generating AI frames...")
                    seed = random.randint(1, 9999)
                    v_url = f"https://pollinations.ai/p/{u_input.replace(' ', '%20')}?width=720&height=1280&seed={seed}&model=video"
                
                st.markdown('<div class="v-box">', unsafe_allow_html=True)
                st.video(v_url)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown(f"### [📥 Download Video]({v_url})")
                v_url_to_save = v_url
                status.update(label="✅ Video Ready!", state="complete")
                final_reply = "Bhai, video load ho rahi hai. Ye hategi nahi aur high quality mein hai."
        
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # State Update
    new_entry = {"role": "assistant", "content": final_reply}
    if v_url_to_save: new_entry["v_url"] = v_url_to_save
    st.session_state.messages.append(new_entry)
    st.rerun()
               
