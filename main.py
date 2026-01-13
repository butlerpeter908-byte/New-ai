import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz 
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("❌ API Key Missing! Please add GROQ_API_KEY in Streamlit Secrets.")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= CSS: MIC SHIFTED TO BOTTOM-MOST =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 2rem;}
    
    /* Input Box space for Mic */
    div[data-testid="stChatInput"] { 
        margin-left: 60px !important; 
        z-index: 1000;
    }

    /* Mic Icon: Shifted further DOWN (10px from bottom) */
    .mic-fixed-container { 
        position: fixed; 
        bottom: 10px; /* Pehle 35px tha, ab aur niche kar diya */
        left: 15px; 
        z-index: 9999 !important; 
    }

    .mic-fixed-container button {
        background-color: #FF4B4B !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        border: 2px solid white !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.4) !important;
        font-size: 20px !important;
    }

    .menu-card { 
        background-color: #121212; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #FF4B4B; 
        margin-bottom: 20px; 
    }
    </style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "messages" not in st.session_state: 
    st.session_state.messages = []
if "last_audio_id" not in st.session_state: 
    st.session_state.last_audio_id = None
if "last_audio_content" not in st.session_state: 
    st.session_state.last_audio_content = None
if "show_menu" not in st.session_state: 
    st.session_state.show_menu = False

st.title("🚀 Pro AI")

# ================= MENU SECTION (ENGLISH) =================
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📖 About Pro AI")
    st.info("**Pro AI** is a professional assistant using Whisper (Voice) and Llama 3.3 (Brain) technology.")
    st.subheader("🔒 Privacy Policy")
    st.write("No data storage. Conversations are session-based and private.")
    st.subheader("⚖️ Terms & Conditions")
    st.write("Use ethically. Verify critical AI-generated information.")
    st.divider()
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.last_audio_content = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ================= DISPLAY CHAT =================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ================= MIC WITH VOICE WAVE ICON & BOTTOM SHIFT =================
st.markdown('<div class="mic-fixed-container">', unsafe_allow_html=True)
# start_prompt mein mic aur sound wave ka feel diya hai
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🌊", key='pro_mic_voice_wave')
st.markdown('</div>', unsafe_allow_html=True)

u_query = st.chat_input("Ask me anything...")

# ================= VOICE LOGIC =================
if audio_data:
    if st.session_state.last_audio_id != audio_data['id']:
        st.session_state.last_audio_id = audio_data['id']
        try:
            with st.spinner("🎙️ Sun raha hoon..."):
                trans = client.audio.transcriptions.create(
                    file=("voice.wav", audio_data['bytes']),
                    model="whisper-large-v3",
                    response_format="text"
                )
                if trans and len(trans.strip()) > 2:
                    u_query = trans
        except:
            u_query = None

# ================= RESPONSE LOGIC =================
if u_query:
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%d %B, %Y")

    st.session_state.messages.append({"role": "user", "content": u_query})
    with st.chat_message("user"):
        st.markdown(u_query)

    try:
        with st.chat_message("assistant"):
            full_res = ""
            box = st.empty()
            
            # System instruction: No time/date unless asked
            sys_msg = (
                f"You are Pro AI. Internal Info: {current_date}, {current_time}. "
                "Respond in English. IMPORTANT: NEVER mention date or time unless the user specifically asks."
            )

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": u_query}],
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    box.markdown(full_res + "▌")
            
            box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

            # TTS
            tts = gTTS(text=full_res, lang='en', tld='com.au')
            tts.save("ans.mp3")
            with open("ans.mp3", "rb") as f:
                st.session_state.last_audio_content = f.read()
            st.rerun()

    except Exception as e:
        st.error(f"AI Error: {e}")

if st.session_state.last_audio_content:
    if st.button("🔈 Hear Response"):
        st.audio(st.session_state.last_audio_content, format="audio/mp3", autoplay=True)
        
