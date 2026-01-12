import streamlit as st
from groq import Groq
import datetime
import pytz
import os
from streamlit_mic_recorder import mic_recorder
from google.cloud import texttospeech

# ================= API SETUP =================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("❌ GROQ API key missing")

# Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_key.json"

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= CSS =================
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

# ================= SESSION =================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
if "voice_type" not in st.session_state:
    st.session_state.voice_type = "Male"

# ================= TITLE =================
st.title("🚀 Pro AI (Gemini Voice)")

# ================= VOICE SELECT =================
st.session_state.voice_type = st.radio(
    "🗣️ Voice Select Karein",
    ["Male", "Female"],
    horizontal=True
)

# ================= CHAT HISTORY =================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ================= MIC =================
st.markdown('<div class="mic-fixed-container">', unsafe_allow_html=True)
audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key="mic")
st.markdown('</div>', unsafe_allow_html=True)

user_query = st.chat_input("Yahan puchiye...")

# ================= VOICE TO TEXT =================
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
        st.error("❌ Voice recognition failed")

# ================= GEMINI VOICE FUNCTION =================
def gemini_voice(text, gender):
    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)

    if gender == "Male":
        voice = texttospeech.VoiceSelectionParams(
            language_code="hi-IN",
            name="hi-IN-Wavenet-B"
        )
    else:
        voice = texttospeech.VoiceSelectionParams(
            language_code="hi-IN",
            name="hi-IN-Wavenet-A"
        )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open("voice.mp3", "wb") as out:
        out.write(response.audio_content)

# ================= CHAT PROCESS =================
if user_query:
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(IST)

    st.session_state.messages.append(
        {"role": "user", "content": user_query}
    )

    with st.chat_message("user"):
        st.markdown(user_query)

    messages = [{
        "role": "user",
        "content": f"Time {now}. User: {user_query}. Reply in Hindi-English mix."
    }]

    with st.chat_message("assistant"):
        full_response = ""
        box = st.empty()

        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                box.markdown(full_response + "▌")

        box.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

        # ---- GEMINI REAL VOICE ----
        gemini_voice(full_response, st.session_state.voice_type)

        with open("voice.mp3", "rb") as f:
            st.session_state.last_audio = f.read()

        os.remove("voice.mp3")
        st.rerun()

# ================= AUDIO OUTPUT =================
if st.session_state.last_audio:
    st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
