import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & CREDENTIALS =================
GROQ_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" # Your App Password

client = Groq(api_key=GROQ_KEY)

# ================= 2. UI & WHATSAPP STYLING =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    .block-container {{ padding-top: 0rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* WhatsApp Bubbles */
    .chat-container {{ display: flex; flex-direction: column; gap: 10px; }}
    .user-bubble {{
        background-color: #005c4b; color: white; padding: 12px; 
        border-radius: 15px 15px 0px 15px; margin: 5px; 
        align-self: flex-end; max-width: 80%;
    }}
    .ai-bubble {{
        background-color: #202c33; color: white; padding: 12px; 
        border-radius: 15px 15px 15px 0px; margin: 5px; 
        align-self: flex-start; max-width: 80%;
        border-left: 4px solid #00a884;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. LOGIC & SESSIONS =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

# --- LOGIN / SIGN UP ---
if not st.session_state.logged_in:
    st.markdown('<div style="padding-top: 50px; text-align: center;">', unsafe_allow_html=True)
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
    menu = st.radio("Navigation", ["💬 Chat", "👤 About Creator", "📩 Feedback", "🛡️ Privacy Policy", "📄 Terms"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# ================= 5. PROFESSIONAL ENGLISH PAGES =================
if menu == "💬 Chat":
    st.markdown('<div style="color:white; text-align:center; padding:10px;"><h3>🤖 New AI Session</h3></div>', unsafe_allow_html=True)
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
    st.header("📩 Send Feedback")
    fb_text = st.text_area("How can we improve?")
    if st.button("Send to Developer"):
        try:
            msg = MIMEText(f"Feedback from {st.session_state.current_user}:\n\n{fb_text}")
            msg['Subject'] = 'New AI App Feedback'
            msg['From'] = MY_GMAIL
            msg['To'] = MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(MY_GMAIL, APP_PASS)
                server.send_message(msg)
            st.success("Feedback sent directly to Siddique's Gmail! ✅")
        except Exception as e: st.error(f"Error: {e}")

elif menu == "🛡️ Privacy Policy":
    st.header("🛡️ Privacy Policy")
    st.write("""
    **1. Data Collection:** We do not store your personal conversations on our servers permanently. 
    **2. Security:** Your login credentials are encrypted within the session.
    **3. Third-Party:** We use Groq Cloud for processing AI responses.
    """)

elif menu == "📄 Terms":
    st.header("📄 Terms & Conditions")
    st.write("""
    **1. Usage:** Users must not use this AI for illegal activities.
    **2. Responsibility:** The developer is not liable for AI-generated content.
    **3. Agreement:** By using New AI, you agree to these terms.
    """)

elif menu == "👤 About Creator":
    st.header("👤 About Creator")
    st.info(f"Developed & Maintained by **{CREATOR_NAME}**.")
    
