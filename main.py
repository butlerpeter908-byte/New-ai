import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import smtplib
from email.mime.text import MIMEText

# ================= CREDENTIALS & IDENTITY =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohammad Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= AUTHENTICATION SYSTEM =================
if "users" not in st.session_state:
    st.session_state.users = {} 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🤖 Welcome to New AI")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    
    with t2:
        u = st.text_input("New Username", key="reg_u")
        p = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Register"):
            if u and p: 
                st.session_state.users[u] = p
                st.success("Account created! Go to Login.")
            else: st.error("Fill all fields")
            
    with t1:
        lu = st.text_input("Username", key="log_u")
        lp = st.text_input("Password", type="password", key="log_p")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login"):
                if lu in st.session_state.users and st.session_state.users[lu] == lp:
                    st.session_state.logged_in = True
                    st.session_state.current_user = lu
                    st.rerun()
                else: st.error("Invalid credentials")
        with c2:
            if st.button("Forgot Details?"):
                if lu in st.session_state.users:
                    st.info(f"Password for {lu}: {st.session_state.users[lu]}")
                else: st.warning("Username not found.")
    st.stop()

# ================= PERMANENT SIDEBAR (SAB KUCH ISKE ANDAR HAI) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

with st.sidebar:
    st.title(f"🤖 New AI Menu")
    st.write(f"User: **{st.session_state.current_user}**")
    
    # --- YEH RAHA AAPKA MENU JISE MAINE EK SELECTBOX MEIN DAAL DIYA HAI ---
    menu = st.selectbox("📌 Menu", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    
    st.markdown("---")
    
    # Menu logic
    if menu == "About Creator":
        st.subheader("About")
        st.info(f"👤 **Creator:** {CREATOR_NAME}")
    elif menu == "Feedback":
        st.subheader("Feedback")
        f_msg = st.text_area("Write your feedback:")
        if st.button("Submit Feedback"):
            try:
                msg = MIMEText(f"Feedback: {f_msg}")
                msg['Subject'] = 'New AI Feedback'
                msg['From'] = MY_GMAIL
                msg['To'] = MY_GMAIL
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(MY_GMAIL, APP_PASS)
                    server.send_message(msg)
                st.success("Thanks for feedback")
            except: st.error("Error")
    elif menu == "Privacy Policy":
        st.subheader("Privacy")
        st.write("🔒 Secure processing via Groq.")
    elif menu == "Terms & Conditions":
        st.subheader("Terms")
        st.write("⚖️ Use responsibly.")
    
    st.markdown("---")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ================= WHATSAPP UI & CHAT SYSTEM =================
# Chat sirf tab dikhega jab Menu mein 'Chat' selected ho
if menu == "Chat":
    st.title("🤖 Chat Screen")
    st.markdown("""
    <style>
        header, footer {visibility: hidden;}
        .block-container {background-color: #0b141a;}
        .user-bubble { background-color: #005c4b; color: white; padding: 10px 15px; border-radius: 15px 15px 0 15px; margin: 8px 0; max-width: 75%; float: right; clear: both; }
        .ai-bubble { background-color: #202c33; color: white; padding: 10px 15px; border-radius: 15px 15px 15px 0; margin: 8px 0; max-width: 75%; float: left; clear: both; border-left: 4px solid #00a884; }
    </style>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state: 
        st.session_state.messages = []

    for i, m in enumerate(st.session_state.messages):
        cls = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{cls}">{m["content"]}</div>', unsafe_allow_html=True)

    u_input = st.chat_input("Ask something...")
    if u_input:
        st.session_state.messages.append({"role": "user", "content": u_input})
        sys = f"Your name is New AI. You were created by {CREATOR_NAME}."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": u_input}]
        )
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
        
