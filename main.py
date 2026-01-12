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

# Google Cloud credentials (Ensure this file is in your repo)
if os.path.exists("google_key.json"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_key.json"
else:
    st.warning("⚠️ google_key.json missing! Voice synthesis might fail.")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= CSS (Fixed Layout) =================
st.markdown("""
<style>
header, footer, .stDeployButton {visibility: hidden;}
[data-testid="stSidebar"] {display: none;}
.block-container {padding-bottom: 150px; padding-top: 2rem;}
div[data-testid="stChatInput"] { margin-left: 60px !important; }

/* Mic Button Fixed at Left Corner */
.mic-fixed-container {
    position: fixed;
    bottom: 32px;
    left: 15px;
    z-index: 9999;
}
.mic-fixed-container button {
    border-radius: 50% !important;
    width: 48px !important;
    height: 48px !important;
    background-color: #FF4B4B !important;
    border: 2px solid white !important;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
if "voice_type" not in st.session_state:
    st.session_state.voice_type = "Male"

st.title("🚀 Pro AI (Gemini Voice)")

# Voice Select (Top bar)
st.session_state.voice_type = st.radio(
    "🗣️ Voice Select:",
    ["Male", "Female"],
    horizontal=True,
    index=0 if st.session_state.voice_type == "Male" else 1
)

# ================= CHAT HISTORY =================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ================= PERMANENT MIC & INPUT =================
st.markdown('<div class="mic-fixed-container">', unsafe_allow_html=True)
audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key="permanent_mic")
st.markdown('</div>', unsafe_allow_html=True)

# Important: user_query ko reset hone se bachane ke liye handle karna
query_text = st.chat_input("Yahan puchiye...")

# Voice to Text Logic
if audio and st.session_state.last_audio_id != audio["id"]:
    st.session_state.last_audio_id = audio["id"]
    try:
        with st.spinner("Sun raha hoon..."):
            trans = client.audio.transcriptions.create(
                file=("audio.wav", audio["bytes"]),
                model="whisper-large-v3",
                response_format="text"
            )
            query_text = trans
    except Exception as e:
        st.error(f"❌ Voice recognition failed: {e}")

# ================= GEMINI VOICE FUNCTION =================
def gemini_voice(text, gender):
    try:
        tts_client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Hindi (India) Voices
        voice_name = "hi-IN-Wavenet-B" if gender == "Male" else "hi-IN-Wavenet-A"
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="hi-IN",
            name=voice_name
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=0.0,
            speaking_rate=1.0
        )

        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        return response.audio_content
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# ================= CHAT PROCESS =================
if query_text:
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(IST)

    st.session_state.messages.append({"role": "user", "content": query_text})
    with st.chat_message("user"):
        st.markdown(query_text)

    try:
        with st.chat_message("assistant"):
            full_response = ""
            box = st.empty()

            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"User: {query_text}. Reply in Hindi-English mix."}],
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    box.markdown(full_res := full_response + "▌")

            box.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Voice Generation
            with st.spinner("Generating Voice..."):
                audio_content = gemini_voice(full_response, st.session_state.voice_type)
                if audio_content:
                    st.session_state.last_audio = audio_content
            
            st.rerun()
    except Exception as e:
        st.error(f"API Error: {e}")

# ================= AUDIO OUTPUT =================
if st.session_state.last_audio:
    st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
    
