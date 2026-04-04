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

# ================= 2. SHAANDAAR UI CSS =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    .stApp { 
        background: radial-gradient(circle at top, #1a1f25 0%, #0e1117 100%) !important;
        color: #e0e0e0 !important;
    }
    /* Bottom Chat Fix */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 20px !important;
        z-index: 9999 !important;
        background: rgba(14, 17, 23, 0.9) !important;
        backdrop-filter: blur(10px);
    }
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
    .stException, .stAlert { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "fb_sent" not in st.session_state: st.session_state.fb_sent = False
if "otp_timestamp" not in st.session_state: st.session_state.otp_timestamp = 0

# Optimized Fast Mail Sender
def send_fast_otp(to_email, otp_code):
    try:
        msg = MIMEText(f"Aapka Secure Login OTP hai: {otp_code}\n\nYe code 10 minutes tak valid hai.")
        msg['Subject'] = '🚀 Quick Login OTP'
        msg['From'] = MY_GMAIL
        msg['To'] = to_email
        
        # Connection pool ki tarah fast login
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(MY_GMAIL, APP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# ================= 4. LOGIN SCREEN (OTP & RESEND) =================
if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><div class="welcome-text">WELCOME</div><p>Siddique\'s Super-Fast AI Portal</p></div>', unsafe_allow_html=True)
    
    email_input = st.text_input("Enter Gmail:", value=st.session_state.user_email, placeholder="example@gmail.com")
    
    if not st.session_state.otp_sent:
        if st.button("Get OTP (Under 10s)", use_container_width=True):
            if "@gmail.com" in email_input:
                new_otp = str(random.randint(100000, 999999)) # 6 Digit for better security
                with st.spinner("Sending OTP..."):
                    if send_fast_otp(email_input, new_otp):
                        st.session_state.generated_otp = new_otp
                        st.session_state.user_email = email_input
                        st.session_state.otp_sent = True
                        st.session_state.otp_timestamp = time.time()
                        st.rerun()
            else:
                st.error("Please enter a valid Gmail.")
    else:
        st.success(f"OTP sent to {st.session_state.user_email}")
        otp_val = st.text_input("Enter OTP Code:", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Verify & Login", use_container_width=True):
                if otp_val == st.session_state.generated_otp:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Wrong OTP!")
        
        with col2:
            # Resend Logic (1 Min Wait)
            time_passed = time.time() - st.session_state.otp_timestamp
            if time_passed < 60:
                st.button(f"Resend in {int(60 - time_passed)}s", disabled=True, use_container_width=True)
                time.sleep(1)
                st.rerun()
            else:
                if st.button("Resend OTP Now", use_container_width=True):
                    st.session_state.otp_sent = False # Phir se process start karega
                    st.rerun()
                    
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.user_email}**")
    if st.button("🗑️ Clear Chat", use_container_width=True): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout Account", use_container_width=True): 
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "⚙️ Settings", "📩 Feedback"])

with tab_chat:
    chat_box = st.container()
    with chat_box:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Ask me anything...")
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
    with st.expander("👤 Creator Info"): st.write(f"Developed by {CREATOR}")
    with st.expander("🛡️ Privacy Policy"): st.write("We value your privacy. Sessions are temporary.")

with tab_feedback:
    if st.session_state.fb_sent:
        st.markdown('<div class="thanks-card"><div class="thanks-text">THANKS FOR FEEDBACK!</div><p>Aapka sandesh Siddique tak pahunch gaya hai. ❤️</p></div>', unsafe_allow_html=True)
        if st.button("Send New Feedback"): st.session_state.fb_sent = False; st.rerun()
    else:
        st.header("📩 Feedback")
        fb = st.text_area("Experience kaisa raha?", height=150)
        if st.button("Submit Feedback", use_container_width=True):
            if fb and send_fast_otp(MY_GMAIL, f"FEEDBACK: {fb}"):
                st.session_state.fb_sent = True; st.rerun()
    
