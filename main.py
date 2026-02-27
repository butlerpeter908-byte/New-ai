import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder

# ================= SETUP =================
GROQ_KEY = "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"
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Universal AI Pro Max", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= TOP MENU (DETAILED) =================
col1, col2 = st.columns([6, 4])
with col2:
    menu = st.selectbox("📋 Options & Legal", ["AI Chat", "Privacy Policy", "Terms & Conditions", "About Creator", "Clear History"])
    
    if menu == "Privacy Policy":
        st.markdown("""
        ### 🔒 Privacy Policy
        * **Data Encryption:** Your conversations are processed in real-time and not stored on our permanent servers.
        * **Anonymity:** We do not collect names, emails, or personal identifiers.
        * **Cookies:** This app uses minimal session cookies to keep your chat active.
        """)
    elif menu == "Terms & Conditions":
        st.markdown("""
        ### ⚖️ Terms & Conditions
        * **Usage:** Users must not generate hate speech, illegal content, or NSFW material.
        * **Liability:** This AI is for informational purposes. We are not responsible for any decisions made based on AI output.
        * **Age Limit:** Users must be 13+ to interact with the global model.
        """)
    elif menu == "About Creator":
        st.markdown("""
        ### 👤 Creator Information
        * **Developer:** [Siddiqui Mohd Saif]
        * **Model:** Powered by Groq Llama 3.3 (Ultra Fast).
        * **Goal:** Providing a global, multi-language communication tool.
        """)
    elif menu == "Clear History":
        if st.button("Confirm Clear Chat"):
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

# ================= APP LOGIC =================
st.title("🌍 Global Multi-Lang AI")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- MIC & INPUT ---
audio_data = mic_recorder(start_prompt="🎙️ Speak", stop_prompt="⏹️ Stop", key='pro_v10')
u_input = st.chat_input("Type in any language (English default)...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)
    
    with st.chat_message("assistant"):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """
                1. Default language: English. 
                2. Detect user language and reply in the SAME language (Hindi, Hinglish, Spanish, etc.).
                3. Be professional and extremely fast (under 1s).
                """},
                {"role": "user", "content": u_input}
            ]
        )
        reply = res.choices[0].message.content
        st.write(reply)
        speak_auto(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
    
