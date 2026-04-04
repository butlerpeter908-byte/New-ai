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

# ================= 2. THE SHAANDAAR UI CSS =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    .stApp { 
        background: radial-gradient(circle at top, #1a1f25 0%, #0e1117 100%) !important;
        color: #e0e0e0 !important;
    }

    /* Welcome Container Styling */
    .welcome-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }
    .welcome-text {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(90deg, #00ff88, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    /* Input & Button Styling */
    .stTextInput>div>div>input {
        background-color: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
    }
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(90deg, #00ff88, #00d2ff) !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        height: 50px;
    }

    /* Chat Bubbles */
    .user-msg { background: linear-gradient(135deg, #00b09b, #96c93d); padding: 14px; border-radius: 20px 20px 4px 20px; margin: 12px 0; text-align: right; margin-left: auto; max-width: 85%; }
    .ai-msg { background: rgba(255, 255, 255, 0.07); padding: 14px; border-radius: 20px 20px 20px 4px; margin: 12px 0; border-left: 4px solid #00ff88; max-width: 85%; }
    
    .stChatInputContainer { position: fixed !important; bottom: 15px !important; z-index: 1000; background: transparent !important; }
    .stException, .stAlert { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "last_otp_time" not in st.session_state: st.session_state.last_otp_time = 0

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN SCREEN WITH WELCOME =================
if not st.session_state.logged_in:
    # --- WELCOME CONTAINER ---
    st.markdown("""
        <div class="welcome-card">
            <div class="welcome-text">WELCOME</div>
            <p style="color: #888; font-size: 16px;">Siddique's Secure AI Portal Mein Aapka Swagat Hai</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- LOGIN INPUTS ---
    email = st.text_input("Apna Gmail Id Daalein:", value=st.session_state.user_email, placeholder="example@gmail.com")
    
    if not st.session_state.otp_sent:
        if st.button("Generate Secure OTP", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Login OTP", f"Aapka OTP: {otp}"):
                    st.session_state.generated_otp = otp; st.session_state.user_email = email
                    st.session_state.otp_sent = True; st.session_state.last_otp_time = time.time(); st.rerun()
    else:
        st.success(f"OTP Sent! Check {st.session_state.user_email}")
        otp_in = st.text_input("4-Digit OTP Daalein:", type="password")
        if st.button("Verify & Login", use_container_width=True):
            if otp_in == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
            
        elapsed = time.time() - st.session_state.last_otp_time
        if elapsed < 60: st.info(f"Resend OTP in {int(60-elapsed)}s")
        else: 
            if st.button("Resend OTP Now", use_container_width=True): st.session_state.otp_sent = False; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.markdown(f"<div style='text-align:center;'><h3 style='color:#00ff88;'>👤 Profile</h3><p>{st.session_state.user_email}</p></div>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout", use_container_width=True): st.session_state.logged_in = False; st.rerun()

tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "⚙️ Settings", "📩 Feedback"])

with tab_chat:
    chat_box = st.container()
    with chat_box:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Ask anything...")
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

with tab_settings:
    st.header("⚙️ Settings")
    with st.expander("👤 About Developer"): st.write(f"Developed by {CREATOR}")
    with st.expander("🛡️ Privacy Policy"): st.write("Data is session-based and secure.")

with tab_feedback:
    st.header("📩 Feedback")
    fb = st.text_area("Kaisa laga app?")
    if st.button("Submit Feedback", use_container_width=True):
        if fb and send_mail(MY_GMAIL, "Feedback", f"From: {st.session_state.user_email}\n{fb}"):
            st.success("Sent! ✅")
        
