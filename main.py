import streamlit as st
from groq import Groq
from gtts import gTTS
import os
import datetime
import pytz 
from streamlit_mic_recorder import mic_recorder

# ---------------- API KEY ----------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing! Please check Streamlit secrets.")

st.set_page_config(page_title="Pro AI", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
header, footer, .stDeployButton {visibility: hidden;}
[data-testid="stSidebar"] {display: none;}
.block-container {padding-bottom: 150px; padding-top: 2rem;}

div[data-testid="stChatInput"] { margin-left: 55px !important; }

.mic-fixed-container { 
    position: fixed; 
    bottom: 32px; 
    left: 15px; 
    z-index: 9999; 
}

.mic-fixed-container button {
    border-radius: 50%;
    width: 45px;
    height: 45px;
    background-color: #FF4B4B;
    border: 2px solid white;
}

.menu-card {
    background-color: #121212;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #FF4B4B;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None
if "show_menu" not in st.session_state:
    st.session_state.show_menu = False
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
if "voice_type" not in st.session_state:
    st.session_state.voice_type = "Male"

# ---------------- TITLE ----------------
st.title("🚀 Pro AI")

# ---------------- VOICE SELECTOR ----------------
st.session_state.voice_type = st.radio(
    "🗣️ Voice Select Karein",
    ["Male", "Female"],
    horizontal=True
)

# ---------------- MENU ----------------
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📖 About Pro AI")
    st.write("Voice based AI Assistant using LLaMA 3.3 + Whisper")
    st.subheader("🔒 Privacy Policy")
    st.write("We do not store user data.")
    st.subheader("⚖️ Terms")
    st.write("AI responses may not be 100% accurate.")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- MIC BUTTON ----------------
st.markdown('<div class="mic-fixed-container">', unsafe_allow_html=True)
audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key="mic")
st.markdown('</div>', unsafe_allow_html=True)

user_query = st.chat_input("Yahan puchiye...")

# ---------------- VOICE INPUT ----------------
if audio and st.session_state.last_audio_id != audio["id"]:
    st.session_state.last_audio_id = audio["id"]
    try:
        trans = client.audio.transcriptions.create(
            file=("audio.wav", audio["bytes"]),
            model="whisper-large-v3",
            response_format="text"
        )
        user_query = trans
    except:
        st.error("Voice input failed")

# ---------------- CHAT PROCESS ----------------
if user_query:
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(IST)
    timestamp = now.strftime("%I:%M %p | %d-%m-%Y")

    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )

    with st.chat_message("user"):
        st.markdown(user_query)

    messages = [{
        "role": "user",
        "content": f"Time: {timestamp}. User said: {user_query}. Reply in Hindi-English mix."
    }]

    with st.chat_message("assistant"):
        response_text = ""
        box = st.empty()

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                box.markdown(response_text + "▌")

        box.markdown(response_text)
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )

        # ---------------- MALE / FEMALE VOICE ----------------
        if st.session_state.voice_type == "Male":
            tts = gTTS(
                text=response_text,
                lang="hi",
                tld="co.in",
                slow=False
            )
        else:
            tts = gTTS(
                text=response_text,
                lang="hi",
                tld="com.au",
                slow=False
            )

        tts.save("voice.mp3")

        with open("voice.mp3", "rb") as f:
            st.session_state.last_audio = f.read()

        os.remove("voice.mp3")
        st.rerun()

# ---------------- AUDIO PLAY ----------------
if st.session_state.last_audio:
    if st.button("🔈 Jawab Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
