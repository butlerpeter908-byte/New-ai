import streamlit as st
from groq import Groq
import smtplib
import random
import time
import html
import requests
from datetime import datetime, timedelta
import pytz
from email.mime.text import MIMEText

# ================= 1. SETUP & CREDENTIALS (HARDCODED) =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "mhja kxfr ptbb mazj"
CREATOR  = "mr owner"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="MR NEXUS AI", layout="centered")

# ================= 2. SAME PREMIUM CYBER UI =================
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
        color: white !important; padding: 12px 20px;
        border-radius: 20px 20px 0 20px;
        margin: 10px 0; text-align: right;
        box-shadow: 0 0 15px #6366f1;
        font-weight: bold;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .ai-msg {
        background: rgba(255, 255, 255, 0.15); color: #ffffff !important;
        padding: 12px 20px; border-radius: 20px 20px 20px 0;
        margin: 10px 0;
        border-left: 4px solid #38bdf8;
        white-space: pre-wrap;
        word-wrap: break-word;
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

# ================= 3. REAL CLIENT IP TRACKING =================
def get_real_client_ip():
    try:
        headers = st.context.headers
        xff = headers.get("X-Forwarded-For", "")
        if xff:
            return xff.split(",")[0].strip()
        return headers.get("X-Real-IP", "") or headers.get("CF-Connecting-IP", "") or "Not Captured"
    except Exception:
        return "Not Captured"

def lookup_ip_info(ip):
    try:
        if not ip or ip in ("Not Captured", "127.0.0.1", "::1"):
            return {}
        r = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
        if r.status_code == 200:
            d = r.json()
            return {
                "city": d.get("city", "N/A"),
                "region": d.get("region", "N/A"),
                "country": d.get("country_name", "N/A"),
                "org": d.get("org", "N/A"),
            }
    except Exception:
        pass
    return {}

# ================= 4. SESSION INIT =================
for key, default in {
    "messages": [],
    "generated_otp": None,
    "otp_expiry": None,
    "otp_attempts": 0,
    "last_otp_time": 0,
    "user_email": None,
    "otp_sent": False,
    "otp_logged_in": False,
    "login_alert_sent": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ================= 5. CONSTANTS =================
DISPOSABLE_DOMAINS = [
    "tempmail.com","10minutemail.com","mailinator.com","guerrillamail.com",
    "sharklasers.com","yopmail.com","trashmail.com","dispostable.com",
    "getnada.com","tempail.com","inboxkitten.com","fakeinbox.com",
    "maildrop.cc","crazymailing.com","tmail.ws","temp-mail.org",
    "temp-mail.io","throwawaymail.com","mohmal.com","emailondeck.com",
]
OTP_VALIDITY_MIN    = 5
OTP_MAX_ATTEMPTS    = 3
OTP_RESEND_COOLDOWN = 60
MAX_MESSAGE_LEN     = 2000
MAX_HISTORY         = 15

# ================= 6. HELPERS =================
def is_valid_real_email(email):
    email = (email or "").strip().lower()
    if "@" not in email or "." not in email:
        return False, "Invalid Email format!"
    domain = email.split("@")[-1]
    if any(domain == d or domain.endswith("." + d) for d in DISPOSABLE_DOMAINS):
        return False, "🚫 Temporary / Disposable Emails are NOT allowed!"
    if any(x in domain for x in ["temp", "disposable", "fake", "throwaway"]):
        return False, "🚫 Temporary / Disposable Emails are NOT allowed!"
    return True, "OK"

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = sub
        msg['From'] = MY_GMAIL
        msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15) as s:
            s.login(MY_GMAIL, APP_PASS)
            s.send_message(msg)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def send_login_tracking_alert(user_email="User"):
    ist = pytz.timezone('Asia/Kolkata')
    time_ist = datetime.now(ist).strftime('%Y-%m-%d %I:%M:%S %p IST')
    ip = get_real_client_ip()
    info = lookup_ip_info(ip)
    alert_body = f"""
🚨 NEW USER LOGIN ALERT!

👤 User Identifier: {user_email}
🕒 Time (IST): {time_ist}

🌐 Real IP Address: {ip}
📍 City: {info.get("city", "N/A")}
🗺️ State/Region: {info.get("region", "N/A")}
🏳️ Country: {info.get("country", "N/A")}
📡 Network Provider (ISP): {info.get("org", "N/A")}
    """
    send_mail(MY_GMAIL, f"🚨 Login Alert: {user_email}", alert_body)

def safe_text(t):
    return html.escape(t).replace("\n", "<br>")

def trim_history(msgs):
    return msgs[-MAX_HISTORY:]

# ================= 7. LOGIN SCREEN =================
google_logged_in = st.user.is_logged_in
otp_logged_in = st.session_state.get("otp_logged_in", False)

if not google_logged_in and not otp_logged_in:
    st.markdown("<div class='chat-card' style='text-align:center'><h1>NEXUS AI</h1><p>System Authentication Required</p></div>", unsafe_allow_html=True)

    st.markdown("""
        <div class="blinking-note">
            ⚠️ <b>Note:</b> If the 'Continue with Google' option is not working, please try the alternative email login method below.
        </div>
    """, unsafe_allow_html=True)

    # ---- 1. GOOGLE LOGIN (NATIVE) ----
    if st.button("🔵 Continue with Google", use_container_width=True):
        st.login("google")

    st.markdown("<p style='text-align:center; margin:15px 0; color:#cbd5e1;'>--- OR ---</p>", unsafe_allow_html=True)

    # ---- 2. EMAIL OTP LOGIN ----
    if not st.session_state.otp_sent:
        email = st.text_input("Enter Email ID")
        if st.button("Initialize Access", use_container_width=True):
            if email:
                is_valid, msg = is_valid_real_email(email)
                if is_valid:
                    otp = str(random.randint(100000, 999999))
                    with st.spinner("Sending OTP..."):
                        sent, err = send_mail(email, "Access PIN", f"Your PIN: {otp}")
                    if sent:
                        st.session_state.user_email    = email
                        st.session_state.generated_otp = otp
                        st.session_state.otp_expiry    = datetime.now() + timedelta(minutes=OTP_VALIDITY_MIN)
                        st.session_state.otp_sent      = True
                        st.session_state.otp_attempts  = 0
                        st.session_state.last_otp_time = time.time()
                        st.rerun()
                    else:
                        st.error(f"Failed to send email. ({err})")
                else:
                    st.error(f"❌ {msg}")
            else:
                st.error("Please enter a valid Email ID first!")
    else:
        st.info(f"OTP sent to {st.session_state.user_email}. Valid {OTP_VALIDITY_MIN} min.")
        otp_in = st.text_input("Enter Secret PIN", type="password", max_chars=6)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Unlock System", use_container_width=True):
                if st.session_state.otp_expiry and datetime.now() > st.session_state.otp_expiry:
                    st.error("❌ OTP expired. Request a new one.")
                    st.session_state.otp_sent = False
                    st.rerun()
                if st.session_state.otp_attempts >= OTP_MAX_ATTEMPTS:
                    st.error("❌ Too many wrong attempts. Request a new OTP.")
                    st.session_state.otp_sent = False
                    st.rerun()
                if otp_in == st.session_state.generated_otp:
                    st.session_state.otp_logged_in = True
                    send_login_tracking_alert(st.session_state.get('user_email', 'OTP User'))
                    st.session_state.login_alert_sent = True
                    st.rerun()
                else:
                    st.session_state.otp_attempts += 1
                    left = OTP_MAX_ATTEMPTS - st.session_state.otp_attempts
                    st.error(f"❌ Incorrect PIN! {left} attempts left.")

        with col2:
            if st.button("Resend / Change", use_container_width=True):
                if time.time() - st.session_state.last_otp_time < OTP_RESEND_COOLDOWN:
                    wait = int(OTP_RESEND_COOLDOWN - (time.time() - st.session_state.last_otp_time))
                    st.warning(f"Wait {wait}s before resending.")
                else:
                    st.session_state.otp_sent = False
                    st.session_state.generated_otp = None
                    st.session_state.otp_attempts = 0
                    st.rerun()

    st.stop()

# ================= 8. GOOGLE LOGIN ALERT =================
if google_logged_in and not st.session_state.login_alert_sent:
    user_email = getattr(st.user, "email", "Google User")
    send_login_tracking_alert(user_email)
    st.session_state.login_alert_sent = True
    st.session_state.user_email = user_email

# ================= 9. MAIN DASHBOARD (SAME UI) =================
with st.sidebar:
    st.header("🛸 Menu")
    nav = st.radio("Navigation", ["💬 Nexus Chat", "⚙️ Settings", "📩 Terminal Feedback"])
    st.markdown("---")

    if google_logged_in:
        st.caption(f"👤 {getattr(st.user, 'email', 'User')}")
    elif otp_logged_in:
        st.caption(f"👤 {st.session_state.get('user_email', 'User')}")

    if st.button("System Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        if st.user.is_logged_in:
            st.logout()
        else:
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
        st.markdown(f'<div class="{c}">{safe_text(m["content"])}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    q = st.chat_input("Connect with AI...")
    if q:
        if len(q) > MAX_MESSAGE_LEN:
            st.error(f"Message too long (max {MAX_MESSAGE_LEN} chars).")
        else:
            st.session_state.messages.append({"role": "user", "content": q})
            try:
                with st.spinner("Nexus is thinking..."):
                    res = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "system", "content": f"Creator: {CREATOR}"}]
                                 + trim_history(st.session_state.messages),
                    )
                reply = res.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"⚠️ AI busy hai, thodi der baad try karo. ({e})")
            st.rerun()

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
        * **Login Tracking:** Security ke liye login ke time aapka IP aur email temporarily track kiya jata hai.
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
    fb = st.text_area("Log your message", max_chars=2000)
    if st.button("Transmit"):
        if fb.strip():
            with st.spinner("Transmitting..."):
                sent, err = send_mail(MY_GMAIL, "Feedback", fb)
            if sent:
                st.success("THANK YOU FOR FEEDBACK! 🫶🏻🎊")
            else:
                st.error(f"Failed to send feedback. ({err})")
        else:
            st.error("Please write some feedback before transmitting.")
