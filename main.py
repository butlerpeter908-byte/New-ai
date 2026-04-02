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

# ================= 2. THE ULTIMATE CSS FIX (FORCED VISIBILITY) =================
st.set_page_config(page_title="New AI 🤖", layout="wide", initial_sidebar_state="collapsed")

st.markdown(f"""
    <style>
    /* Sabse pehle extra space aur default headers khatam */
    .block-container {{ padding-top: 0.5rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* CUSTOM FLOATING MENU BUTTON (☰) - 100% VISIBLE ON MOBILE */
    /* Hum asali button ko hi customize karke top par la rahe hain */
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00ff88 !important; /* Neon Green */
        color: black !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        width: 50px !important;
        height: 50px !important;
        z-index: 9999999 !important;
        border-radius: 10px !important;
        box-shadow: 0px 0px 15px #00ff88 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 2px solid white !important;
    }}

    /* Ensuring the icon inside is black and visible */
    button[data-testid="stSidebarCollapse"] svg {{
        fill: black !important;
        width: 30px !important;
        height: 30px !important;
    }}

    /* WhatsApp Style Bubbles */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; padding: 15px; margin-top: 60px; }}
    .user-bubble {{
        background-color: #005c4b; color: white; padding: 12px; 
        border-radius: 15px 15px 0px 15px; align-self: flex-end; max-width: 85%;
    }}
    .ai-bubble {{
        background-color: #202c33; color: white; padding: 12px; 
        border-radius: 15px 15px 15px 0px; align-self: flex-start; max-width: 85%;
        border-left: 4px solid #00a884;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. PERSISTENT SESSION LOGIC =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

# --- LOGIN / SIGN UP PAGE ---
if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; color:white; padding-top:80px;">', unsafe_allow_html=True)
    st.title("🔐 Welcome to New AI")
    t1, t2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
    with t1:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Wrong details!")
    with t2:
        nu = st.text_input("New Username", key="reg_user")
        np = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register", use_container_width=True):
            st.session_state.user_db[nu] = np; st.success("Account Ready!")
    st.stop()

# ================= 4. SIDEBAR SETTINGS (RE-ADDED ALL PAGES) =================
with st.sidebar:
    st.title("🤖 New AI Menu")
    st.write(f"Logged as: **{st.session_state.current_user}**")
    st.markdown("---")
    menu = st.radio("Navigation", [
        "💬 Chat", 
        "👤 About Creator", 
        "📩 Feedback", 
        "🛡️ Privacy Policy", 
        "📄 Terms & Conditions"
    ])
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ================= 5. MAIN CONTENT =================
if menu == "💬 Chat":
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Message New AI...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif menu == "📩 Feedback":
    st.header("📩 Feedback")
    fb = st.text_area("Write to Siddique...")
    if st.button("Send"):
        try:
            msg = MIMEText(fb); msg['Subject']='New AI Feedback'; msg['From']=MY_GMAIL; msg['To']=MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Sent to Siddique's Gmail! ✅")
        except: st.error("Email Error.")

elif menu == "🛡️ Privacy Policy":
    st.header("🛡️ Privacy Policy")
    st.write("Professional English: We ensure that your chat data is secure and session-based.")

elif menu == "📄 Terms & Conditions":
    st.header("📄 Terms")
    st.write("Professional English: Usage must follow ethical guidelines set by the developer.")

elif menu == "👤 About Creator":
    st.header("👤 Creator")
    st.info(f"Designed and Developed by: **{CREATOR_NAME}**")
