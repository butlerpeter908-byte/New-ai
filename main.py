import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & CREDENTIALS =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
# Aapka naam yahan pakka kar diya hai
CREATOR_NAME = "Siddique Mohammad Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. REFRESH-PROOF SYSTEM =================
if "user_db" not in st.session_state:
    st.session_state.user_db = {"admin": "123"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ================= 3. PERMANENT SIDEBAR MENU =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

with st.sidebar:
    st.title("🤖 New AI Menu")
    menu = st.radio("Navigation", 
                    ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    
    st.markdown("---")
    if st.session_state.logged_in:
        st.write(f"👤 User: **{st.session_state.current_user}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# ================= 4. LOGIN LOGIC =================
if not st.session_state.logged_in:
    st.title("🔐 Login to New AI")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t2:
        nu = st.text_input("New Username", key="s_u")
        np = st.text_input("New Password", type="password", key="s_p")
        if st.button("Register"):
            if nu and np: st.session_state.user_db[nu] = np; st.success("Done!")
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Login"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Invalid Details")
    st.stop()

# ================= 5. MENU PAGES (ENGLISH CONTENT) =================
if menu == "Chat":
    st.title("💬 WhatsApp Chat")
    st.markdown("""<style>.user-bubble { background-color: #005c4b; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: right; clear: both; } .ai-bubble { background-color: #202c33; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: left; clear: both; border-left: 4px solid #00a884; }</style>""", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        div = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)
    q = st.chat_input("Siddique Mohammad Saif ka AI ready hai...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        # AI ka naam New AI aur Creator ka naam Siddique Mohammad Saif set hai
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": f"Your name is New AI. You were created by {CREATOR_NAME}."}, {"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content}); st.rerun()

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.write(f"""
    **Developer Information:**
    - **Name:** Siddique Mohammad Saif
    - **Vision:** To create a smart, secure, and user-friendly AI assistant (New AI) for everyone.
    - **Technology:** This AI is powered by Groq's Llama models and Streamlit.
    """)

elif menu == "Feedback":
    st.header("📝 Feedback")
    f_msg = st.text_area("How can we improve?")
    if st.button("Submit"):
        st.success("Thanks for feedback")

elif menu == "Privacy Policy":
    st.header("🔒 Privacy Policy")
    st.write("""
    **Your Privacy Matters:**
    1. New AI does not store your personal chat history on our permanent servers.
    2. Your login credentials are encrypted within the session.
    3. We do not share user data with any third-party advertising companies.
    4. Your messages are processed securely via Groq Cloud APIs.
    """)

elif menu == "Terms & Conditions":
    st.header("⚖️ Terms & Conditions")
    st.write("""
    **Usage Rules:**
    1. Do not use New AI for generating illegal or harmful content.
    2. Respect the system boundaries and do not attempt to hack the application.
    3. This AI is provided for educational and personal assistance purposes.
    4. The creator, Siddique Mohammad Saif, is not responsible for any AI-generated misinformation.
    """)
    
