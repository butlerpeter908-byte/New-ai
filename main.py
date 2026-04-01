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

# ================= 2. ULTRA-VISIBLE UI CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 2rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* NEON SUPER MENU BUTTON */
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00ff88 !important; /* Neon Green */
        color: #000000 !important;        /* Black Icon */
        border-radius: 12px !important;
        position: fixed !important;
        top: 30px !important;    /* Kafi neeche */
        left: 25px !important;   /* Margin badha di */
        z-index: 999999 !important;
        width: 60px !important;  /* Bada size */
        height: 50px !important;
        box-shadow: 0px 0px 15px #00ff88 !important; /* Glowing effect */
        display: block !important;
    }}

    /* WhatsApp Bubbles */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; padding: 15px; }}
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

# --- LOGIN / SIGN UP ---
if not st.session_state.logged_in:
    st.markdown('<div style="padding-top: 80px; text-align: center; color:white;">', unsafe_allow_html=True)
    st.title("🔐 New AI Login")
    t1, t2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login Now", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register", use_container_width=True):
            st.session_state.user_db[nu] = np; st.success("Done!")
    st.stop()

# ================= 4. SIDEBAR MENU (POST-LOGIN) =================
with st.sidebar:
    st.title("🤖 New AI Settings")
    st.write(f"Logged as: **{st.session_state.current_user}**")
    menu = st.radio("Go to:", ["💬 Chat", "👤 About Creator", "📩 Feedback", "🛡️ Privacy", "📄 Terms"])
    st.markdown("---")
    if st.button("🗑️ Clear History"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# ================= 5. CONTENT =================
if menu == "💬 Chat":
    st.markdown('<div style="color:white; text-align:center; margin-top:50px;"><h3>🤖 Welcome to New AI</h3></div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Ask something...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif menu == "📩 Feedback":
    st.header("📩 Feedback")
    fb = st.text_area("Message:")
    if st.button("Submit to Siddique"):
        try:
            msg = MIMEText(fb); msg['Subject']='New AI Feedback'; msg['From']=MY_GMAIL; msg['To']=MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Sent! ✅")
        except: st.error("Error.")

elif menu == "🛡️ Privacy":
    st.header("🛡️ Privacy Policy")
    st.write("Your data is safe and not shared with third parties.")

elif menu == "📄 Terms":
    st.header("📄 Terms of Use")
    st.write("Use this AI responsibly for legal purposes only.")

elif menu == "👤 About Creator":
    st.header("👤 About")
    st.info(f"Created by: **{CREATOR_NAME}**")
            
