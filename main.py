import streamlit as st
from groq import Groq
import smtplib
import random
from email.mime.text import MIMEText
from datetime import datetime
import pytz

# ================= 1. SETUP =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Siddique AI 🤖", layout="wide", page_icon="🤖")

# ================= 2. UI STYLING (Modern Glassmorphism) =================
st.markdown("""
    <style>
    /* Global Styles */
    .stApp { background: radial-gradient(circle at center, #0f172a, #020617); color: #e0e0e0; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(15px); border-right: 1px solid #1e293b; }
    
    /* Chat Input Styling */
    div[data-testid="stChatInput"] { 
        position: fixed; bottom: 20px; left: 20%; right: 20%; 
        background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); 
        border-radius: 20px; border: 1px solid #334155; 
    }

    /* Message Bubbles */
    .user-msg { 
        background: linear-gradient(135deg, #00ff88, #00d2ff); 
        color: #000; padding: 12px 18px; border-radius: 18px 18px 0 18px; 
        margin: 10px 0; text-align: right; margin-left: auto; max-width: 70%; font-weight: 500;
    }
    .ai-msg { 
        background: rgba(255, 255, 255, 0.08); 
        color: #fff; padding: 12px 18px; border-radius: 18px 18px 18px 0; 
        margin: 10px 0; border-left: 4px solid #00d2ff; max-width: 80%; backdrop-filter: blur(5px);
    }
    
    /* Buttons */
    .stButton>button { border-radius: 20px; border: 1px solid #00d2ff; background: transparent; color: #00d2ff; transition: 0.3s; }
    .stButton>button:hover { background: #00d2ff; color: #000; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION & FUNCTIONS =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "messages" not in st.session_state: st.session_state.messages = []

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN =================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #00d2ff;'>SIDDIQUE AI 🤖</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Secure Access Required</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Enter Email ID:")
        if not st.session_state.otp_sent:
            if st.button("Get Access PIN"):
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Access PIN", f"Your PIN: {otp}"):
                    st.session_state.generated_otp = otp
                    st.session_state.otp_sent = True; st.rerun()
        else:
            otp_in = st.text_input("Enter PIN:", type="password")
            if st.button("Verify Access"):
                if otp_in == st.session_state.generated_otp: 
                    st.session_state.logged_in = True; st.rerun()
                else: st.error("Invalid PIN")
    st.stop()

# ================= 5. MAIN INTERFACE =================
# Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712038.png", width=100)
    st.title("Siddique AI")
    menu = st.radio("Navigation", ["💬 Messenger", "⚙️ Account", "📩 Support"])
    st.divider()
    if st.button("Logout"): 
        st.session_state.logged_in = False; st.rerun()

if menu == "💬 Messenger":
    st.header("Chat with AI")
    # Display messages
    for m in st.session_state.messages:
        st.markdown(f'<div class="{"user-msg" if m["role"]=="user" else "ai-msg"}">{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Ask me anything...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"Creator: {CREATOR}"}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif menu == "⚙️ Account":
    st.header("⚙️ Account & Privacy")
    if st.button("Clear Chat History"): 
        st.session_state.messages = []; st.success("History Cleared!"); st.rerun()
    st.write(f"**Developer:** {CREATOR}")
    with st.expander("🛡️ Privacy Policy"): st.write("Session-based chat, no data retention.")

elif menu == "📩 Support":
    st.header("📩 Feedback & Support")
    fb = st.text_area("Your thoughts...", height=150)
    if st.button("Submit Feedback"):
        send_mail(MY_GMAIL, "Feedback", fb)
        st.success("✅ Thank you for your feedback!")
        
