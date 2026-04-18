import streamlit as st
from groq import Groq
import smtplib
import random
import time
from email.mime.text import MIMEText
from datetime import datetime
import pytz 
import requests 
from streamlit_mic_recorder import mic_recorder

# ================= 1. SETUP =================
GROQ_KEY = "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"
ELEVEN_KEY = "sk_3660ca7856e9021fc0eecda2bc3159eee65b14a045b7f8f6"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Siddique AI 🤖", layout="wide")

# ================= 2. PREMIUM UI =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    .stApp { background: #0d1117; color: #e0e0e0; }
    .user-msg { background: #00ff88; color: #000; padding: 12px; border-radius: 15px 15px 0 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .ai-msg { background: #1e293b; color: #fff; padding: 12px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 5px solid #00d2ff; max-width: 85%; }
    .mic-box { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; text-align: center; border: 1px solid #00ff88; margin-bottom: 20px; }
    .policy-text { font-size: 14px; color: #aaa; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None

# ================= 4. FUNCTIONS =================
def speak_ai(text):
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
        headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
        data = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
        res = requests.post(url, json=data, headers=headers)
        if res.status_code == 200:
            st.audio(res.content, format='audio/mp3', autoplay=True)
    except: pass

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 5. LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.title("🔐 Secure Access")
    email_in = st.text_input("Gmail ID:", value=st.session_state.user_email)
    if not st.session_state.otp_sent:
        if st.button("Send Access PIN"):
            if "@gmail.com" in email_in:
                otp = str(random.randint(1000, 9999))
                if send_mail(email_in, "Access PIN", f"Aapka PIN: {otp}"):
                    st.session_state.generated_otp = otp
                    st.session_state.user_email = email_in
                    st.session_state.otp_sent = True; st.rerun()
    else:
        pin_in = st.text_input("Enter PIN:", type="password")
        if st.button("Login"):
            if pin_in == st.session_state.generated_otp:
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Wrong PIN")
    st.stop()

# ================= 6. MAIN INTERFACE =================
with st.sidebar:
    st.title("SIDDIQUE AI 🤖")
    st.write(f"User: {st.session_state.user_email}")
    st.markdown("---")
    if st.button("🚪 Logout Session"):
        st.session_state.clear(); st.rerun()

# --- TABS SETUP ---
tab_chat, tab_support, tab_policies, tab_about = st.tabs(["💬 Messenger", "📩 Support", "📜 Policies", "ℹ️ About"])

with tab_chat:
    # Mic Section
    st.markdown('<div class="mic-box">', unsafe_allow_html=True)
    voice_data = mic_recorder(start_prompt="Boliye 🎙️", stop_prompt="Sun raha hoon... ⏳", key='voice_input')
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat Box
    chat_container = st.container()
    with chat_container:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    # Input Logic
    text_q = st.chat_input("Type here...")
    final_q = None

    if voice_data and voice_data['id'] != st.session_state.last_audio_id:
        st.session_state.last_audio_id = voice_data['id']
        with st.spinner("Decoding..."):
            trans = client.audio.transcriptions.create(file=("audio.wav", voice_data['bytes']), model="whisper-large-v3")
            final_q = trans.text
    elif text_q:
        final_q = text_q

    if final_q:
        st.session_state.messages.append({"role": "user", "content": final_q})
        try:
            sys = {"role": "system", "content": f"Brief response. Creator: {CREATOR}."}
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[sys] + st.session_state.messages)
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            speak_ai(ans); st.rerun()
        except: st.error("AI Error")

with tab_support:
    st.header("📩 Feedback & Support")
    fb = st.text_area("Write to Siddique...")
    if st.button("Submit Feedback"):
        if fb and send_mail(MY_GMAIL, "User Feedback", fb):
            st.success("Feedback sent successfully!")

with tab_policies:
    st.header("📜 Legal Information")
    with st.expander("Privacy Policy"):
        st.write("Hum aapka data bechte nahi hain. Sab kuch encrypted hai.")
    with st.expander("Terms & Conditions"):
        st.write("Ise sirf personal use ke liye istemal karein.")

with tab_about:
    st.header("ℹ️ About This AI")
    st.write(f"Developed by: **{CREATOR}**")
    st.write("Technologies: Groq, Llama 3.1, ElevenLabs, Streamlit.")
            
