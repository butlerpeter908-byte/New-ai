import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import smtplib 
import random 
import time
from email.mime.text import MIMEText
from streamlit_oauth import OAuth2Component

# ================= 1. SETUP =================
GROQ_KEY = "Gsk_7gbMisIhP9ENVZbcRg7gWGdyb3FYF3y6PpoxJJM5EVKnzoRwfG5w"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "mhja kxfr ptbb mazj" 
CREATOR = "mr owner"

# Google OAuth Configuration
CLIENT_ID = "1099072935326-kl56dikg9pnho1nm68evt8gem0kj2deh.apps.googleusercontent.com"
CLIENT_SECRET = "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"
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REFRESH_TOKEN_URL = TOKEN_URL
REVOKE_TOKEN_URL = "https://oauth2.googleapis.com/revoke"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, REFRESH_TOKEN_URL, REVOKE_TOKEN_URL)
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="MR NEXUS AI", layout="centered")

# ================= 2. 3D-STYLE CYBER UI ANIMATIONS =================
st.markdown("""
    <style>
    /* Background Animation */
    @keyframes bgMove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #0f172a);
        background-size: 400% 400%;
        animation: bgMove 12s ease infinite;
    }
    
    /* Pop-Up Animation for Login Form */
    @keyframes popUp {
        0% { transform: translateY(150px) scale(0.8); opacity: 0; }
        80% { transform: translateY(-10px) scale(1.02); opacity: 1; }
        100% { transform: translateY(0) scale(1); opacity: 1; }
    }
    
    .chat-card { 
        background: rgba(0, 0, 0, 0.65) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(99, 102, 241, 0.4);
        padding: 30px;
        border-radius: 24px;
        box-shadow: 0 15px 40px 0 rgba(0, 0, 0, 0.6);
        animation: popUp 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }
    
    h1, h2, h3, p, label { color: #ffffff !important; font-weight: 500; }
    
    .user-msg { 
        background: linear-gradient(90deg, #6366f1, #a855f7); 
        color: white !important; padding: 12px 20px; border-radius: 20px 20px 0 20px; 
        margin: 10px 0; text-align: right; box-shadow: 0 0 15px #6366f1;
        font-weight: bold;
    }
    .ai-msg { 
        background: rgba(255, 255, 255, 0.15); color: #ffffff !important; 
        padding: 12px 20px; border-radius: 20px 20px 20px 0; margin: 10px 0;
        border-left: 4px solid #38bdf8;
    }

    /* Input Field Styling */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Sleek Button */
    .stButton>button { 
        background: linear-gradient(90deg, #4f46e5, #9333ea) !important; 
        border: none !important; 
        color: #ffffff !important; 
        border-radius: 50px !important;
        font-weight: bold !important;
        padding: 10px 24px !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stButton>button:hover { 
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(147, 51, 234, 0.5) !important; 
    }

    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.35; }
        100% { opacity: 1; }
    }
    .blinking-note {
        animation: blink 1.8s infinite ease-in-out;
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid #ef4444;
        color: #fca5a5 !important;
        padding: 12px 16px;
        border-radius: 12px;
        text-align: center;
        font-size: 14px;
        font-weight: 500;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION & HELPER FUNCTIONS =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "messages" not in st.session_state: st.session_state.messages = []

DISPOSABLE_DOMAINS = [
    "tempmail.com", "10minutemail.com", "mailinator.com", "guerrillamail.com", 
    "yopmail.com", "trashmail.com", "getnada.com", "tempail.com"
]

def is_valid_real_email(email):
    if "@" not in email or "." not in email:
        return False, "Invalid Email format!"
    domain = email.strip().lower().split("@")[-1]
    if domain in DISPOSABLE_DOMAINS or "temp" in domain or "disposable" in domain:
        return False, "🚫 Temporary Emails not allowed!"
    return True, "OK"

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: 
        return False

# ================= 4. ANIMATED LOGIN INTERFACE =================
if not st.session_state.logged_in:
    
    # 🌟 LOTTIE ANIMATION (3D Character Vibe)
    lottie_html = """
    <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
    <div style="display: flex; justify-content: center; margin-bottom: -30px;">
        <lottie-player 
            src="https://lottie.host/8b2f6f59-33ff-4927-8025-a7bdfd9b3506/U40oM5Z7c6.json" 
            background="transparent" 
            speed="1" 
            style="width: 250px; height: 250px;" 
            loop 
            autoplay>
        </lottie-player>
    </div>
    """
    components.html(lottie_html, height=220)

    # 🌟 POP-UP LOGIN FORM
    st.markdown("<div class='chat-card' style='text-align:center'><h1>NEXUS AI</h1><p style='color:#a5b4fc !important;'>System Authentication Required</p>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="blinking-note">
            ⚠️ <b>Note:</b> If 'Continue with Google' fails, please use the OTP method below.
        </div>
    """, unsafe_allow_html=True)

    # GOOGLE LOGIN
    result = oauth2.authorize_button(
        name="Continue with Google",
        icon="https://www.google.com/favicon.ico",
        redirect_uri="https://9s2s.streamlit.app/component/streamlit_oauth.authorize_button",
        scope="openid email profile",
        key="google_auth",
        use_container_width=True,
    )

    if result and "token" in result:
        st.session_state.logged_in = True
        st.session_state.token = result["token"]
        st.rerun()

    st.markdown("<p style='text-align:center; margin:15px 0; color:#cbd5e1;'>─── OR ───</p>", unsafe_allow_html=True)

    # OTP LOGIN
    if not st.session_state.otp_sent:
        email = st.text_input("Enter Email ID", placeholder="your.email@example.com")
        if st.button("Initialize Access", use_container_width=True):
            if email:
                is_valid, msg = is_valid_real_email(email)
                if is_valid:
                    otp = str(random.randint(1000, 9999))
                    if send_mail(email, "Access PIN", f"Your PIN: {otp}"):
                        st.session_state.generated_otp = otp
                        st.session_state.otp_sent = True
                        st.rerun()
                    else:
                        st.error("Mail send nahi hua. Connection check karo.")
            else:
                st.error("Pehle valid Email ID daalo Sir!")
    else:
        st.info("OTP bhej diya hai! Apna inbox check karo.")
        otp_in = st.text_input("Enter Secret PIN", type="password")
        if st.button("Unlock System", use_container_width=True):
            if otp_in == st.session_state.generated_otp:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Galat PIN! Wapas try karo.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.header("🛸 Menu")
    nav = st.radio("Navigation", ["💬 Nexus Chat", "⚙️ Settings"])
    st.markdown("---")
    if st.button("System Logout"): 
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

if nav == "💬 Nexus Chat":
    st.markdown("""
        <div class='chat-card' style='text-align: center; margin-bottom: 15px;'>
            <h2 style='margin: 0; padding: 0;'>🚀 WELCOME TO NEXUS AI</h2>
            <p style='margin-top: 5px; opacity: 0.8;'>Aapka Jarvis ready hai Sir.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='chat-card'>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        c = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{c}">{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Connect with AI...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"Creator: {CREATOR}, Name: Jarvis"}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "⚙️ Settings":
    st.subheader("System Preferences")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat history clear kar di hai, Sir!")
        time.sleep(1)
        st.rerun()
        
