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

# ================= 2. UI CSS (RIGHT SIDEBAR & FLOATING BUTTON) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Remove default headers & spacing */
    .block-container {{ padding-top: 1rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* RIGHT SIDEBAR LOGIC */
    /* Note: Streamlit's default sidebar is left, but we force button to the Right */
    
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00ff88 !important;
        color: black !important;
        border-radius: 50% !important;
        position: fixed !important;
        top: 20px !important;
        right: 20px !important; /* SHIFTED TO RIGHT */
        left: auto !important;
        width: 60px !important;
        height: 60px !important;
        z-index: 999999 !important;
        box-shadow: 0px 0px 15px #00ff88 !important;
        border: 2px solid white !important;
    }}

    /* WhatsApp Style Bubbles */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; padding: 10px; margin-top: 60px; }}
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

# ================= 3. AUTHENTICATION =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; color:white; padding-top:80px;">', unsafe_allow_html=True)
    st.title("🔐 New AI Login")
    t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Sign In", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
    with t2:
        nu = st.text_input("New User", key="r_u")
        np = st.text_input("New Pass", type="password", key="r_p")
        if st.button("Create Account", use_container_width=True):
            st.session_state.user_db[nu] = np; st.success("Created!")
    st.stop()

# ================= 4. SIDEBAR MENU (RIGHT BORDERED) =================
with st.sidebar:
    st.title("🤖 New AI Settings")
    st.markdown(f"**Hello, {st.session_state.current_user}**")
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

# ================= 5. PAGE CONTENT =================
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

elif menu == "📩 Feedback":
    st.header("📩 Feedback")
    fb = st.text_area("Write to Siddique...")
    if st.button("Send"):
        try:
            msg = MIMEText(fb); msg['Subject']='App Feedback'; msg['From']=MY_GMAIL; msg['To']=MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Sent to Siddique's Gmail! ✅")
        except: st.error("Error.")

elif menu == "🛡️ Privacy Policy":
    st.header("🛡️ Privacy Policy")
    st.write("We ensure high-level security for your session data. No logs are stored on public servers.")

elif menu == "📄 Terms & Conditions":
    st.header("📄 Terms & Conditions")
    st.write("Professional Terms: Usage of this AI must comply with community guidelines.")

elif menu == "👤 About Creator":
    st.header("👤 About Creator")
    st.info(f"Developed by: **{CREATOR_NAME}**")
