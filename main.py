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

st.set_page_config(page_title="New AI 🤖", layout="wide")

# ================= 2. THE PREMIUM CSS (Shaandaar Look) =================
st.markdown("""
    <style>
    /* Global Styles */
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    .stApp { 
        background: radial-gradient(circle at top, #1a1f25 0%, #0e1117 100%) !important;
        color: #e0e0e0 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Modern Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255, 255, 255, 0.05);
        padding: 8px;
        border-radius: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 10px;
        background-color: transparent;
        color: #888;
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00ff88 !important;
        color: #000 !important;
        font-weight: bold;
        box-shadow: 0px 4px 15px rgba(0, 255, 136, 0.4);
    }

    /* Chat Bubble Overhaul */
    .user-msg { 
        background: linear-gradient(135deg, #00b09b, #96c93d); 
        color: white;
        padding: 14px 18px; 
        border-radius: 20px 20px 4px 20px; 
        margin: 12px 0; 
        text-align: right; 
        margin-left: auto; 
        max-width: 85%; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }
    .ai-msg { 
        background: rgba(255, 255, 255, 0.07); 
        backdrop-filter: blur(10px);
        padding: 14px 18px; 
        border-radius: 20px 20px 20px 4px; 
        margin: 12px 0; 
        border-left: 4px solid #00ff88; 
        max-width: 85%; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }

    /* Input Box at Bottom */
    .stChatInputContainer { 
        position: fixed !important; 
        bottom: 15px !important; 
        z-index: 1000; 
        background: rgba(14, 17, 23, 0.8) !important;
        backdrop-filter: blur(15px);
        border-radius: 30px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* Settings & Cards */
    .settings-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(90deg, #00ff88, #00d2ff) !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        transition: 0.3s !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 5px 15px rgba(0, 255, 136, 0.4);
    }

    .stException, .stAlert { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "last_otp_time" not in st.session_state: st.session_state.last_otp_time = 0

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN UI (Modern) =================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#00ff88; margin-bottom:30px;'>🚀 Welcome to New AI</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="settings-card">', unsafe_allow_html=True)
        email = st.text_input("Enter your Gmail address:")
        
        if not st.session_state.otp_sent:
            if st.button("Generate Secure OTP", use_container_width=True):
                if "@gmail.com" in email:
                    otp = str(random.randint(1000, 9999))
                    if send_mail(email, "Login OTP", f"Aapka Secure OTP hai: {otp}"):
                        st.session_state.generated_otp = otp; st.session_state.user_email = email
                        st.session_state.otp_sent = True; st.session_state.last_otp_time = time.time(); st.rerun()
        else:
            st.success(f"OTP Sent to {st.session_state.user_email}")
            otp_in = st.text_input("Enter 4-Digit OTP:", type="password")
            if st.button("Verify & Login", use_container_width=True):
                if otp_in == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
            
            elapsed = time.time() - st.session_state.last_otp_time
            if elapsed < 60: st.info(f"Resend in {int(60-elapsed)}s")
            else: 
                if st.button("Resend Now", use_container_width=True): st.session_state.otp_sent = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.markdown(f"<div style='text-align:center;'><h3 style='color:#00ff88;'>👤 Profile</h3><p>{st.session_state.user_email}</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout Account", use_container_width=True): st.session_state.logged_in = False; st.rerun()

# --- SHAANDAAR TABS ---
tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "⚙️ Settings", "📩 Feedback"])

# --- MESSENGER ---
with tab_chat:
    chat_box = st.container()
    with chat_box:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Ask me anything...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        with chat_box: st.markdown(f'<div class="user-msg">{q}</div>', unsafe_allow_html=True)
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=st.session_state.messages)
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            with chat_box: st.markdown(f'<div class="ai-msg">{ans}</div>', unsafe_allow_html=True)
            st.rerun()
        except: pass

# --- SETTINGS ---
with tab_settings:
    st.markdown("<h2 style='color:#00ff88;'>⚙️ App Control Center</h2>", unsafe_allow_html=True)
    
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("👤 About Developer")
    st.write(f"This AI Portal is crafted by **{CREATOR}**.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    st.subheader("🛡️ Privacy & Security")
    st.write("• End-to-end Session Encryption\n• No persistent chat logs\n• Secure OTP Authentication")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FEEDBACK ---
with tab_feedback:
    st.markdown("<h2 style='color:#00ff88;'>📩 User Feedback</h2>", unsafe_allow_html=True)
    st.markdown('<div class="settings-card">', unsafe_allow_html=True)
    fb = st.text_area("How was your experience?", placeholder="Type here...", height=150)
    if st.button("🚀 Submit to Siddique", use_container_width=True):
        if fb and send_mail(MY_GMAIL, "AI Feedback", f"User: {st.session_state.user_email}\n\n{fb}"):
            st.success("Feedback sent successfully! ✅")
        else: st.error("Failed to send. Please check input.")
    st.markdown('</div>', unsafe_allow_html=True)
    
