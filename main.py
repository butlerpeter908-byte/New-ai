import streamlit as st
from groq import Groq
import smtplib
import random
from email.mime.text import MIMEText

# ================= 1. SETUP =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Siddique AI", layout="centered")

# ================= 2. LIVE PREMIUM CYBER UI =================
st.markdown("""
    <style>
    @keyframes bgMove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #4338ca, #be185d, #0f172a);
        background-size: 400% 400%;
        animation: bgMove 10s ease infinite;
    }
    .chat-card { 
        background: rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    h1, h2 { color: #fff !important; text-shadow: 0 0 10px #6366f1; }
    .user-msg { 
        background: linear-gradient(90deg, #6366f1, #a855f7); 
        color: white; padding: 12px 20px; border-radius: 20px 20px 0 20px; 
        margin: 10px 0; text-align: right; box-shadow: 0 0 15px #6366f1;
    }
    .ai-msg { 
        background: rgba(255, 255, 255, 0.1); color: #e2e8f0; 
        padding: 12px 20px; border-radius: 20px 20px 20px 0; margin: 10px 0;
        border-left: 4px solid #38bdf8;
    }
    .stButton>button { 
        background: transparent !important; 
        border: 2px solid #6366f1 !important; 
        color: #fff !important; 
        border-radius: 50px !important;
        transition: 0.4s !important;
    }
    .stButton>button:hover { 
        background: #6366f1 !important; 
        box-shadow: 0 0 20px #6366f1 !important; 
    }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
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
    st.markdown("<div class='chat-card' style='text-align:center'><h1>SIDDIQUE AI</h1><p>System Authentication Required</p></div>", unsafe_allow_html=True)
    email = st.text_input("Enter Email ID")
    if not st.session_state.otp_sent:
        if st.button("Initialize Access"):
            otp = str(random.randint(1000, 9999))
            # Sending OTP to user
            if send_mail(email, "Access PIN", f"Your PIN: {otp}"):
                # Notification to Admin (Siddique)
                send_mail(MY_GMAIL, "Login Attempt Alert!", f"User {email} has requested a PIN: {otp}")
                st.session_state.generated_otp = otp; st.session_state.otp_sent = True; st.rerun()
    else:
        otp_in = st.text_input("Enter Secret PIN", type="password")
        if st.button("Unlock System"):
            if otp_in == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.header("🛸 System Panel")
    nav = st.radio("Navigation", ["💬 Nexus Chat", "⚙️ Core Settings", "📩 Terminal Feedback"])
    st.markdown("---")
    if st.button("System Logout"): st.session_state.logged_in = False; st.rerun()

if nav == "💬 Nexus Chat":
    st.markdown("<div class='chat-card'>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        c = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{c}">{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Connect with AI...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"Creator: {CREATOR}"}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "⚙️ Core Settings":
    st.subheader("Preferences")
    if st.button("Purge Memory"): st.session_state.messages = []; st.rerun()

elif nav == "📩 Terminal Feedback":
    st.subheader("Direct Link")
    fb = st.text_area("Log your message")
    if st.button("Transmit"):
        send_mail(MY_GMAIL, "Feedback", fb)
        st.success("Transmitted!")
        
