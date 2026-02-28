import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ================= 1. IDENTITY & CREDENTIALS =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohammad Saif"

client = Groq(api_key=GROQ_KEY)

# ================= 2. SESSION & LOGIN SYSTEM =================
if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"} # Default user

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Login / Sign Up Page ---
if not st.session_state.logged_in:
    st.title("🔐 Welcome to New AI")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab2:
        new_u = st.text_input("Choose Username", key="reg_u")
        new_p = st.text_input("Choose Password", type="password", key="reg_p")
        if st.button("Create Account"):
            if new_u and new_p:
                st.session_state.users[new_u] = new_p
                st.success("Account created! Now go to Login.")
            else: st.error("Details fill karein.")
            
    with tab1:
        u = st.text_input("Username", key="log_u")
        p = st.text_input("Password", type="password", key="log_p")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login"):
                if u in st.session_state.users and st.session_state.users[u] == p:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
                else: st.error("Wrong details!")
        with c2:
            if st.button("Forgot Password"):
                if u in st.session_state.users:
                    st.info(f"Password for {u}: {st.session_state.users[u]}")
                else: st.warning("Username not found.")
    st.stop()

# ================= 3. PERMANENT SIDEBAR MENU =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

with st.sidebar:
    st.title(f"🤖 New AI Menu")
    st.write(f"User: **{st.session_state.current_user}**")
    st.markdown("---")
    
    # Ye raha wo menu jo kabhi nahi hatega
    menu = st.radio("📌 Navigation", 
                    ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ================= 4. WHATSAPP STYLE UI & PAGES =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {background-color: #0b141a; padding-top: 1rem;}
    .user-bubble { background-color: #005c4b; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; margin: 8px 0; max-width: 75%; float: right; clear: both; box-shadow: 0 1px 0.5px rgba(0,0,0,0.13); }
    .ai-bubble { background-color: #202c33; color: white; padding: 10px 15px; border-radius: 15px 15px 15px 0; margin: 8px 0; max-width: 75%; float: left; clear: both; border-left: 4px solid #00a884; box-shadow: 0 1px 0.5px rgba(0,0,0,0.13); }
</style>
""", unsafe_allow_html=True)

# --- Logic for Menu Screens ---
if menu == "Chat":
    st.title("💬 WhatsApp Chat")
    if "messages" not in st.session_state: st.session_state.messages = []

    for m in st.session_state.messages:
        div = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    prompt = st.chat_input("Siddique Mohammad Saif ka AI ready hai...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Identity System Prompt
        sys_msg = f"Your name is New AI. You were created by {CREATOR_NAME}. Answer strictly as this persona."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]
        )
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.info(f"This AI is proudly created and maintained by **{CREATOR_NAME}**.")

elif menu == "Feedback":
    st.header("📝 Feedback")
    f_text = st.text_area("Humein batayein ki aapko ye AI kaisa laga:")
    if st.button("Submit Feedback"):
        try:
            msg = MIMEText(f"Feedback from {st.session_state.current_user}: {f_text}")
            msg['Subject'] = 'New AI Feedback'
            msg['From'] = MY_GMAIL
            msg['To'] = MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(MY_GMAIL, APP_PASS)
                server.send_message(msg)
            st.success("Thanks for feedback")
        except: st.error("Email sending failed.")

elif menu == "Privacy Policy":
    st.header("🔒 Privacy Policy")
    st.write("Hum aapki privacy ka dhyan rakhte hain. Aapka data humare servers par save nahi hota.")

elif menu == "Terms & Conditions":
    st.header("⚖️ Terms & Conditions")
    st.write("Is AI ka upyog sirf achhe kamo ke liye karein. Galat bhasha ka upyog na karein.")
    
