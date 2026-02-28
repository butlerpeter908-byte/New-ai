import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ================= 1. CREDENTIALS =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohammad Saif"

client = Groq(api_key=GROQ_KEY)

# ================= 2. PERSISTENT LOGIN & DATA =================
if "user_db" not in st.session_state:
    st.session_state.user_db = {"admin": "123"}

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Chat"

# ================= 3. LOGIN PAGE FIX =================
if not st.session_state.is_logged_in:
    st.title("🔐 Login to New AI")
    t_log, t_sign = st.tabs(["Login", "Sign Up"])
    
    with t_sign:
        nu = st.text_input("New Username", key="s_u")
        np = st.text_input("New Password", type="password", key="s_p")
        if st.button("Register"):
            if nu and np:
                st.session_state.user_db[nu] = np
                st.success("Registration Successful!")
            else: st.error("Fill details")

    with t_log:
        un = st.text_input("Username", key="l_u")
        up = st.text_input("Password", type="password", key="l_p")
        if st.button("Login"):
            if un in st.session_state.user_db and st.session_state.user_db[un] == up:
                st.session_state.is_logged_in = True
                st.session_state.current_user = un
                st.rerun()
            else: st.error("Invalid Login")
    st.stop()

# ================= 4. PERMANENT TOP MENU (FIXED) =================
# Ab menu sidebar mein nahi, screen ke upar hamesha dikhega
st.markdown("### 📌 Navigation Menu")
m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    if st.button("💬 Chat"): st.session_state.app_mode = "Chat"
with m2:
    if st.button("👤 About"): st.session_state.app_mode = "About"
with m3:
    if st.button("📝 Feedback"): st.session_state.app_mode = "Feedback"
with m4:
    if st.button("🔒 Privacy"): st.session_state.app_mode = "Privacy"
with m5:
    if st.button("⚖️ Terms"): st.session_state.app_mode = "Terms"

st.markdown("---")

# ================= 5. PAGE CONTENT =================
mode = st.session_state.app_mode

if mode == "Chat":
    st.title("💬 WhatsApp Chat")
    st.markdown("""
    <style>
        .user-bubble { background-color: #005c4b; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: right; clear: both; }
        .ai-bubble { background-color: #202c33; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: left; clear: both; border-left: 4px solid #00a884; }
    </style>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state: st.session_state.chat_history = []

    for chat in st.session_state.chat_history:
        div = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{div}">{chat["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Siddique Mohammad Saif ka AI ready hai...")
    if q:
        st.session_state.chat_history.append({"role": "user", "content": q})
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Your name is New AI, created by {CREATOR_NAME}."}, {"role": "user", "content": q}]
        )
        st.session_state.chat_history.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif mode == "About":
    st.header("👤 About Creator")
    st.info(f"Created by: **{CREATOR_NAME}**")

elif mode == "Feedback":
    st.header("📝 Feedback")
    msg = st.text_area("Write here:")
    if st.button("Send Feedback"):
        st.success("Thanks for feedback") # Message updated

elif mode == "Privacy":
    st.header("🔒 Privacy Policy")
    st.write("Aapka data secure hai.")

elif mode == "Terms":
    st.header("⚖️ Terms & Conditions")
    st.write("Use responsibly.")

# Logout at bottom
if st.button("Logout"):
    st.session_state.is_logged_in = False
    st.rerun()
        
