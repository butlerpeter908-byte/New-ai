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
client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="New AI 🤖", layout="wide")

# ================= 2. CSS (Dark Mode & Chat Fix) =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    header, footer { visibility: hidden !important; }
    .stApp { background-color: #0e1117 !important; color: #ffffff !important; }
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; border: 0.5px solid #00a884; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 80%; }
    .stChatInputContainer { position: fixed !important; bottom: 20px !important; z-index: 999; background-color: #0e1117 !important; }
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

# ================= 4. LOGIN (OTP) =================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#00ff88;'>🔐 Secure Login</h1>", unsafe_allow_html=True)
    email = st.text_input("Enter Gmail:", value=st.session_state.user_email)
    if not st.session_state.otp_sent:
        if st.button("Send OTP", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Login OTP", f"OTP: {otp}"):
                    st.session_state.generated_otp = otp; st.session_state.user_email = email
                    st.session_state.otp_sent = True; st.session_state.last_otp_time = time.time(); st.rerun()
    else:
        st.markdown(f"<p style='color:#00ff88;'>📩 Check Gmail: {st.session_state.user_email}</p>", unsafe_allow_html=True)
        otp_in = st.text_input("Enter OTP:", type="password")
        if st.button("Verify", use_container_width=True):
            if otp_in == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
        # Resend Timer
        elapsed = time.time() - st.session_state.last_otp_time
        if elapsed < 60: st.write(f"Resend in {int(60-elapsed)}s")
        elif st.button("Resend OTP"): st.session_state.otp_sent = False; st.rerun()
    st.stop()

# ================= 5. MAIN CHAT (THE FIX) =================
with st.sidebar:
    st.write(f"👤 {st.session_state.user_email}")
    choice = st.radio("Menu", ["💬 Chat", "📩 Feedback"])
    if st.button("🗑️ Clear"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

if choice == "💬 Chat":
    st.markdown("<h3 style='text-align:center; color:#00ff88;'>🤖 Siddique's AI</h3>", unsafe_allow_html=True)
    
    # --- STEP 1: Pehle purane saare messages dikhao ---
    chat_container = st.container()
    with chat_container:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    # --- STEP 2: Input handle karo ---
    q = st.chat_input("Puchiye...")
    if q:
        # Naya message history mein dalo
        st.session_state.messages.append({"role": "user", "content": q})
        
        # Screen par turant dikhane ke liye forceful update
        with chat_container:
            st.markdown(f'<div class="user-msg">{q}</div>', unsafe_allow_html=True)
        
        # Phir AI response laao
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=st.session_state.messages)
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
            
            # AI message bhi turant render karo
            with chat_container:
                st.markdown(f'<div class="ai-msg">{ans}</div>', unsafe_allow_html=True)
            
            st.rerun() # Final State sync
        except:
            st.error("Kuch issue hai API mein.")

elif choice == "📩 Feedback":
    st.header("📩 Feedback")
    fb = st.text_area("Experience?")
    if st.button("Submit"):
        if fb and send_mail(MY_GMAIL, "Feedback", f"From: {st.session_state.user_email}\n\n{fb}"):
            st.success("Done! ✅")
    
