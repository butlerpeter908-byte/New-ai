import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from datetime import datetime

# ================= API SETUP =================
GROQ_KEY = "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" 
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Universal Smart AI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI CSS (WHATSAPP BUBBLES) =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem; background-color: #0E1117;}
    
    /* User: Right Side */
    .user-bubble {
        background-color: #005c4b; color: white;
        padding: 12px 18px; border-radius: 18px 18px 0 18px;
        margin: 10px 0; max-width: 80%; float: right; clear: both;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    
    /* AI: Left Side */
    .ai-bubble {
        background-color: #202c33; color: white;
        padding: 12px 18px; border-radius: 18px 18px 18px 0;
        margin: 10px 0; max-width: 80%; float: left; clear: both;
        border-left: 5px solid #FFD700;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .chat-container { width: 100%; overflow: hidden; }
    .stButton>button { border-radius: 20px; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# ================= VOICE LOGIC (Manual Click) =================
def get_audio_html(text):
    try:
        lang = 'hi' if any(ord(c) > 2300 for c in text) else 'en'
        tts = gTTS(text=text, lang=lang, tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        return f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>'
    except: return ""

# ================= MAIN APP =================
st.title("🌍 Smart Multi-Lang AI")

# Real-time Context
now = datetime.now()
current_info = f"Date: {now.strftime('%A, %b %d, %Y')} | Time: {now.strftime('%I:%M %p')}"

# Display Chat History
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for i, m in enumerate(st.session_state.messages):
    b_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{b_class}">{m["content"]}</div>', unsafe_allow_html=True)
    
    # Listen Button only for AI messages
    if m["role"] == "assistant":
        if st.button(f"🔊 Listen", key=f"voice_btn_{i}"):
            audio_html = get_audio_html(m["content"])
            st.markdown(audio_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- TEXT INPUT ONLY ---
st.markdown("---")
u_input = st.chat_input("Apna sawal yahan type karein...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    
    try:
        # AI Response
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Context: {current_info}, Location: Navi Mumbai. Directly answer the question in user's language. Never output code or 'It seems you are speaking English'."},
                {"role": "user", "content": u_input}
            ]
        )
        reply = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
        
