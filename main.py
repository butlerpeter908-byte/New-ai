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

# ================= AUTHENTICATION SYSTEM =================
if "users" not in st.session_state:
    st.session_state.users = {} # Format: {username: password}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def auth_page():
    st.title("🤖 Welcome to New AI")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab2:
        st.subheader("Create New Account")
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pwd = st.text_input("Choose Password", type="password", key="reg_pwd")
        if st.button("Register"):
            if new_user and new_pwd:
                st.session_state.users[new_user] = new_pwd
                st.success("Registration Successful! Now go to Login tab.")
            else:
                st.error("Please fill all fields")

    with tab1:
        st.subheader("Login to your Account")
        user = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            if user in st.session_state.users and st.session_state.users[user] == pwd:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("Invalid Username or Password")

if not st.session_state.logged_in:
    auth_page()
    st.stop()

# ================= MAIN APP UI =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- FEEDBACK EMAIL ---
def send_feedback_email(user_msg):
    try:
        msg = MIMEText(f"Feedback from {st.session_state.current_user}:\n\n{user_msg}")
        msg['Subject'] = 'New AI Feedback'
        msg['From'] = MY_GMAIL
        msg['To'] = MY_GMAIL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_GMAIL, APP_PASS)
            server.send_message(msg)
        return True
    except: return False

# --- SIDEBAR (FULL OPTIONS RESTORED) ---
with st.sidebar:
    st.title(f"👤 {st.session_state.current_user}")
    menu = st.selectbox("Navigate", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    
    if menu == "About Creator":
        st.info("👤 **Creator:** Butler Peter\n\nAI for Vision and Chat.")
    elif menu == "Feedback":
        f_msg = st.text_area("Share your feedback:")
        if st.button("Submit"):
            if send_feedback_email(f_msg): st.success("Sent to Gmail!")
    elif menu == "Privacy Policy":
        st.write("🔒 Your chat and data are processed securely via Groq Cloud.")
    elif menu == "Terms & Conditions":
        st.write("⚖️ Use this AI responsibly. Powered by Llama 3.3 and 3.2 Vision.")
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- MAIN CHAT INTERFACE ---
st.title("🤖 New AI Chat")

for i, m in enumerate(st.session_state.messages):
    role_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{role_class}">{m["content"]}</div>', unsafe_allow_html=True)
    if m["role"] == "assistant":
        if st.button(f"🔊 Listen", key=f"v_{i}"):
            tts = gTTS(text=m["content"], lang='hi', tld='co.in')
            fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)

# --- IMAGE UPLOAD (VISION) ---
st.markdown("---")
uploaded_file = st.file_uploader("📸 Upload Photo for Solution", type=["jpg", "png", "jpeg"])
if uploaded_file and st.button("Analyze Photo"):
    base64_img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    # Using the fixed vision model
    res = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[{"role": "user", "content": [{"type": "text", "text": "Describe or solve this image."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}]}]
    )
    st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
    st.rerun()

# --- TEXT INPUT (INSTANT) ---
u_input = st.chat_input("Ask New AI anything...")
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    st.rerun() # Refresh for instant visibility

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("New AI is thinking..."):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": st.session_state.messages[-1]["content"]}]
        )
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
        
