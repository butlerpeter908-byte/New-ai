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

# ================= 2. UI & DESIGN (Dark Mode) =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
    
    /* Chat Bubbles */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; border: 0.5px solid #00a884; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 80%; }
    
    /* Input Fix */
    .stChatInputContainer { position: fixed !important; bottom: 20px !important; z-index: 999; background-color: #0e1117 !important; }
    
    /* Settings Styling */
    .settings-card { background-color: #1c2128; padding: 15px; border-radius: 10px; border-left: 4px solid #00ff88; margin-bottom: 10px; }
    
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

# ================= 4. LOGIN (OTP) =================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#00ff88;'>🔐 Secure Login</h1>", unsafe_allow_html=True)
    email = st.text_input("Enter Gmail:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Send OTP", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Login OTP", f"OTP: {otp}"):
                    st.session_state.generated_otp = otp; st.session_state.user_email = email
                    st.session_state.otp_sent = True; st.session_state.last_otp_time = time.time(); st.rerun()
    else:
        st.info(f"📩 OTP sent to {st.session_state.user_email}")
        otp_in = st.text_input("Enter OTP:", type="password")
        if st.button("Verify & Enter", use_container_width=True):
            if otp_in == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
        
        elapsed = time.time() - st.session_state.last_otp_time
        if elapsed < 60: st.write(f"Resend in {int(60-elapsed)}s")
        elif st.button("Resend OTP"): st.session_state.otp_sent = False; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE (TABS) =================
with st.sidebar:
    st.write(f"👤 **{st.session_state.user_email}**")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

# --- TABS CREATION ---
tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Chat", "⚙️ Settings", "📩 Feedback"])

# --- CHAT TAB ---
with tab_chat:
    st.markdown("<h3 style='text-align:center; color:#00ff88;'>🤖 Siddique's AI</h3>", unsafe_allow_html=True)
    chat_box = st.container()
    with chat_box:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Puchiye...")
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
    st.header("⚙️ App Settings")
    
    with st.expander("👤 About Developer"):
        st.write(f"Created by: **{CREATOR}**")
        st.write("Purpose: Advanced AI assistant for high-speed mobile interaction.")

    with st.expander("🛡️ Privacy Policy"):
        st.write("1. We do not store your personal chats on our main database.")
        st.write("2. Sessions are temporary and cleared upon logout.")
        st.write("3. Your Email is only used for OTP verification.")

    with st.expander("📄 Terms & Conditions"):
        st.write("- Use this AI for ethical purposes.")
        st.write("- Do not attempt to bypass security layers.")
        st.write("- The developer is not responsible for generated content.")

# --- FEEDBACK TAB ---
with tab_feedback:
    st.header("📩 User Feedback")
    fb = st.text_area("Write your feedback here...", height=150)
    if st.button("🚀 Send Feedback", use_container_width=True):
        if fb:
            if send_mail(MY_GMAIL, "New Feedback", f"User: {st.session_state.user_email}\n\n{fb}"):
                st.success("Sent to Siddique! ✅")
            else: st.error("Error sending mail.")
        else: st.warning("Please write something.")
            
