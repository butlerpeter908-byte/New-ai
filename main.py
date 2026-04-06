import streamlit as st
from groq import Groq
import smtplib
import random
import time
from email.mime.text import MIMEText

# ================= 1. SETUP =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Siddique AI 🤖", layout="wide")

# ================= 2. PREMIUM UI =================
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
    
    .install-section {
        background: rgba(0, 255, 136, 0.05);
        border: 1px solid #00ff88;
        border-radius: 12px;
        padding: 15px;
        margin-top: 20px;
    }

    .user-msg { background: #00ff88; color: #000; padding: 12px; border-radius: 15px 15px 0 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .ai-msg { background: #1e293b; color: #fff; padding: 12px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 5px solid #00d2ff; max-width: 85%; }
    
    .main .block-container { padding-bottom: 150px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
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

# ================= 4. LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><div style="font-size:45px; font-weight:900; color:#00ff88;">SIDDIQUE AI</div><p>Secure Professional Access</p></div>', unsafe_allow_html=True)
    st.write("")
    email = st.text_input("Aapka Gmail ID:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Send Access PIN", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Access Code", f"Aapka Secret PIN: {otp}"):
                    st.session_state.generated_otp = otp; st.session_state.user_email = email
                    st.session_state.otp_sent = True; st.rerun()
    else:
        st.success(f"PIN sent to {st.session_state.user_email}")
        otp_in = st.text_input("Enter PIN:", type="password")
        if st.button("Verify & Launch AI", use_container_width=True):
            if otp_in == st.session_state.generated_otp: 
                notification_body = f"Alert! Ek naye bande ne login kiya hai.\n\nUser Email: {st.session_state.user_email}\nTime: {time.ctime()}"
                send_mail(MY_GMAIL, "New Login Detected 🚨", notification_body)
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Incorrect PIN!")
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.markdown(f"### Logged in as: \n`{st.session_state.user_email}`")

tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "⚙️ Account & Privacy", "📩 Support"])

# --- CHAT TAB ---
with tab_chat:
    chat_box = st.container()
    with chat_box:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Type here...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        with chat_box: st.markdown(f'<div class="user-msg">{q}</div>', unsafe_allow_html=True)
        try:
            instruction = {"role": "system", "content": f"You are a helpful AI. ONLY if asked about creator/owner, say {CREATOR} made you."}
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[instruction] + st.session_state.messages)
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            with chat_box: st.markdown(f'<div class="ai-msg">{ans}</div>', unsafe_allow_html=True)
            st.rerun()
        except: pass

# --- SETTINGS / ACCOUNT TAB (Includes Install Button) ---
with tab_settings:
    st.header("⚙️ Account Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All Chat", use_container_width=True):
            st.session_state.messages = []; st.rerun()
    with col2:
        if st.button("🚪 Logout Session", use_container_width=True):
            st.session_state.logged_in = False; st.session_state.otp_sent = False; st.rerun()

    # --- INSTALL SECTION INSIDE SETTINGS ---
    st.markdown('<div class="install-section"><h3>📲 Install Siddique AI on Phone</h3>', unsafe_allow_html=True)
    st.write("Ise app ki tarah use karne ke liye browser menu (3 dots ⋮) mein jaakar **'Add to Home Screen'** ya **'Install App'** par click karein.")
    if st.button("Download & Install (Setup)", use_container_width=True):
        st.success("App configuration ready! Browser menu se 'Add to Home Screen' karein.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.header("🛡️ Privacy & Terms")
    with st.expander("🛡️ Privacy Policy"):
        st.write("Aapka chat data session-based hai. Logout karte hi delete ho jata hai.")
    with st.expander("📄 Terms and Conditions"):
        st.write(f"Is AI ko {CREATOR} ne develop kiya hai.")
    st.write(f"**Version**: 1.0.4 | **Developed by**: {CREATOR}")

# --- FEEDBACK TAB ---
with tab_feedback:
    if st.session_state.fb_sent:
        st.success("Feedback sent successfully!")
        if st.button("Send Another"): st.session_state.fb_sent = False; st.rerun()
    else:
        st.header("📩 Feedback")
        fb = st.text_area("Write your message...", height=150)
        if st.button("Submit to Siddique", use_container_width=True):
            if fb and send_mail(MY_GMAIL, "Feedback", f"From: {st.session_state.user_email}\n{fb}"):
                st.session_state.fb_sent = True; st.rerun()
                
