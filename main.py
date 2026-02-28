import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ================= 1. CREDENTIALS =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohammad Saif"

client = Groq(api_key=GROQ_KEY)

# ================= 2. REFRESH-PROOF LOGIN =================
# User data ko session mein save rakhne ke liye logic
if "user_db" not in st.session_state:
    st.session_state.user_db = {"admin": "123"} # Permanent admin account

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

# ================= 3. PERMANENT SIDEBAR MENU =================
# Isko hum Authentication se PEHLE define karenge taaki ye hamesha dikhe
with st.sidebar:
    st.title("🤖 New AI Menu")
    
    # Ye Radio button hamesha sidebar mein dikhega
    app_mode = st.radio("Navigate:", 
                        ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    
    st.markdown("---")
    if st.session_state.is_logged_in:
        st.write(f"Logged in as: **{st.session_state.current_user}**")
        if st.button("Logout"):
            st.session_state.is_logged_in = False
            st.rerun()

# ================= 4. LOGIN PAGE LOGIC =================
if not st.session_state.is_logged_in:
    st.title("🔐 Login to New AI")
    tab_log, tab_sign = st.tabs(["Login", "Sign Up"])
    
    with tab_sign:
        new_u = st.text_input("Create Username", key="s_u")
        new_p = st.text_input("Create Password", type="password", key="s_p")
        if st.button("Register Account"):
            if new_u and new_p:
                st.session_state.user_db[new_u] = new_p
                st.success("Registration Successful! Please Login.")
            else: st.error("Please fill all details")

    with tab_log:
        u_name = st.text_input("Username", key="l_u")
        u_pass = st.text_input("Password", type="password", key="l_p")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Login"):
                if u_name in st.session_state.user_db and st.session_state.user_db[u_name] == u_pass:
                    st.session_state.is_logged_in = True
                    st.session_state.current_user = u_name
                    st.rerun()
                else: st.error("Wrong Username or Password")
        with c2:
            if st.button("Forgot Details?"):
                if u_name in st.session_state.user_db:
                    st.info(f"Password for {u_name} is: {st.session_state.user_db[u_name]}")
                else: st.warning("Username not found.")
    st.stop() # Login hone tak aage ka code nahi chalega

# ================= 5. MAIN CONTENT (MENU PAGES) =================
if app_mode == "Chat":
    st.title("💬 WhatsApp Chat")
    # WhatsApp Look CSS
    st.markdown("""
    <style>
        header, footer {visibility: hidden;}
        .block-container {background-color: #0b141a;}
        .user-bubble { background-color: #005c4b; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: right; clear: both; }
        .ai-bubble { background-color: #202c33; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: left; clear: both; border-left: 4px solid #00a884; }
    </style>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state: st.session_state.chat_history = []

    for chat in st.session_state.chat_history:
        style = "user-bubble" if chat["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{style}">{chat["content"]}</div>', unsafe_allow_html=True)

    user_q = st.chat_input("Siddique Mohammad Saif ka AI ready hai...")
    if user_q:
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Your name is New AI, created by {CREATOR_NAME}."}, 
                      {"role": "user", "content": user_q}]
        )
        st.session_state.chat_history.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

elif app_mode == "About Creator":
    st.header("👤 About Creator")
    st.info(f"This AI application is designed and developed by **{CREATOR_NAME}**.")

elif app_mode == "Feedback":
    st.header("📝 Submit Feedback")
    f_msg = st.text_area("Your Message:")
    if st.button("Send"):
        try:
            msg = MIMEText(f"Feedback from {st.session_state.current_user}: {f_msg}")
            msg['Subject'] = 'New AI Feedback'
            msg['From'] = MY_GMAIL
            msg['To'] = MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(MY_GMAIL, APP_PASS)
                server.send_message(msg)
            st.success("Thanks for feedback")
        except: st.error("Feedback error")

elif app_mode == "Privacy Policy":
    st.header("🔒 Privacy Policy")
    st.write("Aapka data secure hai aur hum koi bhi personal chat save nahi karte.")

elif app_mode == "Terms & Conditions":
    st.header("⚖️ Terms & Conditions")
    st.write("Is AI ka istemal educational aur creative kamo ke liye karein.")
    
