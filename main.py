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

# ================= 2. FORCE DARK & BOTTOM CHAT CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown("""
    <style>
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    
    /* Hard Dark Background */
    .stApp { 
        background-color: #0e1117 !important; 
        color: #ffffff !important; 
    }

    /* Fixing Chat Input to Bottom */
    .stChatInputContainer {
        position: fixed !important;
        bottom: 20px !important;
        left: 0;
        right: 0;
        padding: 10px !important;
        background-color: #0e1117 !important;
        z-index: 999;
    }

    /* Feedback Box Styling */
    .feedback-container {
        background: linear-gradient(45deg, #161b22, #21262d);
        border: 2px solid #00ff88;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 20px auto;
        box-shadow: 0px 0px 20px rgba(0, 255, 136, 0.3);
    }

    /* Chat Bubbles */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; border: 0.5px solid #00a884; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 80%; }
    
    /* Input Visibility Fix */
    input, textarea { background-color: #1c2128 !important; color: white !important; }

    /* Hide Red Boxes */
    .stException, .stAlert[data-baseweb="notification"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. PERMANENT SESSION LOGIC =================
# Isse login refresh par nahi udega
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
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

# ================= 4. LOGIN LOGIC (ONLY IF NOT LOGGED IN) =================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color:#00ff88;'>🔐 New AI Portal</h1>", unsafe_allow_html=True)
    
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

# ================= 5. MAIN APP INTERFACE =================
# Sidebar for Navigation (Chat/Feedback) and Logout
with st.sidebar:
    st.markdown(f"<h3 style='color:#00ff88;'>👤 {st.session_state.user_email}</h3>", unsafe_allow_html=True)
    st.markdown("---")
    choice = st.radio("Navigation", ["💬 Chat", "📩 Feedback"])
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True): 
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout Account", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

# --- CHAT TAB ---
if choice == "💬 Chat":
    st.markdown("<h3 style='text-align:center; color:#00ff88;'>🤖 Siddique's AI</h3>", unsafe_allow_html=True)
    
    # Message Display
    for m in st.session_state.messages:
        role = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    
    # Bottom Chat Input
    q = st.chat_input("Puchiye...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: pass

# --- FEEDBACK TAB ---
elif choice == "📩 Feedback":
    st.markdown("""
        <div class="feedback-container">
            <h2 style='color:#00ff88;'>📩 Feedback Area</h2>
            <p>Your message will be sent directly to Siddique.</p>
        </div>
    """, unsafe_allow_html=True)
    
    fb_text = st.text_area("Write here...", height=150)
    if st.button("🚀 Send to Siddique", use_container_width=True):
        if fb_text:
            if send_mail(MY_GMAIL, "New Feedback", f"User: {st.session_state.user_email}\n\n{fb_text}"):
                st.success("Feedback sent! ✅")
            else: st.error("Failed to send.")
        else: st.warning("Kuch likhiye!")
        
