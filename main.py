import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & NEW FAST API KEY =================
# Maine yahan nayi key daal di hai error solve karne ke liye
GROQ_KEY = "gsk_yV8jB6X..." # (Yahan nayi key replace karein)
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohammad Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. REFRESH-PROOF SYSTEM =================
if "user_db" not in st.session_state:
    st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 3. ULTRA CLEAN UI (HIDE FORK, GITHUB, FOOTER) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

# Ye CSS Fork aur Footer ko hide kar degi
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    button[title="View source on GitHub"] {display:none;}
    div[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

# ================= 4. LOGIN PAGE =================
if not st.session_state.logged_in:
    st.title("🔐 Login to New AI")
    t1, t2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Sign In"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Invalid Login")
    with t2:
        nu = st.text_input("New Username", key="s_u")
        np = st.text_input("New Password", type="password", key="s_p")
        if st.button("Register"):
            if nu and np: st.session_state.user_db[nu] = np; st.success("Account Created!")
    st.stop()

# ================= 5. SIDEBAR MENU =================
with st.sidebar:
    st.title("🤖 New AI Menu")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ================= 6. QUICK RESPONSE CHAT =================
if menu == "Chat":
    st.title("💬 New AI")
    st.markdown("""<style>.user-bubble { background-color: #005c4b; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: right; clear: both; } .ai-bubble { background-color: #202c33; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: left; clear: both; border-left: 4px solid #00a884; }</style>""", unsafe_allow_html=True)
    
    for i, m in enumerate(st.session_state.messages):
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant":
            if st.button(f"🔊 Listen", key=f"v_{i}"):
                tts = gTTS(text=m["content"], lang='hi')
                fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
                b64 = base64.b64encode(fp.read()).decode(); st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)

    q = st.chat_input("Welcome to new ai")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            # Quick 8b model for instant response
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[{"role": "system", "content": f"Your name is New AI. Created by {CREATOR_NAME}."}, {"role": "user", "content": q}]
            )
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except Exception:
            st.error("API Key issue! Please update the GROQ_KEY.")

# --- Feedback, About, etc. ---
elif menu == "Feedback":
    st.header("📝 Submit Your Feedback")
    user_feedback = st.text_area("Write your message here...")
    if st.button("Submit"):
        if user_feedback:
            try:
                msg = MIMEText(f"User: {st.session_state.current_user}\nFeedback: {user_feedback}")
                msg['Subject'] = "New AI Feedback"; msg['From'] = MY_GMAIL; msg['To'] = MY_GMAIL
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(MY_GMAIL, APP_PASS); server.send_message(msg)
                st.success("Thanks for feedback")
            except Exception: st.error("Email Error")

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.info(f"Developed by: **{CREATOR_NAME}**")
    
