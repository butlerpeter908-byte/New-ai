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
# CREATOR NAME JO AI BOLEGA
CREATOR_NAME = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="New AI 🤖", layout="wide")

# ================= 2. THE ULTIMATE SHAANDAAR CSS =================
st.markdown(f"""
    <style>
    :root {{ color-scheme: dark; }}
    header, footer {{ visibility: hidden !important; }}
    .stApp {{ 
        background: radial-gradient(circle at top, #1a1f25 0%, #0e1117 100%) !important;
        color: #e0e0e0 !important;
    }}

    /* RIGHT-LEFT CHAT LOGIC */
    .chat-container {{
        display: flex;
        flex-direction: column;
        gap: 15px;
        padding-bottom: 150px;
    }}

    .user-msg {{
        align-self: flex-end;
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 2px 20px;
        max-width: 75%;
        box-shadow: 2px 4px 15px rgba(0,0,0,0.3);
        font-family: 'Inter', sans-serif;
    }}

    .ai-msg {{
        align-self: flex-start;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        color: #f0f0f0;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 2px;
        max-width: 75%;
        border-left: 4px solid #00ff88;
        box-shadow: -2px 4px 15px rgba(0,0,0,0.3);
    }}

    /* BOTTOM CHAT INPUT FIXED */
    div[data-testid="stChatInput"] {{
        position: fixed !important;
        bottom: 25px !important;
        z-index: 9999 !important;
        background: rgba(14, 17, 23, 0.95) !important;
        backdrop-filter: blur(15px);
        border-radius: 15px !important;
        border: 1px solid rgba(0, 255, 136, 0.2) !important;
    }}

    /* Welcome & Thanks Cards */
    .welcome-card, .thanks-card {{
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        margin-bottom: 20px;
    }}
    .welcome-text, .thanks-text {{
        font-size: 32px;
        font-weight: 900;
        background: linear-gradient(90deg, #00ff88, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "fb_sent" not in st.session_state: st.session_state.fb_sent = False
if "otp_timestamp" not in st.session_state: st.session_state.otp_timestamp = 0

def send_fast_otp(to_email, body, subject="🚀 Quick Update"):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = MY_GMAIL
        msg['To'] = to_email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(MY_GMAIL, APP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# ================= 4. LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><div class="welcome-text">WELCOME</div><p>Siddique\'s Private AI Engine</p></div>', unsafe_allow_html=True)
    
    email_input = st.text_input("Gmail ID Daalein:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Send OTP (Fast Delivery)", use_container_width=True):
            if "@gmail.com" in email_input:
                new_otp = str(random.randint(100000, 999999))
                if send_fast_otp(email_input, f"Login OTP: {new_otp}", "Login Verification"):
                    st.session_state.generated_otp = new_otp
                    st.session_state.user_email = email_input
                    st.session_state.otp_sent = True
                    st.session_state.otp_timestamp = time.time()
                    st.rerun()
    else:
        st.success(f"OTP Sent to {st.session_state.user_email}")
        otp_val = st.text_input("OTP Code Daalein:", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Verify & Login", use_container_width=True):
                if otp_val == st.session_state.generated_otp:
                    st.session_state.logged_in = True
                    st.rerun()
        with col2:
            time_passed = time.time() - st.session_state.otp_timestamp
            if time_passed < 60:
                st.button(f"Resend in {int(60 - time_passed)}s", disabled=True, use_container_width=True)
                time.sleep(1); st.rerun()
            else:
                if st.button("Resend Now", use_container_width=True):
                    st.session_state.otp_sent = False; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.user_email}**")
    if st.button("🗑️ Clear History", use_container_width=True): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout", use_container_width=True): 
        st.session_state.logged_in = False
        st.session_state.otp_sent = False; st.rerun()

tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "⚙️ Settings", "📩 Feedback"])

# --- CHAT TAB ---
with tab_chat:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        div_class = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div_class}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    q = st.chat_input("Siddique's AI se kuch bhi puchiye...")
    if q:
        # AI ko pta chale ki use kisne banaya
        system_prompt = f"You are a helpful AI. You were created by {CREATOR_NAME}. If anyone asks who made you or created you, always say {CREATOR_NAME}."
        
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            # Context ke saath creator ka naam add kiya
            chat_context = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=chat_context)
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()
        except: pass

# --- SETTINGS TAB ---
with tab_settings:
    st.markdown('<div class="welcome-card"><h2 style="color:#00ff88;">⚙️ Control Panel</h2></div>', unsafe_allow_html=True)
    with st.expander("👤 Creator Details"): st.write(f"This platform is exclusively developed by **{CREATOR_NAME}**.")
    with st.expander("📄 Terms"): st.write("Privacy-first AI experience.")

# --- FEEDBACK TAB ---
with tab_feedback:
    if st.session_state.fb_sent:
        st.markdown('<div class="thanks-card"><div class="thanks-text">THANKS FOR FEEDBACK!</div><p>Siddique tak aapka message pahunch gaya hai. ❤️</p></div>', unsafe_allow_html=True)
        if st.button("Naya Feedback Bhein"): st.session_state.fb_sent = False; st.rerun()
    else:
        st.header("📩 User Feedback")
        fb = st.text_area("App kaisa laga?", height=150)
        if st.button("🚀 Submit Feedback", use_container_width=True):
            if fb and send_fast_otp(MY_GMAIL, f"FEEDBACK FROM {st.session_state.user_email}:\n\n{fb}", "New User Feedback"):
                st.session_state.fb_sent = True; st.rerun()
                
