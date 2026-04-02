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

# ================= 2. CUSTOM HEADER & UI CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Spacing and Background Fix */
    .block-container {{ padding-top: 0rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* FIXED TOP HEADER (ALWAYS VISIBLE) */
    .top-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 65px;
        background: rgba(0, 255, 136, 0.15); backdrop-filter: blur(15px);
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 15px; z-index: 99999; border-bottom: 2px solid #00ff88;
    }}
    .logo-text {{ color: #00ff88; font-size: 22px; font-weight: bold; }}
    .profile-section {{ display: flex; align-items: center; gap: 10px; color: white; }}

    /* WhatsApp Bubbles Styling */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; padding: 15px; margin-top: 80px; }}
    .user-bubble {{
        background-color: #005c4b; color: white; padding: 12px; 
        border-radius: 15px 15px 0px 15px; align-self: flex-end; max-width: 85%;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }}
    .ai-bubble {{
        background-color: #202c33; color: white; padding: 12px; 
        border-radius: 15px 15px 15px 0px; align-self: flex-start; max-width: 85%;
        border-left: 4px solid #00a884;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. PERSISTENT SESSION =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "active_page" not in st.session_state: st.session_state.active_page = "💬 Chat"

# --- LOGIN / SIGN UP ---
if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; color:white; padding-top:80px;">', unsafe_allow_html=True)
    st.title("🔐 Welcome to New AI")
    t1, t2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Enter AI", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
            else: st.error("Wrong Username/Password!")
    with t2:
        nu = st.text_input("New Username", key="s_u")
        np = st.text_input("New Password", type="password", key="s_p")
        if st.button("Register Account", use_container_width=True):
            st.session_state.user_db[nu] = np; st.success("Account Created! Please Sign In.")
    st.stop()

# ================= 4. CUSTOM TOP NAVIGATION (INSTEAD OF SIDEBAR) =================
# Header display
st.markdown(f'''
    <div class="top-header">
        <div class="logo-text">New AI 🤖</div>
        <div class="profile-section">
            <span>👤 {st.session_state.current_user}</span>
        </div>
    </div>
''', unsafe_allow_html=True)

# Navigation Buttons at the top
cols = st.columns([1,1,1,1,1])
with cols[0]:
    if st.button("💬 Chat", use_container_width=True): st.session_state.active_page = "💬 Chat"
with cols[1]:
    if st.button("📩 Feed", use_container_width=True): st.session_state.active_page = "📩 Feed"
with cols[2]:
    if st.button("🛡️ Legal", use_container_width=True): st.session_state.active_page = "🛡️ Legal"
with cols[3]:
    if st.button("🗑️ Clear", use_container_width=True): st.session_state.messages = []; st.rerun()
with cols[4]:
    if st.button("🚪 Out", use_container_width=True): st.session_state.logged_in = False; st.rerun()

st.markdown("---")

# ================= 5. MAIN CONTENT =================
page = st.session_state.active_page

if page == "💬 Chat":
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

elif page == "📩 Feed":
    st.header("📩 Feedback")
    fb = st.text_area("How can we improve?")
    if st.button("Send to Siddique"):
        try:
            msg = MIMEText(f"User: {st.session_state.current_user}\nFeedback: {fb}")
            msg['Subject']='New AI Feedback'; msg['From']=MY_GMAIL; msg['To']=MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Feedback sent! ✅")
        except: st.error("Email Error.")

elif page == "🛡️ Legal":
    st.subheader("👤 About Creator")
    st.info(f"Designed and Developed by: **{CREATOR_NAME}**")
    st.markdown("---")
    st.subheader("🛡️ Privacy Policy")
    st.write("We ensure high-level security for your chat data. No logs are stored on public servers.")
    st.markdown("---")
    st.subheader("📄 Terms & Conditions")
    st.write("Usage must comply with ethical AI guidelines and legal policies.")
