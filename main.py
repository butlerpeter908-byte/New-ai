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

# ================= 2. MOBILE-OPTIMIZED UI CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Removing Top Space */
    .block-container {{ padding-top: 1rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* FIXED MOBILE MENU BUTTON (Adjusted Margins) */
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00a884 !important;
        color: white !important;
        border-radius: 8px !important;
        position: fixed !important;
        top: 20px !important;    /* Thoda neeche kiya */
        left: 20px !important;   /* Thoda right side margin di */
        z-index: 999999 !important;
        padding: 10px !important;
        display: block !important;
    }}

    /* WhatsApp Bubbles */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; padding: 10px; }}
    .user-bubble {{
        background-color: #005c4b; color: white; padding: 12px; 
        border-radius: 15px 15px 0px 15px; margin: 5px; 
        align-self: flex-end; max-width: 85%;
    }}
    .ai-bubble {{
        background-color: #202c33; color: white; padding: 12px; 
        border-radius: 15px 15px 15px 0px; margin: 5px; 
        align-self: flex-start; max-width: 85%;
        border-left: 4px solid #00a884;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

# --- LOGIN / SIGN UP PAGE ---
if not st.session_state.logged_in:
    st.markdown('<div style="padding-top: 60px; text-align: center;">', unsafe_allow_html=True)
    st.title("🔐 Welcome to New AI")
    t1, t2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Sign In", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
    with t2:
        nu = st.text_input("New Username", key="s_u")
        np = st.text_input("New Password", type="password", key="s_p")
        if st.button("Register", use_container_width=True):
            st.session_state.user_db[nu] = np; st.success("Account Created!")
    st.stop()

# ================= 4. SIDEBAR MENU (POST-LOGIN) =================
with st.sidebar:
    st.title("🤖 New AI Menu")
    st.write(f"User: **{st.session_state.current_user}**")
    menu = st.radio("Navigation", ["💬 Chat", "👤 About Creator", "📩 Feedback", "🛡️ Privacy Policy", "📄 Terms"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# ================= 5. PAGE CONTENT =================
if menu == "💬 Chat":
    st.markdown('<div style="color:white; text-align:center; padding-top:30px;"><h3>🤖 Welcome to New AI</h3></div>', unsafe_allow_html=True)
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
    fb_text = st.text_area("Tell us what you think...")
    if st.button("Submit"):
        try:
            msg = MIMEText(f"Feedback: {fb_text}"); msg['Subject'] = 'New AI Feedback'; msg['From'] = MY_GMAIL; msg['To'] = MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Sent to Siddique's Gmail! ✅")
        except: st.error("Email Error.")

elif menu == "🛡️ Privacy Policy":
    st.header("🛡️ Privacy Policy")
    st.write("Professional English Privacy Content: We respect your data security.")

elif menu == "📄 Terms":
    st.header("📄 Terms")
    st.write("Professional English Terms Content: Use responsibly.")

elif menu == "👤 About Creator":
    st.header("👤 About")
    st.info(f"Built with ❤️ by **{CREATOR_NAME}**")
