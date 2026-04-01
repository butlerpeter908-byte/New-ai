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

# ================= 2. UI & VISIBILITY CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0.5rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* Custom Floating Menu Button 'M' */
    button[data-testid="stSidebarCollapse"] {{
        opacity: 0.0 !important; /* Real button is hidden but clickable */
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        width: 70px !important;
        height: 70px !important;
        z-index: 9999999 !important;
    }}

    .custom-menu-btn {{
        position: fixed;
        top: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background-color: #00ff88;
        color: black;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 24px;
        z-index: 9999998;
        box-shadow: 0px 0px 20px #00ff88;
        border: 3px solid white;
        pointer-events: none;
    }}

    /* WhatsApp Style Bubbles */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; padding: 10px; margin-top: 70px; }}
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
    
    <div class="custom-menu-btn">M</div>
    """, unsafe_allow_html=True)

# ================= 3. AUTHENTICATION (BOTH OPTIONS) =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; color:white; padding-top:80px;">', unsafe_allow_html=True)
    st.title("🔐 Welcome to New AI")
    st.write(f"Developed by {CREATOR_NAME}")
    
    # Dono Options wapas aa gaye!
    tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create Account"])
    
    with tab_login:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Login Now", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else:
                st.error("Invalid Details!")

    with tab_signup:
        nu = st.text_input("New Username", key="s_u")
        np = st.text_input("New Password", type="password", key="s_p")
        if st.button("Register Account", use_container_width=True):
            if nu and np:
                st.session_state.user_db[nu] = np
                st.success("Account Created! Go to Sign In tab.")
            else:
                st.warning("Please fill all details.")
    st.stop()

# ================= 4. SIDEBAR SETTINGS (ONLY AFTER LOGIN) =================
with st.sidebar:
    st.title("🤖 SETTINGS")
    st.write(f"User: **{st.session_state.current_user}**")
    st.markdown("---")
    menu = st.radio("Go to:", ["💬 Chat", "👤 About Creator", "📩 Feedback", "🛡️ Privacy Policy", "📄 Terms"])
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ================= 5. PAGE CONTENT (ENGLISH) =================
if menu == "💬 Chat":
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
    fb = st.text_area("How can we improve?")
    if st.button("Submit"):
        try:
            msg = MIMEText(fb); msg['Subject']='New AI Feedback'; msg['From']=MY_GMAIL; msg['To']=MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Sent to Siddique's Gmail! ✅")
        except: st.error("Mail Error.")

elif menu == "🛡️ Privacy Policy":
    st.header("🛡️ Privacy Policy")
    st.write("Professional English: We ensure that your session data is temporary and secure.")

elif menu == "📄 Terms":
    st.header("📄 Terms & Conditions")
    st.write("Professional English: Use this AI for ethical and legal purposes only.")

elif menu == "👤 About Creator":
    st.header("👤 About")
    st.info(f"Designed and Developed by: **{CREATOR_NAME}**")
    
