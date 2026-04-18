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

def get_ist_time():
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime('%Y-%m-%d %I:%M:%S %p')

# ================= 2. PREMIUM UI =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background: linear-gradient(-45deg, #0f172a, #051937, #004d40, #0d1117); background-size: 400% 400%; animation: gradient 15s ease infinite; color: #e0e0e0 !important; }
    @keyframes gradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    div[data-testid="stChatInput"] { position: fixed !important; bottom: 30px !important; left: 5% !important; right: 5% !important; width: 90% !important; z-index: 9999 !important; background: rgba(15, 23, 42, 0.9) !important; backdrop-filter: blur(12px); border: 1px solid #00ff88; border-radius: 15px; }
    .welcome-card { background: rgba(255, 255, 255, 0.05); border: 2px solid #00ff88; border-radius: 25px; padding: 40px; text-align: center; }
    .user-msg { background: #00ff88; color: #000; padding: 12px; border-radius: 15px 15px 0 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; border: 1px solid rgba(0,0,0,0.1); }
    .ai-msg { background: #1e293b; color: #fff; padding: 12px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 5px solid #00d2ff; max-width: 85%; }
    .main .block-container { padding-bottom: 180px !important; }
    .mic-float { position: fixed; bottom: 100px; right: 30px; z-index: 10001; background: #1e293b; border-radius: 50%; padding: 10px; border: 2px solid #00ff88; box-shadow: 0 0 15px #00ff88; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><div style="font-size:45px; font-weight:900; color:#00ff88;">SIDDIQUE AI</div><p>Professional Secure Access</p></div>', unsafe_allow_html=True)
    email = st.text_input("Aapka Gmail ID:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Send Access PIN", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Access Code", f"Aapka Secret PIN: {otp}"):
                    st.session_state.generated_otp = otp; st.session_state.user_email = email
                    st.session_state.otp_sent = True; st.rerun()
    else:
        st.success(f"PIN sent to {st.session_state.user_email}")
        otp_in = st.text_input("Enter PIN:", type="password")
        if st.button("Verify & Launch AI", use_container_width=True):
            if otp_in == st.session_state.generated_otp: 
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Incorrect PIN!")
    st.stop()

# ================= 5. VOICE OUTPUT =================
def speak_ai(text):
    try:
        voice_id = "21m00Tcm4TlvDq8ikWAM" # Bella Voice
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
        data = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            st.audio(response.content, format='audio/mp3', autoplay=True)
    except: pass

# ================= 6. MAIN CHAT INTERFACE =================
with st.sidebar:
    st.markdown(f"### User: \n`{st.session_state.user_email}`")
    st.write(f"Created by: {CREATOR}")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

tab_chat, tab_feedback = st.tabs(["💬 Messenger", "📩 Support"])

with tab_chat:
    # Display Chat History
    for m in st.session_state.messages:
        div = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    # Floating Mic Button
    st.markdown('<div class="mic-float">', unsafe_allow_html=True)
    audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop 🛑", key='recorder')
    st.markdown('</div>', unsafe_allow_html=True)

    # Logic to handle Inputs
    user_query = None
    
    # 1. Handle Voice Input
    if audio and audio != st.session_state.last_processed_audio:
        st.session_state.last_processed_audio = audio
        with st.spinner("Sun raha hoon..."):
            try:
                transcription = client.audio.transcriptions.create(
                    file=("audio.wav", audio['bytes']),
                    model="whisper-large-v3",
                )
                if transcription.text.strip():
                    user_query = transcription.text
            except Exception as e:
                st.error("Voice Error")

    # 2. Handle Text Input
    q = st.chat_input("Type something...")
    if q:
        user_query = q

    # 3. Process Response
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.markdown(f'<div class="user-msg">{user_query}</div>', unsafe_allow_html=True)
        
        with st.spinner("AI is thinking..."):
            try:
                sys_msg = {"role": "system", "content": f"You are a helpful AI. Keep responses very short and use emojis. Owner: {CREATOR}."}
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[sys_msg] + st.session_state.messages)
                ans = res.choices[0].message.content
                
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.markdown(f'<div class="ai-msg">{ans}</div>', unsafe_allow_html=True)
                
                speak_ai(ans)
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error("Connection Error")

with tab_feedback:
    fb = st.text_area("Feedback to Creator")
    if st.button("Send Feedback"):
        if fb and send_mail(MY_GMAIL, "AI Feedback", fb):
            st.success("Sent!")
                
