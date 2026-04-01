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

# ================= 2. THE ULTIMATE VISIBILITY CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Sabse pehle extra space khatam */
    .block-container {{ padding-top: 0.5rem !important; }}
    header, footer {{visibility: hidden !important;}}
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}

    /* JREEL JUGAAD: Making the real sidebar button invisible but huge */
    /* And placing our OWN visible button over it */
    
    button[data-testid="stSidebarCollapse"] {{
        opacity: 0.1 !important; /* Halka sa dikhega background mein */
        position: fixed !important;
        top: 20px !important;
        right: 20px !important;
        width: 70px !important;
        height: 70px !important;
        z-index: 9999999 !important;
    }}

    /* CUSTOM VISIBLE NEON BUTTON (This is what you will see) */
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
        pointer-events: none; /* Clicking passes through to the real button below */
    }}

    /* WhatsApp Bubbles Styling */
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

# ================= 3. LOGIC & AUTH =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.markdown('<div style="text-align: center; color:white; padding-top:100px;">', unsafe_allow_html=True)
    st.title("🔐 New AI Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Enter AI World", use_container_width=True):
        if u in st.session_state.user_db and st.session_state.user_db[u] == p:
            st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
    st.stop()

# ================= 4. SIDEBAR (AB YEH RIGHT SE KHULEGA) =================
with st.sidebar:
    st.title("🤖 NEW AI SETTINGS")
    st.write(f"Logged as: **{st.session_state.current_user}**")
    st.markdown("---")
    menu = st.radio("SELECT PAGE:", [
        "💬 Chat", 
        "👤 About Developer", 
        "📩 Feedback", 
        "🛡️ Privacy Policy", 
        "📄 Terms & Conditions"
    ])
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ================= 5. CONTENT PAGES (PROFESSIONAL ENGLISH) =================
if menu == "💬 Chat":
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Write something to New AI...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif menu == "👤 About Developer":
    st.header("👤 About Creator")
    st.info(f"Designed and Developed by: **{CREATOR_NAME}**")

elif menu == "🛡️ Privacy Policy":
    st.header("🛡️ Privacy Policy")
    st.write("We ensure that your chat data is temporary and not stored on any public cloud databases. Your security is our priority.")

elif menu == "📄 Terms & Conditions":
    st.header("📄 Terms of Use")
    st.write("By using this AI, you agree to use it for ethical purposes. The developer is not responsible for AI-generated responses.")

elif menu == "📩 Feedback":
    st.header("📩 User Feedback")
    fb = st.text_area("How's your experience?")
    if st.button("Submit"):
        try:
            msg = MIMEText(fb); msg['Subject']='New AI Feedback'; msg['From']=MY_GMAIL; msg['To']=MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s: s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Feedback sent to Siddique! ✅")
        except: st.error("Mail Error.")
            
