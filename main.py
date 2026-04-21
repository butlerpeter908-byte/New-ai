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

# ================= 2. LIVE PREMIUM CSS =================
st.markdown("""
    <style>
    /* Live Background Animation */
    @keyframes gradientBG {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #0f172a);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }

    /* Professional UI Components */
    .stChatInputContainer { border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; }
    
    .user-msg { 
        background: rgba(255, 255, 255, 0.1); border-left: 3px solid #6366f1; 
        padding: 15px; border-radius: 0 12px 12px 12px; margin-bottom: 10px;
    }
    .ai-msg { 
        background: rgba(0, 0, 0, 0.2); border-left: 3px solid #22d3ee; 
        padding: 15px; border-radius: 12px 0 12px 12px; margin-bottom: 10px;
    }
    
    /* Buttons */
    .stButton>button { 
        background: rgba(255, 255, 255, 0.05) !important; 
        border: 1px solid rgba(255,255,255,0.2) !important; 
        color: white !important; 
        transition: 0.3s;
    }
    .stButton>button:hover { background: rgba(99, 102, 241, 0.3) !important; border-color: #6366f1 !important; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.3) !important; backdrop-filter: blur(10px); }
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
    st.markdown("<h1 style='text-align: center; color: white;'>Siddique AI</h1>", unsafe_allow_html=True)
    email = st.text_input("Email:")
    if not st.session_state.otp_sent:
        if st.button("Authenticate"):
            otp = str(random.randint(1000, 9999))
            if send_mail(email, "Access PIN", f"PIN: {otp}"):
                st.session_state.generated_otp = otp; st.session_state.otp_sent = True; st.rerun()
    else:
        otp_in = st.text_input("Enter PIN:", type="password")
        if st.button("Verify"):
            if otp_in == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.title("Control Panel")
    nav = st.radio("Navigation", ["💬 Chat Session", "⚙️ Settings", "📩 Support"])
    st.markdown("---")
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

if nav == "💬 Chat Session":
    for m in st.session_state.messages:
        c = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{c}"><b>{m["role"].title()}</b><br>{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Message Siddique AI...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"Creator: {CREATOR}"}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif nav == "⚙️ Settings":
    st.header("App Preferences")
    if st.button("Reset Chat Data"): st.session_state.messages = []; st.rerun()

elif nav == "📩 Support":
    st.header("Get in Touch")
    fb = st.text_area("Write feedback")
    if st.button("Submit"):
        send_mail(MY_GMAIL, "Feedback", fb)
        st.success("Message sent!")
        
