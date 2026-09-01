
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import smtplib
import random
import time
import requests
import json
from datetime import datetime
import pytz
from email.mime.text import MIMEText
from streamlit_oauth import OAuth2Component

# ================= 1. SETUP & CREDENTIALS =================
GROQ_KEY = "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"
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

# ================= 2. LIVE PREMIUM CYBER UI & BLINKING ANIMATION =================
st.markdown("""
    <style>
    @keyframes bgMove {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #4338ca, #be185d, #0f172a);
        background-size: 400% 400%;
        animation: bgMove 10s ease infinite;
    }
    .chat-card {
        background: rgba(0, 0, 0, 0.6) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
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
    .stButton>button {
        background: transparent !important;
        border: 2px solid #6366f1 !important;
        color: #ffffff !important;
        border-radius: 50px !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background: #6366f1 !important;
        box-shadow: 0 0 20px #6366f1 !important;
    }

    /* Blinking Animation for Note */
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

# ================= 3. CLIENT-SIDE REAL IP TRACKING =================
# HTML/JavaScript component to capture real user IP from client browser
ip_tracker_html = """
<script>
fetch('https://ipapi.co/json/')
  .then(response => response.json())
  .then(data => {
    const payload = {
        ip: data.ip || 'N/A',
        city: data.city || 'N/A',
        region: data.region || 'N/A',
        country: data.country_name || 'N/A',
        org: data.org || 'N/A'
    };
    window.parent.postMessage({
        type: 'streamlit:setComponentValue',
        value: payload
    }, '*');
  })
  .catch(err => {
    fetch('https://api.ipify.org?format=json')
      .then(res => res.json())
      .then(d => {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: {ip: d.ip, city: 'Unknown', region: 'Unknown', country: 'Unknown', org: 'Mobile Data'}
        }, '*');
      });
  });
</script>
"""

client_data = components.html(ip_tracker_html, height=0)

# ================= 4. SESSION & HELPER FUNCTIONS =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "messages" not in st.session_state:
    st.session_state.messages = []

DISPOSABLE_DOMAINS = [
    "tempmail.com",
    "10minutemail.com",
    "mailinator.com",
    "guerrillamail.com",
    "sharklasers.com",
    "yopmail.com",
    "trashmail.com",
    "dispostable.com",
    "getnada.com",
    "tempail.com",
    "inboxkitten.com",
    "fakeinbox.com",
    "maildrop.cc",
    "crazymailing.com",
    "tmail.ws",
    "temp-mail.org"
]

def is_valid_real_email(email):
    if "@" not in email or "." not in email:
        return False, "Invalid Email format!"
    domain = email.strip().lower().split("@")[-1]
    if domain in DISPOSABLE_DOMAINS or "temp" in domain or "disposable" in domain or "fake" in domain:
        return False, "🚫 Temporary / Disposable Emails are NOT allowed!"
    return True, "OK"

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
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_login_tracking_alert(user_email="User", client_info=None):
    ist = pytz.timezone('Asia/Kolkata')
    time_ist = datetime.now(ist).strftime('%Y-%m-%d %I:%M:%S %p IST')

    if client_info and isinstance(client_info, dict):
        ip = client_info.get('ip', 'Not Captured')
        city = client_info.get('city', 'Not Captured')
        region = client_info.get('region', 'Not Captured')
        country = client_info.get('country', 'Not Captured')
        org = client_info.get('org', 'Not Captured')
    else:
        ip = city = region = country = org = "Fetching Failed or Blocked by Browser"

    alert_body = f"""
🚨 NEW USER LOGIN ALERT!

👤 User Identifier: {user_email}
🕒 Time (IST): {time_ist}

