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

# ================= 2. FIXED UI & BUTTON CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* CUSTOM TOP NAVIGATION FOR MOBILE */
    .mobile-header {{
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: rgba(0, 255, 136, 0.2); backdrop-filter: blur(10px);
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 20px; z-index: 99999; border-bottom: 1px solid #00ff88;
    }}
    .menu-text {{ color: #00ff88; font-weight: bold; font-size: 20px; }}

    /* WhatsApp Style Bubbles */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; padding: 15px; margin-top: 70px; }}
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

# ================= 3. PERSISTENT LOGIN LOGIC =================
# Refresh pe logout na ho isliye session state ko strong kiya hai
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

# --- LOGIN / SIGN UP PAGE ---
if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; color:white; padding-top:80px;">', unsafe_allow_html=True)
    st.title("🔐 Welcome to New AI")
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
    
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Wrong details!")
            
    with tab2:
        nu = st.text_input("Choose Username")
        np = st.text_input("Choose Password", type="password")
        if st.button("Register"):
            st.session_state.user_db[nu] = np; st.success("Account Ready!")
    st.stop()

# ================= 4. SIDEBAR SETTINGS =================
# Ab sidebar ke sath-sath top header bhi hai visibility ke liye
with st.sidebar:
    st.title("🤖 New AI Menu")
    st.write(f"User: **{st.session_state.current_user}**")
    st.markdown("---")
    menu = st.radio("Pages", ["💬 Chat", "👤 About Developer", "📩 Feedback", "🛡️ Privacy", "📄 Terms"])
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ================= 5. MAIN PAGE CONTENT =================
if menu == "💬 Chat":
    st.markdown('<div class="mobile-header"><span class="menu-text">New AI 🤖</span></div>', unsafe_allow_html=True)
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
    st.header("📩 Feedback")
    fb = st.text_area("Write to Siddique...")
    if st.button("Send"):
        try:
            msg = MIMEText(fb); msg['Subject']='New AI Feedback'; msg['From']=MY_GMAIL; msg['To']=MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Feedback Sent! ✅")
        except: st.error("Email Error.")

elif menu == "🛡️ Privacy":
    st.header("🛡️ Privacy Policy")
    st.write("Professional English: We ensure your chat data is secure and temporary.")

elif menu == "📄 Terms":
    st.header("📄 Terms of Use")
    st.write("Professional English: Usage must comply with ethical AI guidelines.")

elif menu == "👤 About Developer":
    st.header("👤 Creator")
    st.info(f"Designed and Developed by: **{CREATOR_NAME}**")
    
