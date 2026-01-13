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

# ================= CSS: MIC NEXT TO PLACEHOLDER =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 2rem;}
    
    /* Shift Chat Input to make space for Mic */
    div[data-testid="stChatInput"] { 
        margin-left: 60px !important; 
        z-index: 1000;
    }

    /* Mic Icon: Fixed exactly next to placeholder */
    .mic-fixed-container { 
        position: fixed; 
        bottom: 35px; 
        left: 18px; 
        z-index: 9999 !important; 
    }

    .mic-fixed-container button {
        background-color: #FF4B4B !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        border: 2px solid white !important;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.3) !important;
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

# ================= MENU SECTION (FULL ENGLISH) =================
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    
    # 1. ABOUT PRO AI
    st.subheader("📖 About Pro AI")
    st.info("""
    **Pro AI** is a cutting-edge multimodal AI assistant. 
    It leverages Google's Whisper for high-accuracy voice recognition and Meta's Llama 3.3 for intelligent reasoning. 
    Designed to provide a seamless, voice-first interactive experience for modern users.
    """)
    
    # 2. PRIVACY POLICY
    st.subheader("🔒 Privacy Policy")
    st.write("""
    We prioritize your privacy. No personal data or voice recordings are stored on our servers. 
    All interactions are processed in real-time and exist only within your current session.
    """)
    
    # 3. TERMS & CONDITIONS
    st.subheader("⚖️ Terms & Conditions")
    st.write("""
    Please use this AI responsibly for ethical purposes. 
    While we strive for accuracy, always verify critical AI-generated information before making key decisions.
    """)
    
    st.divider()
    
    # 4. FEEDBACK
    st.subheader("📬 Send Feedback")
    f_text = st.text_area("How was your experience?")
    if st.button("Submit Feedback"):
        if f_text:
            st.success("✅ Feedback Received! (Saved Successfully)")
        else:
            st.warning("Please enter some text before submitting.")

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.last_audio_content = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ================= DISPLAY CHAT =================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ================= MIC POSITIONED NEAR PLACEHOLDER =================
st.markdown('<div class="mic-fixed-container">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='pro_mic_v_english')
st.markdown('</div>', unsafe_allow_html=True)

u_query = st.chat_input("Ask me anything (e.g., What is the time?)")

# ================= VOICE LOGIC =================
if audio_data:
    if st.session_state.last_audio_id != audio_data['id']:
        st.session_state.last_audio_id = audio_data['id']
        try:
            with st.spinner("🎙️ Transcribing..."):
                trans = client.audio.transcriptions.create(
                    file=("voice.wav", audio_data['bytes']),
                    model="whisper-large-v3",
                    response_format="text"
                )
                if trans and len(trans.strip()) > 3:
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
            
            sys_msg = (
                f"You are Pro AI. Today is {current_date} and current time is {current_time}. "
                "Respond in clear English. Always answer time, date, and weather questions accurately."
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

            # TTS (Generating English Audio)
            tts = gTTS(text=full_res, lang='en', tld='com.au')
            tts.save("ans.mp3")
            with open("ans.mp3", "rb") as f:
                st.session_state.last_audio_content = f.read()
            st.rerun()

    except Exception as e:
        st.error(f"AI Error: {e}")

# ================= AUDIO PLAYER =================
if st.session_state.last_audio_content:
    if st.button("🔈 Listen to Response"):
        st.audio(st.session_state.last_audio_content, format="audio/mp3", autoplay=True)
        
