import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder

# ================= FRESH API SETUP =================
# Aapki di hui key yahan paste kar di hai bhai
GROQ_KEY = "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" 
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Global Multi-Lang AI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= WHATSAPP-STYLE UI CSS =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem; background-color: #0E1117;}
    
    /* User Message (Right Side) */
    .user-bubble {
        background-color: #005c4b; color: white;
        padding: 12px 18px; border-radius: 15px 15px 0 15px;
        margin: 10px 0; max-width: 80%; float: right; clear: both;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    
    /* AI Message (Left Side) */
    .ai-bubble {
        background-color: #202c33; color: white;
        padding: 12px 18px; border-radius: 15px 15px 15px 0;
        margin: 10px 0; max-width: 80%; float: left; clear: both;
        border-left: 5px solid #FFD700;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    
    .chat-container { width: 100%; overflow: hidden; display: flex; flex-direction: column; }
</style>
""", unsafe_allow_html=True)

# ================= TOP MENU (DETAILED LEGAL) =================
with st.container():
    col1, col2 = st.columns([6, 4])
    with col2:
        menu = st.selectbox("📋 Menu & Legal Information", ["AI Chat", "Privacy Policy", "Terms & Conditions", "About Creator", "Clear History"])
        
        if menu == "Privacy Policy":
            st.info("### 🔒 Privacy\nYour chats are processed in real-time and deleted after each session. No personal data is stored.")
        elif menu == "Terms & Conditions":
            st.warning("### ⚖️ Terms\nDo not generate illegal or harmful content. This AI is powered by Groq Llama 3.3.")
        elif menu == "About Creator":
            st.success("### 👤 Creator\n[Aapka Naam]\nPowered by Groq & Streamlit.")
        elif menu == "Clear History":
            if st.button("Confirm: Clear Chat"):
                st.session_state.messages = []
                st.rerun()

# ================= VOICE ENGINE =================
def speak_auto(text):
    try:
        # Detects if text is Hindi for correct accent
        lang = 'hi' if any(ord(c) > 2300 for c in text) else 'en'
        tts = gTTS(text=text, lang=lang, tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

# ================= MAIN CHAT AREA =================
st.title("🌍 Global Multi-Lang AI")

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f'<div class="user-bubble">{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble">{m["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================= INPUTS =================
st.markdown("---")
# Mic for voice input
mic_recorder(start_prompt="🎙️ Record Voice", stop_prompt="⏹️ Send Voice", key='pro_mic_v12')

# Text input
u_input = st.chat_input("Type in Hindi, English, or any language...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    
    try:
        # Fast AI Response using your new Key
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional global AI. Always reply in the user's language (Hindi, Hinglish, English, etc.). Be extremely fast and helpful."},
                {"role": "user", "content": u_input}
            ]
        )
        reply = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        speak_auto(reply)
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {e}")
        
