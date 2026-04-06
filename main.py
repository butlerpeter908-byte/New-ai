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

# ================= 1. SETUP =================
GROQ_KEY = "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"
HF_KEY = "Hf_tpmvquYeKzvBidpnGzBQTWrJEXgLMraKix" 

MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

st.set_page_config(page_title="Siddique AI 🤖", layout="wide")

def get_ist_time():
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST).strftime('%Y-%m-%d %I:%M:%S %p')

# ================= 2. UI STYLING =================
st.markdown("""
    <style>
    :root { color-scheme: dark; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background: linear-gradient(-45deg, #0f172a, #051937, #004d40, #0d1117); background-size: 400% 400%; animation: gradient 15s ease infinite; }
    @keyframes gradient { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    div[data-testid="stChatInput"] { position: fixed !important; bottom: 30px !important; z-index: 9999; background: rgba(15, 23, 42, 0.9); border: 1px solid #00ff88; border-radius: 15px; }
    .user-msg { background: #00ff88; color: #000; padding: 12px; border-radius: 15px 15px 0 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .ai-msg { background: #1e293b; color: #fff; padding: 12px; border-radius: 15px 15px 15px 0; margin: 10px 0; border-left: 5px solid #00d2ff; max-width: 85%; }
    .welcome-card { text-align:center; padding:40px; border:2px solid #00ff88; border-radius:25px; background:rgba(255,255,255,0.05); margin-bottom:20px; }
    </style>
""", unsafe_allow_html=True)

# ================= 3. FUNCTIONS =================
def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

def generate_image(prompt):
    headers = {"Authorization": f"Bearer {HF_KEY}"}
    try:
        # Error 400 se bachne ke liye prompt ko clean kiya
        clean_prompt = prompt.lower().replace("image", "").replace("generate", "").strip()
        response = requests.post(HF_API_URL, headers=headers, json={"inputs": clean_prompt}, timeout=40)
        if response.status_code == 200:
            return io.BytesIO(response.content)
    except: return None
    return None

# ================= 4. LOGIN (OLD STYLE) =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><h1 style="color:#00ff88;">SIDDIQUE AI</h1><p>Enter Gmail to continue</p></div>', unsafe_allow_html=True)
    
    email = st.text_input("Aapka Gmail ID:", value=st.session_state.user_email)
    
    if not st.session_state.otp_sent:
        if st.button("Send Access PIN", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Access Code", f"Aapka Secret PIN: {otp}"):
                    st.session_state.generated_otp = otp
                    st.session_state.user_email = email
                    st.session_state.otp_sent = True
                    st.rerun()
            else: st.error("Valid Gmail address dalein.")
    else:
        st.info(f"PIN sent to {st.session_state.user_email}")
        otp_in = st.text_input("Enter PIN:", type="password")
        col_v, col_r = st.columns(2)
        with col_v:
            if st.button("Verify & Login", use_container_width=True):
                if otp_in == st.session_state.generated_otp:
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("Wrong PIN!")
        with col_r:
            if st.button("Change Email", use_container_width=True):
                st.session_state.otp_sent = False
                st.rerun()
    st.stop()

# ================= 5. MAIN APP =================
with st.sidebar:
    st.write(f"Logged in: `{st.session_state.user_email}`")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

tab_chat, tab_settings = st.tabs(["💬 Messenger", "⚙️ Settings"])

with tab_chat:
    for m in st.session_state.messages:
        if m.get("type") == "img":
            st.image(m["content"])
        else:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Ask me anything...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q, "type": "text"})
        
        # Image Detection
        if any(w in q.lower() for w in ["image", "photo", "banao", "pic", "generate"]):
            with st.spinner("Bana raha hoon..."):
                img_data = generate_image(q)
                if img_data:
                    st.session_state.messages.append({"role": "assistant", "content": img_data, "type": "img"})
                    st.rerun()
                else:
                    st.error("Image limit reached ya API error (400).")
        else:
            # Chat logic
            try:
                res = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": f"You are an AI by {CREATOR}."}] + 
                             [{"role": m["role"], "content": str(m["content"])} for m in st.session_state.messages if m["type"] == "text"]
                )
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content, "type": "text"})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
