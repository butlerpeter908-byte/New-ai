import streamlit as st
from groq import Groq
import smtplib
import random
from email.mime.text import MIMEText

# ================= 1. SETUP & KEYS =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. FORCE DARK MODE CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown("""
    <style>
    /* Force Dark Theme: System kuch bhi ho, AI Dark rahega */
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    
    .stApp { 
        background-color: #0e1117 !important; 
        color: #ffffff !important; 
    }

    /* Feedback Box Centre Styling */
    .feedback-container {
        background: linear-gradient(45deg, #161b22, #21262d);
        border: 2px solid #00ff88;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 20px auto;
        box-shadow: 0px 0px 20px rgba(0, 255, 136, 0.3);
        max-width: 500px;
    }

    .feedback-title {
        color: #00ff88;
        font-weight: bold;
        font-size: 22px;
        margin-bottom: 10px;
    }

    /* Input & Buttons visibility fix */
    input, textarea {
        background-color: #1c2128 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }

    /* Chat Bubbles */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 80%; }
    
    /* Hide Red Boxes */
    .stException, .stAlert { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION STATE =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "generated_otp" not in st.session_state: st.session_state.generated_otp = None
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = sub
        msg['From'] = MY_GMAIL
        msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS)
            s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN SCREEN (FORCE DARK) =================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color:#00ff88;'>🔐 Secure AI Login</h1>", unsafe_allow_html=True)
    
    with st.container():
        if not st.session_state.otp_sent:
            email = st.text_input("Enter Gmail:")
            if st.button("Get OTP", use_container_width=True):
                if "@gmail.com" in email:
                    otp = str(random.randint(1000, 9999))
                    if send_mail(email, "Login OTP", f"Your OTP: {otp}"):
                        st.session_state.generated_otp = otp
                        st.session_state.user_email = email
                        st.session_state.otp_sent = True
                        st.rerun()
        else:
            otp_in = st.text_input("Enter 4-Digit OTP:", type="password")
            if st.button("Verify", use_container_width=True):
                if otp_in == st.session_state.generated_otp:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Wrong OTP")
    st.stop()

# ================= 5. MAIN APP & CENTRE FEEDBACK =================
tab1, tab2 = st.tabs(["💬 Chat", "📩 Send Feedback"])

with tab1:
    st.markdown("<h3 style='text-align:center; color:#00ff88;'>🤖 Siddique's AI</h3>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Ask me something...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: pass

with tab2:
    # CENTRE FEEDBACK SECTION
    st.markdown("""
        <div class="feedback-container">
            <div class="feedback-title">📩 Share Your Feedback</div>
            <p style='color:#8b949e;'>Aapka opinion Siddique ke liye zaroori hai.</p>
        </div>
    """, unsafe_allow_html=True)
    
    fb_text = st.text_area("Write here...", placeholder="Kaisa laga AI?", height=150)
    if st.button("🚀 Submit to Siddique", use_container_width=True):
        if fb_text:
            if send_mail(MY_GMAIL, "New Feedback", f"From: {st.session_state.user_email}\n\n{fb_text}"):
                st.success("Feedback sent! ✅")
            else: st.error("Failed to send.")
        else: st.warning("Khali feedback mat bhejo bhai!")

# Simple Sidebar for Logout only
with st.sidebar:
    st.write(f"Logged in: **{st.session_state.user_email}**")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
                                                                                          
