import streamlit as st
from groq import Groq
import smtplib
import random
import time
from email.mime.text import MIMEText
from datetime import datetime
import pytz

# ================= 1. SETUP & CONFIG =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

# Client Initialization
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Siddique AI 🤖", layout="wide")

# Indian Standard Time Function
def get_ist_time():
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime('%Y-%m-%d %I:%M:%S %p')

# ================= 2. ADVANCED UI STYLING =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { 
        background: linear-gradient(-45deg, #0f172a, #051937, #004d40, #0d1117);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #e0e0e0 !important;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Chat Input Styling */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 30px !important;
        left: 5% !important;
        right: 5% !important;
        width: 90% !important;
        z-index: 9999 !important;
        background: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(12px);
        border: 1px solid #00ff88;
        border-radius: 15px;
    }

    .welcome-card {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #00ff88;
        border-radius: 25px;
        padding: 40px;
        text-align: center;
    }
    
    .note-text {
        color: #ffcc00;
        font-size: 14px;
        font-style: italic;
        margin-top: 10px;
        border: 1px solid rgba(255, 204, 0, 0.3);
        padding: 5px 10px;
        border-radius: 8px;
        display: inline-block;
    }

    .user-msg { background: #00ff88; color: #000; padding: 12px; border-radius: 15px 15px 0 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .ai-msg { background: #1e293b; color: #fff; padding: 12px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 5px solid #00d2ff; max-width: 85%; }
    
    .main .block-container { padding-bottom: 150px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION STATE MANAGEMENT =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "fb_sent" not in st.session_state: st.session_state.fb_sent = False

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN INTERFACE =================
if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><div style="font-size:45px; font-weight:900; color:#00ff88;">SIDDIQUE AI</div><p>Professional Secure Access</p><div class="note-text"><b>Note:</b> Use Dark Mode theme for best experience 🌙</div></div>', unsafe_allow_html=True)
    st.write("")
    
    email = st.text_input("Aapka Gmail ID:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Send Access PIN", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Access Code", f"Aapka Secret PIN: {otp}"):
                    st.session_state.generated_otp = otp
                    st.session_state.user_email = email
                    st.session_state.otp_sent = True
                    st.rerun()
            else: st.error("Please enter a valid @gmail.com address")
    else:
        st.success(f"PIN sent to {st.session_state.user_email}")
        otp_in = st.text_input("Enter PIN:", type="password")
        
        col_log, col_back = st.columns(2)
        with col_log:
            if st.button("Verify & Launch", use_container_width=True):
                if otp_in == st.session_state.generated_otp: 
                    notification = f"User: {st.session_state.user_email}\nTime (IST): {get_ist_time()}"
                    send_mail(MY_GMAIL, "New Login 🚨", notification)
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Incorrect PIN!")
        with col_back:
            if st.button("Edit Email", use_container_width=True):
                st.session_state.otp_sent = False
                st.rerun()
    st.stop()

# ================= 5. MAIN APP INTERFACE =================
with st.sidebar:
    st.markdown(f"### 👤 Profile\n`{st.session_state.user_email}`")
    st.divider()
    if st.button("🚪 Logout Session", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "🛡️ Account & Privacy", "📩 Support"])

# --- CHAT LOGIC ---
with tab_chat:
    chat_holder = st.container()
    with chat_holder:
        for m in st.session_state.messages:
            div_style = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div_style}">{m["content"]}</div>', unsafe_allow_html=True)

    user_query = st.chat_input("Ask me anything...")
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with chat_holder: st.markdown(f'<div class="user-msg">{user_query}</div>', unsafe_allow_html=True)
        
        try:
            sys_msg = {"role": "system", "content": f"You are a helpful AI. Created by {CREATOR}."}
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[sys_msg] + st.session_state.messages
            )
            ai_ans = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_ans})
            st.rerun()
        except Exception as e:
            st.error(f"API Error: {e}")

# --- SETTINGS TAB ---
with tab_settings:
    st.header("⚙️ Settings")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.subheader("🛡️ Legal & Privacy")
    with st.expander("Privacy Policy"):
        st.write("Aapka data session-based hai. Logout par history clear ho jati hai.")
    with st.expander("Terms of Service"):
        st.write(f"Developed by {CREATOR} for educational use.")
    with st.expander("About App"):
        st.write(f"**Version**: 1.1.0\n\n**Developer**: {CREATOR}")

    st.markdown("""
        <div style="background:rgba(0,255,136,0.1); padding:20px; border-radius:15px; border:1px solid #00ff88;">
        <h4>📲 Install on Home Screen</h4>
        Browser menu (3 dots ⋮) -> <b>Add to Home Screen</b>
        </div>
    """, unsafe_allow_html=True)

# --- FEEDBACK TAB ---
with tab_feedback:
    if st.session_state.fb_sent:
        st.success("Message sent to Siddique!")
        if st.button("Write Another"): st.session_state.fb_sent = False; st.rerun()
    else:
        st.header("📩 Contact Support")
        fb_text = st.text_area("Message...", height=150)
        if st.button("Send to Creator", use_container_width=True):
            if fb_text:
                fb_msg = f"User: {st.session_state.user_email}\nTime: {get_ist_time()}\n\n{fb_text}"
                if send_mail(MY_GMAIL, "App Feedback", fb_msg):
                    st.session_state.fb_sent = True
                    st.rerun()
            
