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
PEXELS_KEY = "53301252102819537432009265263651" # High-speed Video API
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Ultimate AI Video Pro", layout="wide")

if "messages" not in st.session_state: st.session_state.messages = []

# ================= UI CSS (TINY MINIMAL YELLOW) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; background-color: #0E1117;}
    div[data-testid="stChatInput"] { padding-left: 70px !important; }

    /* Smallest Yellow Plus Button */
    .stFileUploader {
        position: fixed; bottom: 35px; left: 15px;
        width: 28px !important; height: 28px !important; z-index: 3000;
    }
    .stFileUploader section {
        padding: 0 !important; min-height: 28px !important;
        background-color: #FFD700 !important; border-radius: 50% !important; border: none !important;
    }
    .stFileUploader section div { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 16px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 28px;
    }

    .mic-wrap { position: fixed; bottom: 33px; left: 50px; z-index: 3001; }
    .mic-wrap button { background-color: transparent !important; border: none !important; }
    
    .video-card { border: 2px solid #FFD700; border-radius: 12px; margin-top: 10px; overflow: hidden; }
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

def get_hd_video(query):
    """Fetch High-Quality Generative Style Video"""
    headers = {"Authorization": PEXELS_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        if data['videos']:
            # Sabse high quality file nikalna
            video_files = data['videos'][0]['video_files']
            return video_files[0]['link']
    except: return None
    return None

# ================= MAIN APP =================
st.title("🤖 Pro AI: Real Video Engine")

# Display History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "v_url" in m: st.video(m["v_url"])

# Controls
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="pro_plus_v3")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='pro_mic_v3')
st.markdown('</div>', unsafe_allow_html=True)

u_input = st.chat_input("Prompt: 'Future Navi Mumbai city'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    v_url_to_save = None

    with st.chat_message("assistant"):
        # 1. VIDEO LOGIC (STABLE)
        if any(x in txt for x in ["video", "generate", "banao"]):
            with st.spinner("🎬 Generating Cinematic AI Video..."):
                v_url = get_hd_video(u_input)
                if v_url:
                    st.markdown('<div class="video-card">', unsafe_allow_html=True)
                    st.video(v_url)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown(f"### [📥 Download HD Video]({v_url})")
                    v_url_to_save = v_url
                    final_reply = "Bhai, video taiyar hai! Ye asli AI quality video hai jo hategi nahi."
                else:
                    final_reply = "Bhai, is topic par video nahi mil saki. Kuch aur try karo!"

        # 2. DATE/TIME/WEATHER
        elif any(x in txt for x in ["time", "date", "weather"]):
            india_tz = pytz.timezone('Asia/Kolkata')
            now = datetime.now(india_tz)
            final_reply = f"Navi Mumbai: {now.strftime('%I:%M %p')}, Date: {now.strftime('%d %B %Y')}."

        # 3. CHAT
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # Save logic
    new_msg = {"role": "assistant", "content": final_reply}
    if v_url_to_save: new_msg["v_url"] = v_url_to_save
    st.session_state.messages.append(new_msg)
    st.rerun()
                    
