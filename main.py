import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder
from datetime import datetime

# ================= API SETUP =================
# Aapki di hui fresh key yahan fit kar di hai
GROQ_KEY = "Gsk_NpDwPdUylUGsI0KXLHlIWGdyb3FYZTr8n4pIMru69wiVFzTaRAPf" 
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Universal Smart AI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= SMART UI CSS =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem; background-color: #0E1117;}
    
    .user-bubble {
        background-color: #005c4b; color: white;
        padding: 12px 18px; border-radius: 18px 18px 0 18px;
        margin: 10px 0; max-width: 80%; float: right; clear: both;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    
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

# ================= TOP MENU =================
with st.container():
    col1, col2 = st.columns([6, 4])
    with col2:
        menu = st.selectbox("📋 Menu & Legal", ["AI Chat", "Privacy Policy", "Terms & Conditions", "Clear History"])
        if menu == "Privacy Policy":
            st.info("### 🔒 Privacy\nNo chat history is stored permanently.")
        elif menu == "Terms & Conditions":
            st.warning("### ⚖️ Terms\nAI results depend on real-time API data.")
        elif menu == "Clear History":
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

# ================= MAIN APP =================
st.title("🌍 Smart Multi-Lang AI")

# Time & Date Logic
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
current_date = now.strftime("%Y-%m-%d")

st.markdown(f'<div class="chat-container">', unsafe_allow_html=True)
for m in st.session_state.messages:
    bubble_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{bubble_class}">{m["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- INPUT ---
st.markdown("---")
mic_recorder(start_prompt="🎙️ Voice", stop_prompt="⏹️ Send", key='smart_v16')
u_input = st.chat_input("Ask about Time, Weather, or anything...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    
    try:
        # AI ko context dena Time/Date ka
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"""
                You are a smart global AI. 
                Current Date: {current_date}, Current Time: {current_time}.
                Detect user language and reply instantly. 
                For weather, provide estimated info based on context. 
                Never output code blocks.
                """},
                {"role": "user", "content": u_input}
            ]
        )
        reply = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        speak_auto(reply)
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
        
