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

# ================= 2. MOBILE-FIRST UI CSS (FORCED VISIBILITY) =================
# Isse sidebar hamesha mobile par bhi accessible rahega
st.set_page_config(page_title="New AI 🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
    <style>
    /* Sabse pehle khali space khatam */
    .block-container {{ padding-top: 1rem !important; }}
    header, footer {{visibility: hidden !important;}}
    
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* FORCE SHOW SIDEBAR BUTTON */
    section[data-testid="stSidebar"] {{
        background-color: rgba(20, 20, 40, 0.95) !important;
    }}
    
    /* Neon Green Floating Indicator */
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00ff88 !important;
        color: black !important;
        width: 80px !important;
        height: 60px !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 9999999 !important;
        box-shadow: 0px 0px 20px #00ff88 !important;
        border-radius: 10px !important;
    }}

    /* WhatsApp Style */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; padding: 10px; }}
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

# ================= 3. SESSION LOGIC =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

# --- LOGIN / SIGN UP ---
if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; color:white; margin-top:50px;">', unsafe_allow_html=True)
    st.title("🔐 New AI Login")
    t1, t2 = st.tabs(["🔑 Sign In", "📝 Register"])
    with t1:
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("Login"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
    with t2:
        nu = st.text_input("New User")
        np = st.text_input("New Pass", type="password")
        if st.button("Create Account"):
            st.session_state.user_db[nu] = np; st.success("Done! Login now.")
    st.stop()

# ================= 4. PERMANENT SIDEBAR (AFTER LOGIN) =================
with st.sidebar:
    st.title("🤖 NEW AI MENU")
    st.markdown(f"**Welcome, {st.session_state.current_user}**")
    st.markdown("---")
    menu = st.radio("SELECT PAGE:", ["💬 Chat", "👤 About Creator", "📩 Feedback", "🛡️ Privacy", "📄 Terms"])
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True): 
        st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout", use_container_width=True): 
        st.session_state.logged_in = False; st.rerun()

# ================= 5. MAIN CONTENT =================
if menu == "💬 Chat":
    st.markdown('<div style="color:white; text-align:center; padding-top:40px;"><h3>🤖 Chat Mode</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Ask Siddique's AI...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif menu == "📩 Feedback":
    st.header("📩 User Feedback")
    fb = st.text_area("Write your feedback here...")
    if st.button("Send to Siddique"):
        try:
            msg = MIMEText(fb); msg['Subject']='App Feedback'; msg['From']=MY_GMAIL; msg['To']=MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Feedback sent to Siddique! ✅")
        except: st.error("Email error.")

elif menu == "👤 About Creator":
    st.header("👤 Creator")
    st.info(f"Mastermind: **{CREATOR_NAME}**")
