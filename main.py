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

# ================= 2. HIGH CONTRAST EYE-SAVER UI =================
st.markdown("""
    <style>
    /* Dark, Eye-friendly background with subtle green breath */
    @keyframes slowBreath {
        0% {background-color: #050505;}
        50% {background-color: #0a0e0a;}
        100% {background-color: #050505;}
    }
    .stApp {
        animation: slowBreath 10s infinite;
        color: #e0e0e0;
    }

    /* Neon Green Accents */
    :root { --neon-green: #39ff14; }

    /* Glass Cards */
    .card {
        background: rgba(10, 10, 10, 0.7);
        border: 1px solid #1a1a1a;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }

    /* Messages */
    .user-msg { 
        background: #1a1a1a; border-left: 4px solid var(--neon-green); 
        padding: 12px; border-radius: 5px; margin-bottom: 10px; color: #fff;
    }
    .ai-msg { 
        background: transparent; border-left: 4px solid #333; 
        padding: 12px; margin-bottom: 10px; color: #cfcfcf;
    }

    /* High Contrast Buttons */
    .stButton>button { 
        background-color: transparent !important; 
        border: 1px solid var(--neon-green) !important; 
        color: var(--neon-green) !important; 
        border-radius: 4px !important;
        font-weight: bold;
    }
    .stButton>button:hover { 
        background-color: var(--neon-green) !important; 
        color: #000 !important; 
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
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
    st.markdown("<div class='card' style='text-align:center'><h1>SIDDIQUE AI</h1><p style='color:#888'>Secure Terminal</p></div>", unsafe_allow_html=True)
    email = st.text_input("Email ID:")
    if not st.session_state.otp_sent:
        if st.button("Authenticate"):
            otp = str(random.randint(1000, 9999))
            if send_mail(email, "Access PIN", f"PIN: {otp}"):
                st.session_state.generated_otp = otp; st.session_state.otp_sent = True; st.rerun()
    else:
        otp_in = st.text_input("Enter PIN:", type="password")
        if st.button("Unlock"):
            if otp_in == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.markdown("### 🛰️ System")
    nav = st.radio("Navigation", ["💬 Chat", "⚙️ Settings", "📩 Feedback"], label_visibility="collapsed")
    st.markdown("---")
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

if nav == "💬 Chat":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        c = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{c}"><b>{m["role"].title()}</b>: {m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("System prompt...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"Creator: {CREATOR}"}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "⚙️ Settings":
    st.subheader("Preferences")
    if st.button("Wipe Chat Data"): st.session_state.messages = []; st.rerun()

elif nav == "📩 Feedback":
    st.subheader("Direct Transmission")
    fb = st.text_area("Log details")
    if st.button("Transmit"):
        send_mail(MY_GMAIL, "Feedback", fb)
        st.success("Transmitted!")
        
