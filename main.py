import streamlit as st
from groq import Groq
import smtplib
import random
import time
from email.mime.text import MIMEText

# ================= 1. SETUP =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="New AI 🤖", layout="wide")

# ================= 2. THE PERMANENT BOTTOM CHAT CSS =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    .stApp { 
        background: radial-gradient(circle at top, #1a1f25 0%, #0e1117 100%) !important;
        color: #e0e0e0 !important;
    }

    /* FORCING CHAT INPUT TO BOTTOM */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 30px !important;
        left: 5% !important;
        right: 5% !important;
        width: 90% !important;
        z-index: 9999 !important;
        background: rgba(14, 17, 23, 0.9) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px;
    }

    /* Welcome & Feedback Card Styling */
    .welcome-card, .thanks-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
    }
    .welcome-text, .thanks-text {
        font-size: 35px;
        font-weight: 800;
        background: linear-gradient(90deg, #00ff88, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Chat Bubbles */
    .user-msg { background: linear-gradient(135deg, #00b09b, #96c93d); padding: 12px; border-radius: 18px 18px 2px 18px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .ai-msg { background: rgba(255, 255, 255, 0.08); padding: 12px; border-radius: 18px 18px 18px 2px; margin: 10px 0; border-left: 4px solid #00ff88; max-width: 80%; }
    
    /* Ensuring enough space at bottom for chat input */
    .main .block-container { padding-bottom: 120px !important; }

    .stException, .stAlert { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "fb_sent" not in st.session_state: st.session_state.fb_sent = False

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><div class="welcome-text">WELCOME</div><p>Siddique\'s AI Secure Portal</p></div>', unsafe_allow_html=True)
    email = st.text_input("Gmail ID:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Send Secure OTP", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Login OTP", f"Aapka OTP: {otp}"):
                    st.session_state.generated_otp = otp; st.session_state.user_email = email
                    st.session_state.otp_sent = True; st.rerun()
    else:
        st.info(f"OTP Sent! Check {st.session_state.user_email}")
        otp_in = st.text_input("OTP Daalein:", type="password")
        if st.button("Verify & Enter", use_container_width=True):
            if otp_in == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.write(f"👤 {st.session_state.user_email}")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "⚙️ Settings", "📩 Feedback"])

# --- CHAT TAB ---
with tab_chat:
    chat_box = st.container()
    with chat_box:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Type your message here...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        with chat_box: st.markdown(f'<div class="user-msg">{q}</div>', unsafe_allow_html=True)
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=st.session_state.messages)
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            with chat_box: st.markdown(f'<div class="ai-msg">{ans}</div>', unsafe_allow_html=True)
            st.rerun()
        except: pass

# --- SETTINGS TAB ---
with tab_settings:
    st.header("⚙️ Settings")
    with st.expander("👤 About"): st.write(f"Crafted by {CREATOR}")
    with st.expander("🛡️ Privacy"): st.write("Safe & Session-based.")

# --- FEEDBACK TAB ---
with tab_feedback:
    if st.session_state.fb_sent:
        st.markdown("""
            <div class="thanks-card">
                <div class="thanks-text">THANKS FOR FEEDBACK!</div>
                <p>Aapka sandesh Siddique tak pahunch gaya hai. ❤️</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Send Another Feedback"):
            st.session_state.fb_sent = False; st.rerun()
    else:
        st.header("📩 Feedback")
        fb = st.text_area("Write here...", height=150)
        if st.button("Submit to Siddique", use_container_width=True):
            if fb and send_mail(MY_GMAIL, "New Feedback", f"From: {st.session_state.user_email}\n{fb}"):
                st.session_state.fb_sent = True; st.rerun()
    
