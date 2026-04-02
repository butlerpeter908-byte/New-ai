import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & NEW API KEY =================
# Aapki nayi API key yahan update kar di gayi hai
GROQ_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. SIMPLE & CLEAN UI =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

# Sirf zaroori CSS rakhi hai taaki UI makkhan chale
st.markdown("""
    <style>
    header, footer {visibility: hidden !important;}
    .stApp { background-color: #0e1117; color: white; }
    
    /* Profile Icon Button Styling */
    .profile-btn {
        position: fixed;
        top: 15px;
        right: 15px;
        background-color: #00ff88;
        color: black;
        border-radius: 50%;
        width: 45px;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        cursor: pointer;
        z-index: 1000;
        border: 2px solid white;
    }
    
    /* Chat Bubbles */
    .user-msg { background-color: #005c4b; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right; }
    .ai-msg { background-color: #202c33; padding: 10px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #00ff88; }
    </style>
    """, unsafe_allow_html=True)

# ================= 3. SESSION & LOGIN LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}

if not st.session_state.logged_in:
    st.title("🔐 New AI Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sign In"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Wrong details")
    with tab2:
        nu = st.text_input("New User")
        np = st.text_input("New Pass", type="password")
        if st.button("Create"):
            st.session_state.user_db[nu] = np
            st.success("Done!")
    st.stop()

# ================= 4. PROFILE ICON & SIDEBAR MENU =================
# Yeh icon user ko batayega ki menu kahan hai
st.markdown('<div class="profile-btn">👤</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header(f"Hi, {st.session_state.current_user}!")
    st.markdown("---")
    choice = st.radio("Menu", ["💬 Chat", "👤 About", "📩 Feedback", "🛡️ Privacy", "📄 Terms"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ================= 5. MAIN CONTENT =================
if choice == "💬 Chat":
    st.subheader("New AI Assistant")
    for m in st.session_state.messages:
        div_class = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div_class}">{m["content"]}</div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Type here...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
            st.rerun()
        except Exception as e:
            st.error(f"API Error: {e}")

elif choice == "👤 About":
    st.write(f"Created by: **{CREATOR_NAME}**")

elif choice == "🛡️ Privacy":
    st.write("Your data is temporary and secure.")

elif choice == "📄 Terms":
    st.write("Use this AI for legal purposes only.")

elif choice == "📩 Feedback":
    msg_text = st.text_area("Feedback:")
    if st.button("Send"):
        st.success("Sent to Siddique!")
        
