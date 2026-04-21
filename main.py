import streamlit as st
from groq import Groq
import smtplib
import random
import time
from email.mime.text import MIMEText
from datetime import datetime
import pytz

# ================= 1. SETUP =================
GROQ_KEY = "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"
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
    .stApp { background: linear-gradient(-45deg, #0f172a, #051937, #004d40, #0d1117); background-size: 400% 400%; animation: gradient 15s ease infinite; color: #e0e0e0 !important; }
    div[data-testid="stChatInput"] { position: fixed !important; bottom: 30px !important; left: 5% !important; right: 5% !important; width: 90% !important; z-index: 9999 !important; background: rgba(15, 23, 42, 0.9) !important; backdrop-filter: blur(12px); border: 1px solid #00ff88; border-radius: 15px; }
    .user-msg { background: #00ff88; color: #000; padding: 12px; border-radius: 15px 15px 0 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .ai-msg { background: #1e293b; color: #fff; padding: 12px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 5px solid #00d2ff; max-width: 85%; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "feedback_sent" not in st.session_state: st.session_state.feedback_sent = False
if "messages" not in st.session_state: st.session_state.messages = []

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN =================
if not st.session_state.logged_in:
    st.title("SIDDIQUE AI - Secure Access")
    email = st.text_input("Email ID:")
    if not st.session_state.otp_sent:
        if st.button("Get PIN"):
            otp = str(random.randint(1000, 9999))
            if send_mail(email, "Access PIN", f"PIN: {otp}"):
                st.session_state.generated_otp = otp; st.session_state.user_email = email
                st.session_state.otp_sent = True; st.rerun()
    else:
        otp_in = st.text_input("Enter PIN:", type="password")
        if st.button("Verify"):
            if otp_in == st.session_state.generated_otp: 
                st.session_state.logged_in = True; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE =================
tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "⚙️ Account & Privacy", "📩 Support"])

with tab_chat:
    for m in st.session_state.messages:
        st.markdown(f'<div class="{"user-msg" if m["role"]=="user" else "ai-msg"}">{m["content"]}</div>', unsafe_allow_html=True)
    q = st.chat_input("Type here...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"Creator: {CREATOR}"}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

with tab_settings:
    st.header("Account & Privacy")
    if st.button("Clear History"): st.session_state.messages = []; st.rerun()
    with st.expander("🛡️ Privacy Policy"): st.write("Session-based chat, no data retention.")
    with st.expander("📄 Terms and Conditions"): st.write("Educational use only.")
    with st.expander("ℹ️ About"): st.write(f"Developed by {CREATOR}")

with tab_feedback:
    if st.session_state.feedback_sent:
        st.success("✅ Thanks for your feedback, Sir!")
    else:
        fb = st.text_area("Your feedback...")
        if st.button("Submit"):
            send_mail(MY_GMAIL, "Feedback", fb)
            st.session_state.feedback_sent = True; st.rerun()
