import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder
from datetime import datetime

# ================= API SETUP =================
GROQ_KEY = "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" 
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Universal Smart AI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI CSS =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem; background-color: #0E1117;}
    .user-bubble { background-color: #005c4b; color: white; padding: 12px 18px; border-radius: 18px 18px 0 18px; margin: 10px 0; max-width: 80%; float: right; clear: both; }
    .ai-bubble { background-color: #202c33; color: white; padding: 12px 18px; border-radius: 18px 18px 18px 0; margin: 10px 0; max-width: 80%; float: left; clear: both; border-left: 5px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

# ================= VOICE TRANSCRIPTION LOGIC =================
def process_audio(audio_data):
    if audio_data and 'bytes' in audio_data:
        try:
            # Groq Whisper API for Transcribing
            audio_file = ("temp.wav", audio_data['bytes'], "audio/wav")
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
                response_format="text"
            )
            return transcription
        except Exception as e:
            return None
    return None

def speak_auto(text):
    try:
        lang = 'hi' if any(ord(c) > 2300 for c in text) else 'en'
        tts = gTTS(text=text, lang=lang, tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

# ================= MAIN APP =================
st.title("🌍 Smart Multi-Lang AI")
now = datetime.now()
current_info = now.strftime("%A, %b %d, %Y | %I:%M %p")

# Show Chat History
for m in st.session_state.messages:
    b_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{b_class}">{m["content"]}</div>', unsafe_allow_html=True)

# --- VOICE & TEXT INPUT ---
st.markdown("---")
audio_data = mic_recorder(start_prompt="🎙️ Bolne ke liye click karein", stop_prompt="⏹️ Rokiye", key='transcribe_v1')

u_input = st.chat_input("Type here...")

# Handle Voice Input
if audio_data:
    transcribed_text = process_audio(audio_data)
    if transcribed_text:
        u_input = transcribed_text

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Today: {current_info}. Location: Navi Mumbai. Directly answer the user's question. NEVER say 'It seems you are speaking English' or identify the language. Just reply in the user's language."},
                {"role": "user", "content": u_input}
            ]
        )
        reply = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        speak_auto(reply)
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
        
