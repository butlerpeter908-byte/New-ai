import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import smtplib
from email.mime.text import MIMEText

# ================= CREDENTIALS & IDENTITY =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohammad Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= AUTHENTICATION SYSTEM =================
if "users" not in st.session_state:
    st.session_state.users = {} 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🤖 Welcome to New AI")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    
    with t2:
        u = st.text_input("New Username", key="reg_u")
        p = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Register"):
            if u and p: 
                st.session_state.users[u] = p
                st.success("Account created! Go to Login.")
            else: st.error("Fill all fields")
            
    with t1:
        lu = st.text_input("Username", key="log_u")
        lp = st.text_input("Password", type="password", key="log_p")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login"):
                if lu in st.session_state.users and st.session_state.users[lu] == lp:
                    st.session_state.logged_in = True
                    st.session_state.current_user = lu
                    st.rerun()
                else: st.error("Invalid credentials")
        with c2:
            if st.button("Forgot Details?"):
                if lu in st.session_state.users:
                    st.info(f"Password for {lu}: {st.session_state.users[lu]}")
                else: st.warning("Username not found.")
    st.stop()

# ================= PERMANENT SIDEBAR MENU =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

with st.sidebar:
    st.title(f"👤 {st.session_state.current_user}")
    # Ye options ab hamesha dikhenge
    menu = st.radio("Menu Options", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    
    st.markdown("---")
    if menu == "About Creator":
        st.info(f"👤 **Creator:** {CREATOR_NAME}")
    elif menu == "Feedback":
        f_msg = st.text_area("Humein batayein:")
        if st.button("Submit Feedback"):
            try:
                msg = MIMEText(f"Feedback from {st.session_state.current_user}: {f_msg}")
                msg['Subject'] = 'New AI Feedback'
                msg['From'] = MY_GMAIL
                msg['To'] = MY_GMAIL
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(MY_GMAIL, APP_PASS)
                    server.send_message(msg)
                st.success("Thanks for feedback")
            except: st.error("Error sending feedback")
    elif menu == "Privacy Policy":
        st.write("🔒 Your privacy is our priority. No data is shared with third parties.")
    elif menu == "Terms & Conditions":
        st.write("⚖️ Use this AI for educational and creative purposes. Avoid misuse.")
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ================= WHATSAPP UI & CHAT SYSTEM =================
if menu == "Chat":
    st.title("🤖 New AI Chat")
    st.markdown("""
    <style>
        header, footer {visibility: hidden;}
        .block-container {background-color: #0b141a;}
        .user-bubble { background-color: #005c4b; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; margin: 8px 0; max-width: 75%; float: right; clear: both; }
        .ai-bubble { background-color: #202c33; color: white; padding: 10px 15px; border-radius: 15px 15px 15px 0; margin: 8px 0; max-width: 75%; float: left; clear: both; border-left: 4px solid #00a884; }
    </style>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state: 
        st.session_state.messages = []

    # Instant display of messages
    for i, m in enumerate(st.session_state.messages):
        cls = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{cls}">{m["content"]}</div>', unsafe_allow_html=True)

    u_input = st.chat_input("Siddique Mohammad Saif ka AI ready hai...")
    if u_input:
        st.session_state.messages.append({"role": "user", "content": u_input})
        # Identity logic
        sys = f"Your name is New AI. You were created by {CREATOR_NAME}. Answer strictly as this persona."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": u_input}]
        )
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
            
