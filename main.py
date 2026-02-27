import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
# BHAU, YAHAN APNI GROQ KEY DAALNA WARNA WOH RED ERROR PHIR SE AAYEGA!
GROQ_KEY = "YOUR_GROQ_API_KEY_HERE" 
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Global AI Pro Max", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= TOP DROPDOWN MENU =================
st.markdown("---")
m_col1, m_col2 = st.columns([6, 4])
with m_col2:
    menu = st.selectbox("📋 App Menu & Legal", ["AI Chat", "Privacy Policy (Detailed)", "Terms & Conditions (Long)", "About Creator", "Clear History"])
    
    if menu == "Privacy Policy (Detailed)":
        st.markdown("""
        ### 🔒 Detailed Privacy Policy
        * **Real-time Processing:** We process your data in real-time using Groq's high-speed cloud.
        * **No Logs:** We do not keep permanent logs of your personal chat history.
        * **Voice Privacy:** Your voice recordings are processed for text conversion and deleted instantly.
        """)
    elif menu == "Terms & Conditions (Long)":
        st.markdown("""
        ### ⚖️ Detailed Terms & Conditions
        * **Responsible Use:** Users agree not to generate harmful, illegal, or offensive content.
        * **Service Limits:** We rely on third-party APIs like Groq and gTTS; service depends on their uptime.
        * **Global Support:** This AI supports multiple world languages to ensure accessibility for all.
        """)
    elif menu == "About Creator":
        st.info("👤 **Creator:** [SIDDIQUI MOHD SAIF]\n\n**Goal:** Making AI fast and easy for everyone.")
    elif menu == "Clear History":
        if st.button("Confirm Wipe Chat"):
            st.session_state.messages = []
            st.rerun()

# ================= VOICE LOGIC =================
def speak_auto(text):
    try:
        # Detects language for voice accent
        lang = 'hi' if any(ord(c) > 2300 for c in text) else 'en'
        tts = gTTS(text=text, lang=lang, tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    except: pass

# ================= MAIN APP =================
st.title("🌍 Global Multi-Lang AI")

# Display History
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- MIC & INPUT ---
st.write("🎙️ Talk or Type in any language:")
audio_data = mic_recorder(start_prompt="Record Voice", stop_prompt="Stop & Send", key='final_pro_v1')

u_input = st.chat_input("Type here (English, Hindi, etc.)...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    with st.chat_message("assistant"):
        try:
            # FASTEST RESPONSE LOGIC
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a fast global AI. Detect user language and reply in the same language. Default is English. Never show code blocks."},
                    {"role": "user", "content": u_input}
                ]
            )
            reply = res.choices[0].message.content
            st.write(reply)
            speak_auto(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Error: Please check your API Key in the code! {e}")
    st.rerun()
    
