import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from PIL import Image

# ================= CREDENTIALS =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"

client = Groq(api_key=GROQ_KEY)

# ================= LOGIN SYSTEM =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("🔐 Welcome to New AI")
    st.subheader("Please Login to Continue")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user and pwd: # Aap yahan specific username/pwd bhi set kar sakte hain
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Please enter details")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ================= MAIN APP STARTS HERE =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UTILS ---
def send_feedback_email(user_msg):
    try:
        msg = MIMEText(f"New Feedback: {user_msg}")
        msg['Subject'] = 'New AI Feedback'
        msg['From'] = MY_GMAIL
        msg['To'] = MY_GMAIL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_GMAIL, APP_PASS)
            server.send_message(msg)
        return True
    except: return False

# --- UI CSS ---
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem; background-color: #0E1117;}
    .user-bubble { background-color: #005c4b; color: white; padding: 12px 18px; border-radius: 18px 18px 0 18px; margin: 10px 0; max-width: 80%; float: right; clear: both; }
    .ai-bubble { background-color: #202c33; color: white; padding: 12px 18px; border-radius: 18px 18px 18px 0; margin: 10px 0; max-width: 80%; float: left; clear: both; border-left: 5px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (RESTORED OPTIONS) ---
with st.sidebar:
    st.title("🤖 New AI Menu")
    menu = st.selectbox("Navigate", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    
    if menu == "About Creator":
        st.info("👤 **Creator:** Butler Peter\n\nAI for Vision and Chat.")
    elif menu == "Feedback":
        f_msg = st.text_area("Share feedback:")
        if st.button("Submit"):
            if send_feedback_email(f_msg): st.success("Sent to Gmail!")
    elif menu == "Privacy Policy":
        st.write("🔒 Your data is processed securely via Groq.")
    elif menu == "Terms & Conditions":
        st.write("⚖️ Use responsibly. Powered by Llama 3.3.")
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- MAIN CHAT ---
st.title("🤖 New AI Chat")

for i, m in enumerate(st.session_state.messages):
    b_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{b_class}">{m["content"]}</div>', unsafe_allow_html=True)
    if m["role"] == "assistant":
        if st.button(f"🔊 Listen", key=f"v_{i}"):
            tts = gTTS(text=m["content"], lang='hi', tld='co.in')
            fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)

# --- IMAGE UPLOAD ---
st.markdown("---")
uploaded_file = st.file_uploader("📸 Photo Solution", type=["jpg", "png", "jpeg"])
if uploaded_file and st.button("Analyze Photo"):
    base64_img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    res = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[{"role": "user", "content": [{"type": "text", "text": "Describe image."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
    )
    st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
    st.rerun()

# --- TEXT INPUT ---
u_input = st.chat_input("Ask anything...")
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Thinking..."):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": st.session_state.messages[-1]["content"]}]
        )
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
                     
