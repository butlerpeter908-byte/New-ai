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

# ================= 2. THE CLEAN COLORFUL CSS (Original Layout) =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    .stApp { 
        background: #0e1117 !important;
        background-image: radial-gradient(circle at center, #1a1f25 0%, #0e1117 100%) !important;
        color: #e0e0e0 !important;
    }

    /* FORCING CHAT INPUT TO BOTTOM - Same as original */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 30px !important;
        left: 5% !important;
        right: 5% !important;
        width: 90% !important;
        z-index: 9999 !important;
        background: rgba(30, 39, 46, 0.9) !important;
        backdrop-filter: blur(10px);
        border: 1px solid #00ff88;
        border-radius: 15px;
    }

    /* Welcome & Feedback Card - Improved Colors */
    .welcome-card, .thanks-card {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #00ff88;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
    }
    .welcome-text, .thanks-text {
        font-size: 40px;
        font-weight: 800;
        color: #00ff88;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }

    /* Chat Bubbles - Original Layout Fixed */
    .user-msg { 
        background: #00ff88; 
        color: #000; 
        padding: 12px; 
        border-radius: 15px 15px 0 15px; 
        margin: 10px 0; 
        text-align: right; 
        margin-left: auto; 
        max-width: 80%;
        font-weight: 500;
    }
    .ai-msg { 
        background: #1e272e; 
        color: #fff;
        padding: 12px; 
        border-radius: 15px 15px 15px 0; 
        margin: 10px 0; 
        border-left: 5px solid #00d2ff; 
        max-width: 85%; 
    }
    
    .main .block-container { padding-bottom: 150px !important; }
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
            # Smart identity: Sirf puchne par hi batayega
            instruction = {"role": "system", "content": f"You are a helpful AI. ONLY if the user asks about your creator/owner, state that you were developed by {CREATOR}."}
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[instruction] + st.session_state.messages)
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
        st.markdown(f"""
            <div class="thanks-card">
                <div class="thanks-text">THANKS FOR FEEDBACK!</div>
                <p>Aapka sandesh {CREATOR.split()[0]} tak pahunch gaya hai. ❤️</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Send Another Feedback"):
            st.session_state.fb_sent = False; st.rerun()
    else:
        st.header("📩 Feedback")
        fb = st.text_area("Write here...", height=150)
        if st.button(f"Submit to {CREATOR.split()[0]}", use_container_width=True):
            if fb and send_mail(MY_GMAIL, "New Feedback", f"From: {st.session_state.user_email}\n{fb}"):
                st.session_state.fb_sent = True; st.rerun()
        
