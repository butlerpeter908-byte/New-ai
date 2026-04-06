import streamlit as st
from groq import Groq
import smtplib
import random
import time
from email.mime.text import MIMEText
from datetime import datetime
import pytz
import requests
import io

# ================= 1. SETUP & CONFIG =================
GROQ_KEY = "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"
HF_KEY = "Hf_tpmvquYeKzvBidpnGzBQTWrJEXgLMraKix" 

MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

# Clients & API URLs
client = Groq(api_key=GROQ_KEY)
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

st.set_page_config(page_title="Siddique AI 🤖", layout="wide")

# Indian Standard Time Function
def get_ist_time():
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime('%Y-%m-%d %I:%M:%S %p')

# ================= 2. ADVANCED UI STYLING =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    
    .stApp { 
        background: linear-gradient(-45deg, #0f172a, #051937, #004d40, #0d1117);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #e0e0e0 !important;
    }
    @keyframes gradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }

    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 30px !important;
        left: 5% !important;
        right: 5% !important;
        width: 90% !important;
        z-index: 9999 !important;
        background: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(12px);
        border: 1px solid #00ff88;
        border-radius: 15px;
    }

    .user-msg { background: #00ff88; color: #000; padding: 12px; border-radius: 15px 15px 0 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; font-weight: 500;}
    .ai-msg { background: #1e293b; color: #fff; padding: 12px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 5px solid #00d2ff; max-width: 85%; }
    .welcome-card { background: rgba(255, 255, 255, 0.05); border: 2px solid #00ff88; border-radius: 25px; padding: 40px; text-align: center; margin-bottom: 20px; }
    
    .main .block-container { padding-bottom: 150px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION & HELPER FUNCTIONS =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

def query_image(prompt):
    headers = {"Authorization": f"Bearer {HF_KEY}"}
    try:
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt}, timeout=40)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except: return None
    return None

# ================= 4. LOGIN INTERFACE =================
if not st.session_state.logged_in:
    st.markdown(f'<div class="welcome-card"><h1 style="color:#00ff88;">SIDDIQUE AI</h1><p>Image Generation + Secure Smart Chat</p><p style="font-size:12px; color:#aaa;">Developed by {CREATOR}</p></div>', unsafe_allow_html=True)
    
    email = st.text_input("Aapka Gmail ID:", value=st.session_state.user_email, placeholder="example@gmail.com")
    
    if not st.session_state.otp_sent:
        if st.button("Send Access PIN", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Siddique AI Access Code", f"Aapka Secret PIN: {otp}"):
                    st.session_state.generated_otp = otp
                    st.session_state.user_email = email
                    st.session_state.otp_sent = True
                    st.rerun()
                else: st.error("Email bhejte waqt error aaya. Check Internet.")
            else: st.error("Kripya ek valid @gmail.com address dalein.")
    else:
        st.success(f"PIN aapke email ({st.session_state.user_email}) par bhej diya gaya hai.")
        otp_in = st.text_input("Enter 4-Digit PIN:", type="password")
        
        col_verify, col_edit = st.columns(2)
        with col_verify:
            if st.button("Verify & Login", use_container_width=True):
                if otp_in == st.session_state.generated_otp:
                    log_msg = f"User Login: {st.session_state.user_email}\nTime: {get_ist_time()}"
                    send_mail(MY_GMAIL, "New Login Detected 🚨", log_msg)
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Galat PIN! Dubara koshish karein.")
        with col_edit:
            if st.button("Change Email", use_container_width=True):
                st.session_state.otp_sent = False
                st.rerun()
    st.stop()

# ================= 5. MAIN APP INTERFACE =================
with st.sidebar:
    st.markdown(f"### 👤 Profile\n`{st.session_state.user_email}`")
    st.divider()
    if st.button("🚪 Logout Session", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()
    st.info(f"Creator: {CREATOR}\nVersion: 1.3.0")

tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "🛡️ Account & Privacy", "📩 Support"])

# --- CHAT & IMAGE LOGIC ---
with tab_chat:
    chat_container = st.container()
    with chat_container:
        for m in st.session_state.messages:
            if m["type"] == "img":
                st.image(m["content"], caption="Generated by Siddique AI", use_column_width=True)
            else:
                div_style = "user-msg" if m["role"] == "user" else "ai-msg"
                st.markdown(f'<div class="{div_style}">{m["content"]}</div>', unsafe_allow_html=True)

    user_query = st.chat_input("Baat karo ya bolo 'image banao'...")
    if user_query:
        # Add user query to history
        st.session_state.messages.append({"role": "user", "content": user_query, "type": "text"})
        with chat_container: st.markdown(f'<div class="user-msg">{user_query}</div>', unsafe_allow_html=True)
        
        # Keyword Detection for Image Generation
        img_triggers = ["image", "photo", "banao", "generate", "picture", "drawing", "painting", "pic"]
        is_image = any(word in user_query.lower() for word in img_triggers)

        if is_image:
            with st.spinner("Siddique AI aapki image taiyar kar raha hai..."):
                img_data = query_image(user_query)
                if img_data:
                    st.session_state.messages.append({"role": "assistant", "content": img_data, "type": "img"})
                    st.rerun()
                else:
                    st.error("Image generation failed. Check API limit or Key.")
        else:
            # Regular AI Chat
            try:
                # Filter context to text only
                text_history = [m for m in st.session_state.messages if m["type"] == "text"]
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": f"You are a smart AI assistant. Your creator is {CREATOR}."}] + text_history
                )
                ai_text = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": ai_text, "type": "text"})
                st.rerun()
            except Exception as e:
                st.error(f"Chat Error: {e}")

# --- SETTINGS ---
with tab_settings:
    st.header("⚙️ Account Settings")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.write(f"**App Information**")
    st.write(f"User: {st.session_state.user_email}")
    st.write(f"Status: Securely Logged In")

# --- FEEDBACK ---
with tab_feedback:
    st.header("📩 Contact Creator")
    fb_msg = st.text_area("Aapka message...")
    if st.button("Send to Siddique", use_container_width=True):
        if fb_msg:
            full_fb = f"Feedback from {st.session_state.user_email}:\n\n{fb_msg}"
            if send_mail(MY_GMAIL, "App Feedback", full_fb):
                st.success("Message sent successfully!")
