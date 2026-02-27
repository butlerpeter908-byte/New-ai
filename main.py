import streamlit as st
from groq import Groq
import requests
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
PIXABAY_KEY = "48943715-64d84f88e7f1d448404a11c81"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Ultra Fast Indian AI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI & MENU =================
col1, col2 = st.columns([7, 3])
with col2:
    voice_choice = st.selectbox("🗣️ Choose Voice", ["Hindi (Indian Female)", "English (Indian Accent)"])
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ================= VOICE ENGINE (INDIAN) =================
def speak_indian(text, lang_choice):
    try:
        lang_code = 'hi' if "Hindi" in lang_choice else 'en'
        tld = 'co.in' # Indian Accent TLD
        tts = gTTS(text=text, lang=lang_code, tld=tld, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except Exception as e:
        pass

# ================= APP LOGIC =================
st.title("⚡ Ultra-Fast Indian AI")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- IMPROVED MIC ---
st.write("🎤 Tap to Speak Clear:")
audio_data = mic_recorder(start_prompt="Record Voice", stop_prompt="Stop & Send", key='pro_mic')

u_input = st.chat_input("Type or use mic above...")

# Handle Voice or Text Input
final_input = None
if audio_data:
    # Future enhancement: Add Whisper API for better transcription
    final_input = "User sent a voice message" 
if u_input:
    final_input = u_input

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"): st.markdown(final_input)
    
    with st.chat_message("assistant"):
        # FASTEST LLM CALL
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a super-fast Indian AI. Use a mix of Hinglish. Answer instantly in under 1 second. Never show code."},
                {"role": "user", "content": final_input}
            ]
        )
        reply = res.choices[0].message.content
        st.write(reply)
        speak_indian(reply, voice_choice)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
    
