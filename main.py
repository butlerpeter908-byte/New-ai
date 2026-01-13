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
    st.error("❌ API Key Missing!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= CSS: STERN WHITE LINE REMOVAL =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    
    .block-container {padding-bottom: 160px; padding-top: 2rem;}
    
    /* Strict removal of the white line / border-top */
    hr {border: none !important; display: none !important;}
    div.stChatFloatingInputContainer {
        border-top: none !important; 
        box-shadow: none !important;
        background-color: transparent !important;
    }
    
    div[data-testid="stChatInput"] { 
        margin-left: 65px !important; 
        z-index: 1000; 
        border: none !important;
        background-color: #1A1A1A !important;
    }

    .mic-fixed-container { 
        position: fixed; 
        bottom: 10px; 
        left: 15px; 
        z-index: 9999 !important; 
    }

    .mic-fixed-container button {
        background-color: #FF4B4B !important;
        border-radius: 50% !important;
        width: 52px !important; 
        height: 52px !important;
        border: 2px solid white !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5) !important;
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
if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None
if "last_audio_content" not in st.session_state: st.session_state.last_audio_content = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False

st.title("🚀 Pro AI")

# ================= MENU SECTION (NO CHANGES) =================
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📖 About Pro AI")
    st.info("Pro AI is a professional multimodal assistant using Whisper V3 and Llama 3.3.")
    st.subheader("🔒 Privacy Policy")
    st.write("Your conversations are private. We do not store any voice or text data.")
    st.subheader("⚖️ Terms & Conditions")
    st.write("Use ethically. Verify critical information independently.")
    st.divider()
    st.subheader("📬 Send Feedback")
    f_text = st.text_area("Your feedback:", key="feedback_box")
    if st.button("Submit Feedback"):
        if f_text:
            st.toast("Thank you for your feedback!", icon="🎉")
            st.success("Thank you for your feedback!")
    st.divider()
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.last_audio_content = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ================= MIC DISPLAY =================
st.markdown('<div class="mic-fixed-container">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="🌊", key='final_verified_mic_v18')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me anything...")

# ================= VOICE LOGIC (UNCHANGED) =================
if audio_data:
    if st.session_state.last_audio_id != audio_data['id']:
        st.session_state.last_audio_id = audio_data['id']
        try:
            with st.spinner("🎙️ Listening..."):
                transcription = client.audio.transcriptions.create(
                    file=("voice.wav", audio_data['bytes']),
                    model="whisper-large-v3",
                    response_format="text"
                )
                if transcription and len(transcription.strip()) > 1:
                    u_input = transcription
        except: u_input = None

# ================= AI RESPONSE LOGIC =================
if u_input:
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    curr_time = now.strftime("%I:%M %p")
    curr_date = now.strftime("%d %B, %Y")
    weather_info = "The weather in Navi Mumbai is currently 28°C with clear skies."

    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    try:
        with st.chat_message("assistant"):
            full_res = ""
            box = st.empty()
            sys_msg = (
                f"You are Pro AI. Date: {curr_date}. Time: {curr_time}. Weather: {weather_info}. "
                "Respond in English. Mention time/date/weather ONLY if specifically asked for each."
            )
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": u_input}],
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    box.markdown(full_res + "▌")
            box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            tts = gTTS(text=full_res, lang='en', tld='com.au')
            tts.save("ans.mp3")
            with open("ans.mp3", "rb") as f: st.session_state.last_audio_content = f.read()
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state.last_audio_content:
    if st.button("🔈 Hear Response"):
        st.audio(st.session_state.last_audio_content, format="audio/mp3", autoplay=True)
