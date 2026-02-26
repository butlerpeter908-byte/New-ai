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

st.set_page_config(page_title="Pro AI Fixed Storage", layout="wide")

# ================= SESSION STATE (STORAGE) =================
# Ye section video aur chat ko delete hone se rokta hai
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_video" not in st.session_state:
    st.session_state.last_video = None
if "video_bytes" not in st.session_state:
    st.session_state.video_bytes = None

# ================= MODERN UI CSS =================
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
    
    .video-container { border: 2px solid #FFD700; border-radius: 15px; padding: 10px; margin: 10px 0; background: #1a1a1a; }
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

@st.cache_data(show_spinner=False)
def download_video_data(url):
    try:
        r = requests.get(url, timeout=40)
        if r.status_code == 200:
            return r.content
    except: return None
    return None

# ================= MAIN APP =================
st.title("🤖 Pro AI: Non-Stop Video Chat")

# Size Settings
with st.sidebar:
    st.header("Settings")
    size = st.radio("Video Size:", ["Mobile", "Desktop"])
    w, h = (720, 1280) if size == "Mobile" else (1280, 720)

# Buttons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="final_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='final_mic')
st.markdown('</div>', unsafe_allow_html=True)

# 1. PEHLE PURANI CHAT AUR VIDEO DIKHAO (Taaki delete na ho)
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if "video_url" in m:
            st.video(m["video_url"])

# 2. USER INPUT
u_input = st.chat_input("Prompt: 'Show me a futuristic Navi Mumbai'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    txt = u_input.lower()
    final_reply = ""
    v_url_to_save = None

    with st.chat_message("assistant"):
        india_tz = pytz.timezone('Asia/Kolkata')
        now_india = datetime.now(india_tz)

        # LOGIC: TIME/DATE/WEATHER
        if any(x in txt for x in ["date", "time", "weather", "mausam"]):
            if "date" in txt: final_reply = f"Bhai, aaj ki date hai: {now_india.strftime('%d %B %Y')}"
            elif "time" in txt: final_reply = f"Navi Mumbai ka time: {now_india.strftime('%I:%M %p')}"
            else: final_reply = "Navi Mumbai mein mausam mast 29°C hai!"
        
        # LOGIC: VIDEO GENERATION
        elif any(x in txt for x in ["video", "generate", "banao"]):
            with st.spinner("🎬 AI Video bana raha hai... (Thoda sabr rakhein)"):
                seed = random.randint(1, 999999)
                clean_p = u_input.replace(" ", "%20")
                v_url = f"https://pollinations.ai/p/{clean_p}?width={w}&height={h}&seed={seed}&model=video"
                
                # Check if video is ready
                video_bytes = download_video_data(v_url)
                if video_bytes:
                    st.video(video_bytes)
                    st.download_button("📥 Download Video", data=video_bytes, file_name="ai_video.mp4")
                    v_url_to_save = video_bytes # Bytes save karenge taaki refresh pe delete na ho
                    final_reply = "Bhai, video taiyar hai! Ye delete nahi hogi."
                else:
                    final_reply = "Bhai, server thoda slow hai, video load nahi ho payi. Dobara try karo!"
        
        # LOGIC: CHAT
        else:
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": u_input}])
            final_reply = res.choices[0].message.content
        
        st.write(final_reply)
        speak(final_reply)

    # Message ko storage mein save karo
    new_msg = {"role": "assistant", "content": final_reply}
    if v_url_to_save:
        new_msg["video_url"] = v_url_to_save
    st.session_state.messages.append(new_msg)
    st.rerun() # Refresh taaki UI update ho jaye