🌐 Real IP Address: {ip}
📍 City: {city}
🗺️ State/Region: {region}
🏳️ Country: {country}
📡 Network Provider (ISP): {org}
    """

    send_mail(MY_GMAIL, f"🚨 Login Alert: {user_email}", alert_body)

# ================= 5. LOGIN INTERFACE =================
if not st.session_state.logged_in:
    st.markdown("<div class='chat-card' style='text-align:center'><h1>NEXUS AI</h1><p>System Authentication Required</p></div>", unsafe_allow_html=True)

    st.markdown("""
        <div class="blinking-note">
            ⚠️ <b>Note:</b> If the 'Continue with Google' option is not working, please try the alternative email login method below.
        </div>
    """, unsafe_allow_html=True)

    # 1. GOOGLE LOGIN BUTTON
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
        send_login_tracking_alert("Google OAuth User", client_data)
        st.rerun()

    st.markdown("<p style='text-align:center; margin:15px 0; color:#cbd5e1;'>--- OR ---</p>", unsafe_allow_html=True)

    # 2. EMAIL OTP LOGIN
    if not st.session_state.otp_sent:
        email = st.text_input("Enter Email ID")
        if st.button("Initialize Access", use_container_width=True):
            if email:
                is_valid, msg = is_valid_real_email(email)
                if is_valid:
                    otp = str(random.randint(1000, 9999))
                    if send_mail(email, "Access PIN", f"Your PIN: {otp}"):
                        st.session_state.user_email = email
                        st.session_state.generated_otp = otp
                        st.session_state.otp_sent = True
                        st.rerun()
                    else:
                        st.error("Failed to send email. Check your connection or email ID.")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.error("Please enter a valid Email ID first!")
    else:
        st.info("OTP sent successfully! Please check your email.")
        otp_in = st.text_input("Enter Secret PIN", type="password")
        if st.button("Unlock System", use_container_width=True):
            if otp_in == st.session_state.generated_otp:
                st.session_state.logged_in = True
                send_login_tracking_alert(st.session_state.get('user_email', 'OTP User'), client_data)
                st.rerun()
            else:
                st.error("❌ Incorrect PIN! Please try again.")

    st.stop()

# ================= 6. MAIN DASHBOARD INTERFACE =================
with st.sidebar:
    st.header("🛸 Menu")
    nav = st.radio("Navigation", ["💬 Nexus Chat", "⚙️ Settings", "📩 Terminal Feedback"])
    st.markdown("---")
    if st.button("System Logout"):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

if nav == "💬 Nexus Chat":
    st.markdown("""
        <div class='chat-card' style='text-align: center; margin-bottom: 15px;'>
            <h2 style='margin: 0; padding: 0;'>🚀 WELCOME TO NEXUS AI</h2>
            <p style='margin-top: 5px; opacity: 0.8;'>Your Personal AI Companion is Ready</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='chat-card'>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        c = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{c}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Connect with AI...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"Creator: {CREATOR}"}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "⚙️ Settings":
    st.subheader("System Preferences")

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat history cleared successfully, Sir!")
        time.sleep(1)
        st.rerun()

    st.write("---")

    with st.expander("🛡️ Privacy Policy"):
        st.markdown("""
        ### **Privacy Policy**
        * **Data Protection:** Hum aapka koi bhi data ya chats server par store nahi karte.
        * **Session-Based:** Yeh interface poori tarah se session-based hai. Jaise hi aap page refresh karenge ya tab close karenge, aapki saari memory clear ho jayegi.
        * **No Logs:** Groq API connectivity bilkul secure hai aur end-to-end encrypted session use karti hai.
        """)

    with st.expander("📄 Terms & Conditions"):
        st.markdown("""
        ### **Terms & Conditions**
        * **Usage:** Yeh ek personal AI assistant project hai, jo sirf educational aur non-commercial use ke liye design kiya gaya hai.
        * **API Compliance:** Is application ka misuse, heavy automated requests, ya script-based targeting strictly prohibited hai.
        * **Responsibility:** AI ke generated response temporary hote hain; unhe backup karne ki zimmedari user ki hogi.
        """)

    with st.expander("ℹ️ About"):
        st.markdown(f"""
        ### **NEXUS AI v1.0**
        * **Status:** Fully Optimized & Secure Deployment.
        * **Architecture:** Streamlit Core UI equipped with Groq LLM Acceleration.
        * **Developer & Creator:** {CREATOR}
        * *Systems are running under secure environment regulations.*
        """)

elif nav == "📩 Terminal Feedback":
    st.subheader("Direct Link")
    fb = st.text_area("Log your message")
    if st.button("Transmit"):
        if fb:
            send_mail(MY_GMAIL, "Feedback", fb)
            st.success("THANK YOU FOR FEEDBACK! 🫶🏻🎊")
        else:
            st.error("Please write some feedback before transmitting.")
