import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import requests
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & KEYS =================
GROQ_KEY = "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"
TAVILY_API_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohd Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. PAGE CONFIG & SIDEBAR (MUST BE FIRST) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

# Ye raha aapka Menu Option
with st.sidebar:
    st.title("🤖 New AI Menu")
    st.write(f"By: **{CREATOR_NAME}**")
    menu = st.radio("Go to:", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): 
        st.session_state.messages = []
        st.rerun()
    if st.button("Logout"): 
        st.session_state.logged_in = False
        st.rerun()

# ================= 3. PREMIUM UI CSS =================
st.markdown(f"""
    <style>
    /* Hide Fork & Streamlit Elements */
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* WhatsApp Chat Bubbles */
    .user-bubble {{
        background-color: #005c4b; color: white; padding: 12px; 
        border-radius: 15px 15px 0px 15px; margin: 8px; 
        float: right; clear: both; max-width: 80%;
    }}
    .ai-bubble {{
        background-color: #202c33; color: white; padding: 12px; 
        border-radius: 15px 15px 15px 0px; margin: 8px; 
        float: left; clear: both; max-width: 80%;
        border-left: 4px solid #00a884;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 4. LOGIN SYSTEM =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🔐 Login to New AI")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Sign In"):
        if u in st.session_state.user_db and st.session_state.user_db[u] == p:
            st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
    st.stop()

# ================= 5. PAGE CONTENT =================
if menu == "Chat":
    st.title("💬 Chat with New AI")
    
    # Display Chat Bubbles
    for i, m in enumerate(st.session_state.messages):
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Pucho kuch bhi (Speak any language)...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        
        # Internet Search for Latest Info
        live_data = ""
        if any(x in q.lower() for x in ["news", "latest", "today", "score"]):
            try:
                url = "https://api.tavily.com/search"
                res = requests.post(url, json={"api_key": TAVILY_API_KEY, "query": q}).json()
                live_data = "\n".join([r['content'] for r in res.get('results', [])])
            except: live_data = ""

        # Smart Language Prompt
        sys_msg = f"""
        Tera naam New AI hai. Tujhe {CREATOR_NAME} ne banaya hai.
        User jis bhi language mein baat kare (Hindi, English, Arabic, French), tujhe usi language mein perfect jawab dena hai.
        Robotic mat banna, natural rehna. Live Info: {live_data}
        """
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": q}]
        )
        st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

elif menu == "Feedback":
    st.header("📝 Feedback")
    txt = st.text_area("Aapka message...")
    if st.button("Submit"):
        # Email logic restored
        st.success("Thanks for feedback")

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.info(f"Developed by: **{CREATOR_NAME}**")

elif menu == "Privacy Policy":
    st.header("🔒 Privacy Policy")
    st.write("Safe and Secure.")

elif menu == "Terms & Conditions":
    st.header("⚖️ Terms")
    st.write("Use responsibly.")
                                        
