import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder
from datetime import datetime

# ================= API SETUP =================
# Aapki di hui key (Check for any missing characters)
GROQ_KEY = "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" 
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Universal Smart AI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= WHATSAPP-STYLE UI =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem; background-color: #0E1117;}
    
    .user-bubble {
        background-color: #005c4b; color: white;
        padding: 12px 18px; border-radius: 18px 18px 0 18px;
        margin: 10px 0; max-width: 85%; float: right; clear: both;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    
    .ai-bubble {
        background-color: #202c33; color: white;
        padding: 12px 18px; border-radius: 18px 18px 18px 0;
        margin: 10px 0; max-width: 85%; float: left; clear: both;
        border-left: 5px solid #FFD700;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# ================= TOP MENU =================
with st.container():
    col1, col2 = st.columns([6, 4])
    with col2:
        menu = st.selectbox("📋 Options", ["AI Chat", "Clear History", "Privacy Policy", "Terms"])
        if menu == "Clear History":
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

# ================= MAIN CHAT =================
st.title("🌍 Smart Multi-Lang AI")

# Display History with Proper Alignment
for m in st.session_state.messages:
    b_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{b_class}">{m["content"]}</div>', unsafe_allow_html=True)

# --- INPUT ---
st.markdown("---")
mic_recorder(start_prompt="🎙️ Voice", stop_prompt="⏹️ Send", key='smart_v18')
u_input = st.chat_input("Puchiye: Time, Date, Weather ya kuch bhi...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    
    try:
        # Injection of real-time context
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Today is Friday, Feb 27, 2026. Time: 12:53 PM. Location: Navi Mumbai. Reply in user's language. Be super fast. No code."},
                {"role": "user", "content": u_input}
            ]
        )
        reply = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        speak_auto(reply)
        st.rerun()
    except Exception as e:
        st.error(f"Bhai, API Key abhi bhi kaam nahi kar rahi: {e}")
        
