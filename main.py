import streamlit as st
from groq import Groq
import smtplib
import random
from email.mime.text import MIMEText

# ================= 1. CREDENTIALS & SETUP =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. CLEAN UI (No Profile Icon) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown("""
    <style>
    header, footer { visibility: hidden !important; }
    .stApp { background-color: #0e1117; color: white; }
    /* Chat Bubbles */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 85%; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 85%; }
    /* Hide Errors */
    .stException, .stAlert { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. OTP & SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "generated_otp" not in st.session_state: st.session_state.generated_otp = None
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []

def send_otp_email(receiver_email, otp):
    try:
        msg = MIMEText(f"Aapka New AI Verification OTP hai: {otp}")
        msg['Subject'] = 'New AI Login OTP'
        msg['From'] = MY_GMAIL
        msg['To'] = receiver_email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_GMAIL, APP_PASS)
            server.send_message(msg)
        return True
    except:
        return False

# ================= 4. OTP LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color:#00ff88;'>🔐 New AI Secure Login</h1>", unsafe_allow_html=True)
    
    if not st.session_state.otp_sent:
        email_input = st.text_input("Apna Gmail Id daalein:")
        if st.button("OTP Bhein", use_container_width=True):
            if "@gmail.com" in email_input:
                otp = str(random.randint(1000, 9999))
                if send_otp_email(email_input, otp):
                    st.session_state.generated_otp = otp
                    st.session_state.user_email = email_input
                    st.session_state.otp_sent = True
                    st.rerun()
                else: st.error("Email bhenjne mein dikat hui!")
            else: st.warning("Sahi Gmail id daalein!")
    else:
        st.info(f"OTP aapki email ({st.session_state.user_email}) par bhej diya gaya hai.")
        otp_input = st.text_input("4-Digit OTP daalein:", type="password")
        if st.button("Verify & Enter", use_container_width=True):
            if otp_input == st.session_state.generated_otp:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Galat OTP!")
        if st.button("Email Change Karein"):
            st.session_state.otp_sent = False
            st.rerun()
    st.stop()

# ================= 5. MAIN APP & FEEDBACK =================
with st.sidebar:
    st.markdown(f"<h3 style='color:#00ff88;'>👤 Verified User</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:12px;'>{st.session_state.user_email}</p>", unsafe_allow_html=True)
    st.markdown("---")
    choice = st.radio("Menu", ["💬 Chat", "📩 Feedback"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.session_state.otp_sent = False; st.rerun()

if choice == "💬 Chat":
    st.markdown("<h3 style='text-align:center; color:#00ff88;'>🤖 New AI Assistant</h3>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Puchiye...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: pass

elif choice == "📩 Feedback":
    st.header("📩 Feedback")
    fb = st.text_area("Aapka experience kaisa raha?")
    if st.button("Submit Feedback", use_container_width=True):
        if fb:
            try:
                f_msg = MIMEText(f"Feedback from: {st.session_state.user_email}\n\nMessage: {fb}")
                f_msg['Subject'] = 'New AI Feedback'
                f_msg['From'] = MY_GMAIL
                f_msg['To'] = MY_GMAIL
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                    s.login(MY_GMAIL, APP_PASS)
                    s.send_message(f_msg)
                st.success("Feedback Siddique ko bhej diya gaya! ✅")
            except: st.error("Error sending feedback.")
        else: st.warning("Kuch likhiye toh!")
            
