import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import requests
from datetime import datetime # Live Time/Date ke liye

# API Key check
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing!")

st.set_page_config(page_title="Pro AI", layout="wide")

# --- CSS: FIXED LOOK ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px;}

    /* Menu Button 1cm Up */
    div.stButton > button:first-child { 
        margin-top: -40px !important; 
        background-color: #FF4B4B !important;
        color: white !important;
    }

    /* Plus Icon Positioning */
    div[data-testid="stChatInput"] { margin-left: 60px !important; }
    
    .plus-icon-container {
        position: fixed; bottom: 32px; left: 15px;
        background-color: #FF4B4B; color: white;
        border-radius: 50%; width: 45px; height: 45px;
        display: flex; align-items: center; justify-content: center;
        font-size: 30px; font-weight: bold; z-index: 1000;
        border: 2px solid white;
    }

    div[data-testid="stFileUploader"] {
        position: fixed; bottom: 32px; left: 15px;
        width: 45px; height: 45px; opacity: 0; z-index: 1001;
        cursor: pointer;
    }

    .menu-card {
        background-color: #121212; padding: 20px;
        border-radius: 15px; border: 1px solid #FF4B4B;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False

st.title("🚀 Pro AI")

# --- MENU SECTION ---
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.markdown("### 📖 About, Privacy & Terms")
    st.write("Pro AI text aur photos samajhta hai. Hum aapka data save nahi karte. Ise sirf legal kaam ke liye use karein.")
    
    st.divider()
    st.markdown("### 📬 Feedback (GitHub)")
    feedback_msg = st.text_area("Hume batayein aapko app kaisa laga:")
    if st.button("Submit Feedback"):
        if feedback_msg:
            try:
                token, repo = st.secrets["GITHUB_TOKEN"], st.secrets["GITHUB_REPO"]
                url = f"https://api.github.com/repos/{repo}/issues"
                res = requests.post(url, json={"title": "Feedback", "body": feedback_msg}, headers={"Authorization": f"token {token}"})
                if res.status_code == 201: st.success("Bhej diya gaya!")
            except: st.error("GitHub Secrets check karein.")

    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT AREA ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- PLUS ICON & CHAT INPUT ---
st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Yahan puchiye..."):
    # CURRENT TIME & DATE NIKALNA
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%d %B %Y")
    day_name = now.strftime("%A")

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    try:
        # System prompt mein Time aur Date add karna
        sys_info = f"System Info: Today is {day_name}, {current_date}. Current time is {current_time}."
        content = [{"type": "text", "text": f"{sys_info}\nProfessional AI. Use full words. User: {prompt}"}]
        
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            st.image(uploaded_file, width=150)

        with st.chat_message("assistant"):
            full_res = ""
            res_box = st.empty()
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": content}], stream=True)
            for chunk in comp:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state.last_audio:
    if st.button("🔈 Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
