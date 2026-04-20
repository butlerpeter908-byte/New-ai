import streamlit as st
from groq import Groq
import smtplib
import random
import time
from email.mime.text import MIMEText
from datetime import datetime
import pytz 

# ================= 1. SETUP =================
# Security Note: Key updated to your latest provided credential.
GROQ_KEY = "Gsk_hQPE0xbMVB5036M5cNhRWGdyb3FYQArs9HOUFhV1locgLTaayXmn"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Siddique AI 🤖", layout="wide")

def get_ist_time():
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime('%Y-%m-%d %I:%M:%S %p')

# ================= 2. UI STYLING =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    
    .stApp { 
        background: linear-gradient(-45deg, #0f172a, #051937, #004d40, #0d1117);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #e0e0e0 !important;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 30px !important;
        left: 5% !important;
        right: 5% !important;
        width: 90% !important;
        z-index: 9999 !important;
        background: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(12px);
        border: 1px solid #00ff88;
        border-radius: 15px;
    }

    .welcome-card { background: rgba(255, 255, 255, 0.05); border: 2px solid #00ff88; border-radius: 25px; padding: 40px; text-align: center; }
    .user-msg { background: #00ff88; color: #000; padding: 12px; border-radius: 15px 15px 0 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; font-weight: 500; }
    .ai-msg { background: #1e293b; color: #fff; padding: 12px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 5px solid #00d2ff; max-width: 85%; }
    .main .block-container { padding-bottom: 150px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><h1 style="color:#00ff88;">SIDDIQUE AI</h1><p>Professional Secure Access</p></div>', unsafe_allow_html=True)
    email = st.text_input("Aapka Gmail ID:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Send Access PIN", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Access Code", f"Aapka Secret PIN: {otp}"):
                    st.session_state.generated_otp = otp; st.session_state.user_email = email
                    st.session_state.otp_sent = True; st.rerun()
            else: st.error("Please enter a valid @gmail.com address")
    else:
        otp_in = st.text_input("Enter PIN:", type="password")
        col_v, col_e = st.columns(2)
        with col_v:
            if st.button("Verify & Launch AI", use_container_width=True):
                if otp_in == st.session_state.generated_otp: 
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Incorrect PIN!")
        with col_e:
            if st.button("Change Email", use_container_width=True):
                st.session_state.otp_sent = False; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.markdown(f"### Logged in as: \n`{st.session_state.user_email}`")
    if st.button("🚪 Logout Session", use_container_width=True):
        st.session_state.logged_in = False; st.session_state.otp_sent = False; st.rerun()

tab_chat, tab_settings = st.tabs(["💬 Messenger", "⚙️ Account & Privacy"])

with tab_chat:
    for m in st.session_state.messages:
        div = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Type here...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[{"role": "system", "content": f"You are a helpful AI by {CREATOR}."}] + st.session_state.messages
            )
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

with tab_settings:
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []; st.rerun()
    st.divider()
    st.write(f"Developed by {CREATOR}")
            
