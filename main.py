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
CREATOR_NAME = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="New AI 🤖", layout="wide")

# ================= 2. MOBILE-OPTIMIZED CSS =================
st.markdown(f"""
    <style>
    :root {{ color-scheme: dark; }}
    header, footer {{ visibility: hidden !important; }}
    
    /* Smooth Dark Background */
    .stApp {{ 
        background: #0e1117 !important;
        color: #e0e0e0 !important;
    }}

    /* Tabs Fix for Mobile */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        background-color: #161b22;
        padding: 5px;
        border-radius: 10px;
        position: sticky;
        top: 0;
        z-index: 1001;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 14px !important;
        height: 40px !important;
    }}

    /* Chat Container for Mobile Viewport */
    .chat-container {{
        display: flex;
        flex-direction: column;
        padding: 10px;
        margin-bottom: 120px; /* Space for input box */
    }}

    /* Optimized Bubbles (No overlapping) */
    .user-msg {{
        align-self: flex-end;
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        padding: 10px 15px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 85%;
        font-size: 15px;
        word-wrap: break-word;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.3);
    }}

    .ai-msg {{
        align-self: flex-start;
        background: #21262d;
        color: #f0f0f0;
        padding: 10px 15px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
        border-left: 3px solid #00ff88;
        font-size: 15px;
        word-wrap: break-word;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.3);
    }}

    /* Fixed Input Box at the Absolute Bottom */
    div[data-testid="stChatInput"] {{
        position: fixed !important;
        bottom: 10px !important;
        left: 0 !important;
        right: 0 !important;
        padding: 0 10px !important;
        z-index: 9999 !important;
        background: #0e1117 !important;
    }}

    /* Welcome Card - Mobile size */
    .welcome-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-top: 10px;
    }}
    .welcome-text {{
        font-size: 28px;
        font-weight: 800;
        color: #00ff88;
    }}

    /* Hide redundant elements */
    .stDeployButton {{ display:none; }}
    </style>
""", unsafe_allow_html=True)

# ================= 3. LOGIC (OTP & SESSION) =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "fb_sent" not in st.session_state: st.session_state.fb_sent = False
if "otp_timestamp" not in st.session_state: st.session_state.otp_timestamp = 0

def send_mail(to, body, sub="Update"):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login(MY_GMAIL, APP_PASS); s.send_message(msg); s.quit()
        return True
    except: return False

# ================= 4. MOBILE LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><div class="welcome-text">WELCOME</div><p style="font-size:14px;">Siddique\'s AI Secure Portal</p></div>', unsafe_allow_html=True)
    
    email = st.text_input("Gmail ID:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Get OTP", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(100000, 999999))
                if send_mail(email, f"Login OTP: {otp}", "Verification"):
                    st.session_state.generated_otp = otp; st.session_state.user_email = email
                    st.session_state.otp_sent = True; st.session_state.otp_timestamp = time.time(); st.rerun()
    else:
        otp_val = st.text_input("Enter OTP:", type="password")
        if st.button("Verify & Login", use_container_width=True):
            if otp_val == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
        
        # Resend logic
        wait = int(60 - (time.time() - st.session_state.otp_timestamp))
        if wait > 0: st.caption(f"Resend in {wait}s")
        elif st.button("Resend Now"): st.session_state.otp_sent = False; st.rerun()
    st.stop()

# ================= 5. MAIN APP =================
with st.sidebar:
    st.write(f"👤 {st.session_state.user_email}")
    if st.button("🗑️ Clear", use_container_width=True): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout", use_container_width=True): st.session_state.logged_in = False; st.rerun()

tab_chat, tab_set, tab_fb = st.tabs(["💬 Chat", "⚙️ Set", "📩 Feed"])

with tab_chat:
    # Dedicated container for scroll
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    q = st.chat_input("Puchiye...")
    if q:
        # Prompt injection for identity
        sys_prompt = f"You are a helpful AI created by {CREATOR_NAME}. Always mention his name if asked."
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            ctx = [{"role": "system", "content": sys_prompt}] + st.session_state.messages
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=ctx)
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: st.error("Error connecting...")

with tab_set:
    st.markdown('<div class="welcome-card"><b>⚙️ Settings</b></div>', unsafe_allow_html=True)
    st.write(f"Developer: {CREATOR_NAME}")
    st.write("Privacy: Active")

with tab_fb:
    if st.session_state.fb_sent:
        st.success("Thanks for feedback! ❤️")
        if st.button("Send New"): st.session_state.fb_sent = False; st.rerun()
    else:
        msg = st.text_area("Feedback...")
        if st.button("Submit"):
            if send_mail(MY_GMAIL, f"Feedback from {st.session_state.user_email}: {msg}"):
                st.session_state.fb_sent = True; st.rerun()
        
