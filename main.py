import streamlit as st
from groq import Groq
import smtplib
import random
import time
from email.mime.text import MIMEText

# ================= 1. SETUP & KEYS =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. UI & DARK MODE CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown("""
    <style>
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
    
    /* Bottom Chat Fix */
    .stChatInputContainer { position: fixed !important; bottom: 20px !important; z-index: 999; }

    /* Login Box Styling */
    .login-info { color: #00ff88; font-size: 14px; margin-top: 5px; font-weight: bold; }
    .timer-text { color: #ffa500; font-size: 12px; }

    /* Chat Bubbles */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 80%; }
    
    /* Hide Errors */
    .stException, .stAlert[data-baseweb="notification"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC (PERMANENT LOGIN) =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "last_otp_time" not in st.session_state: st.session_state.last_otp_time = 0

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = sub
        msg['From'] = MY_GMAIL
        msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS)
            s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN WITH RESEND TIMER =================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#00ff88;'>🔐 Secure Login</h1>", unsafe_allow_html=True)
    
    email = st.text_input("Enter your Gmail:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Send OTP", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Login OTP", f"Aapka OTP hai: {otp}"):
                    st.session_state.generated_otp = otp
                    st.session_state.user_email = email
                    st.session_state.otp_sent = True
                    st.session_state.last_otp_time = time.time()
                    st.rerun()
    else:
        st.markdown(f"<p class='login-info'>📩 Check your Gmail: {st.session_state.user_email}</p>", unsafe_allow_html=True)
        otp_in = st.text_input("Enter 4-Digit OTP:", type="password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Verify OTP", use_container_width=True):
                if otp_in == st.session_state.generated_otp:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Wrong OTP!")
        
        with col2:
            # RESEND TIMER LOGIC
            elapsed = time.time() - st.session_state.last_otp_time
            if elapsed < 60:
                st.markdown(f"<p class='timer-text'>Resend in {int(60 - elapsed)}s</p>", unsafe_allow_html=True)
                time.sleep(1) # Chota delay for visual update
                st.rerun()
            else:
                if st.button("Resend OTP", use_container_width=True):
                    otp = str(random.randint(1000, 9999))
                    if send_mail(st.session_state.user_email, "Resend Login OTP", f"Aapka naya OTP hai: {otp}"):
                        st.session_state.generated_otp = otp
                        st.session_state.last_otp_time = time.time()
                        st.success("OTP Sent Again!")
                        st.rerun()

        if st.button("Change Email"):
            st.session_state.otp_sent = False
            st.rerun()
    st.stop()

# ================= 5. MAIN CHAT & FEEDBACK =================
with st.sidebar:
    st.markdown(f"<h3 style='color:#00ff88;'>👤 {st.session_state.user_email}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    choice = st.radio("Menu", ["💬 Chat", "📩 Feedback"])
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout Account", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

if choice == "💬 Chat":
    st.markdown("<h3 style='text-align:center; color:#00ff88;'>🤖 Siddique's AI</h3>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Puchiye...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: pass

elif choice == "📩 Feedback":
    st.header("📩 Send Feedback")
    fb_text = st.text_area("Aapka experience kaisa raha?", height=150)
    if st.button("🚀 Submit Feedback", use_container_width=True):
        if fb_text:
            if send_mail(MY_GMAIL, "New User Feedback", f"User: {st.session_state.user_email}\n\n{fb_text}"):
                st.success("Feedback sent! ✅")
            else: st.error("Error sending feedback.")
