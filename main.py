import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & CREDENTIALS =================
GROQ_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. FIXED TOP MENU CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Sabse pehle khali space aur headers khatam */
    .block-container {{ padding-top: 0rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* CUSTOM TOP NAV BAR (Ab ye 100% dikhega) */
    .top-nav {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: rgba(0, 255, 136, 0.1);
        backdrop-filter: blur(10px);
        padding: 10px;
        display: flex;
        justify-content: space-around;
        z-index: 9999;
        border-bottom: 1px solid #00ff88;
    }}

    /* WhatsApp Style Bubbles */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; padding: 20px; margin-top: 60px; }}
    .user-bubble {{
        background-color: #005c4b; color: white; padding: 12px; 
        border-radius: 15px 15px 0px 15px; align-self: flex-end; max-width: 85%;
    }}
    .ai-bubble {{
        background-color: #202c33; color: white; padding: 12px; 
        border-radius: 15px 15px 15px 0px; align-self: flex-start; max-width: 85%;
        border-left: 4px solid #00a884;
    }}

    /* Mobile Text Input Fix */
    .stChatInput {{ margin-bottom: 20px !important; }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "page" not in st.session_state: st.session_state.page = "💬 Chat"

# --- LOGIN / SIGN UP ---
if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; color:white; padding-top:80px;">', unsafe_allow_html=True)
    st.title("🔐 New AI Login")
    t1, t2 = st.tabs(["🔑 Sign In", "📝 Register"])
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
    with t2:
        nu = st.text_input("New User")
        np = st.text_input("New Pass", type="password")
        if st.button("Create Account"):
            st.session_state.user_db[nu] = np; st.success("Done! Login now.")
    st.stop()

# ================= 4. NEW TOP NAVIGATION BUTTONS =================
# Ab hum sidebar nahi use karenge, seedha screen par buttons denge
cols = st.columns(5)
with cols[0]:
    if st.button("💬 Chat", use_container_width=True): st.session_state.page = "💬 Chat"
with cols[1]:
    if st.button("👤 About", use_container_width=True): st.session_state.page = "👤 About"
with cols[2]:
    if st.button("📩 Feed", use_container_width=True): st.session_state.page = "📩 Feed"
with cols[3]:
    if st.button("🗑️ Clear", use_container_width=True): st.session_state.messages = []; st.rerun()
with cols[4]:
    if st.button("🚪 Out", use_container_width=True): st.session_state.logged_in = False; st.rerun()

st.markdown("---")

# ================= 5. PAGE CONTENT =================
menu = st.session_state.page

if menu == "💬 Chat":
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Message Siddique's AI...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif menu == "📩 Feed":
    st.header("📩 Feedback")
    fb = st.text_area("Write feedback for Siddique...")
    if st.button("Submit"):
        try:
            msg = MIMEText(fb); msg['Subject']='App Feedback'; msg['From']=MY_GMAIL; msg['To']=MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Sent to Gmail! ✅")
        except: st.error("Email Error.")

elif menu == "👤 About":
    st.header("👤 Creator")
    st.info(f"App Mastermind: **{CREATOR_NAME}**")
                
