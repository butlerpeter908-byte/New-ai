import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder
from datetime import datetime

# ================= API SETUP =================
# Aapki working key maine yahan fix kar di hai
GROQ_KEY = "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" 
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Universal Smart AI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= SMART CHAT UI (WHATSAPP LOOK) =================
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
</style>
""", unsafe_allow_html=True)

# ================= TOP OPTIONS MENU =================
with st.container():
    col1, col2 = st.columns([6, 4])
    with col2:
        menu = st.selectbox("📋 Options & Legal", ["AI Chat", "Privacy Policy", "Terms & Conditions", "Clear Chat"])
        if menu == "Privacy Policy":
            st.info("### 🔒 Privacy: Your data is session-based and encrypted.")
        elif menu == "Terms & Conditions":
            st.warning("### ⚖️ Terms: No illegal content. AI speed powered by Groq.")
        elif menu == "Clear Chat":
            if st.button("Confirm Reset"):
                st.session_state.messages = []
                st.rerun()

# ================= VOICE ENGINE =================
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

# ================= MAIN CHAT AREA =================
st.title("🌍 Smart Global AI")

# Real-Time Info
now = datetime.now()
current_info = f"Today is {now.strftime('%A, %b %d, %Y')}. Local Time: {now.strftime('%I:%M %p')}. Location: Navi Mumbai."

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for m in st.session_state.messages:
    b_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{b_class}">{m["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- INPUT ---
st.markdown("---")
mic_recorder(start_prompt="🎙️ Voice", stop_prompt="⏹️ Send", key='smart_v30')
u_input = st.chat_input("Puchiye: Time, Weather, ya kuch bhi...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Context: {current_info}. Identify user language (Hindi/English/Hinglish). Be super fast. No code output."},
                {"role": "user", "content": u_input}
            ]
        )
        reply = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        speak_auto(reply)
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
        
