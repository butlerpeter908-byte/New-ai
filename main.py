import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# ================= CREDENTIALS & IDENTITY =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohammad Saif" # Aapka Naam

client = Groq(api_key=GROQ_KEY)

# ================= AUTHENTICATION =================
if "users" not in st.session_state:
    st.session_state.users = {} 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🤖 Welcome to New AI")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")
        if st.button("Register"):
            if u and p: st.session_state.users[u] = p; st.success("Done!")
    with t1:
        lu = st.text_input("Username")
        lp = st.text_input("Password", type="password")
        if st.button("Login"):
            if lu in st.session_state.users and st.session_state.users[lu] == lp:
                st.session_state.logged_in = True
                st.session_state.current_user = lu
                st.rerun()
    st.stop()

# ================= UI & WHATSAPP CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
<style>
    header, footer {{visibility: hidden;}}
    .block-container {{background-color: #0b141a; padding-top: 1rem;}}
    /* User Message - WhatsApp Green */
    .user-bubble {{
        background-color: #005c4b; color: #e9edef;
        padding: 10px 15px; border-radius: 15px 15px 0 15px;
        margin: 8px 0; max-width: 75%; float: right; clear: both;
        font-family: sans-serif; box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
    }}
    /* AI Message - WhatsApp Dark Grey */
    .ai-bubble {{
        background-color: #202c33; color: #e9edef;
        padding: 10px 15px; border-radius: 15px 15px 15px 0;
        margin: 8px 0; max-width: 75%; float: left; clear: both;
        font-family: sans-serif; box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
        border-left: 4px solid #00a884;
    }}
    .stChatInput {{ position: fixed; bottom: 30px; }}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR MENU =================
with st.sidebar:
    st.title(f"👤 {st.session_state.current_user}")
    menu = st.selectbox("Menu", ["Chat", "About Creator", "Feedback", "Privacy", "Terms"])
    if menu == "About Creator":
        st.write(f"This AI was created by **{CREATOR_NAME}**.")
    elif menu == "Feedback":
        f = st.text_area("Feedback:")
        if st.button("Submit"): st.success("Sent to Gmail!")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ================= MAIN CHAT =================
st.title("🤖 New AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Messages
for i, m in enumerate(st.session_state.messages):
    div_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{div_class}">{m["content"]}</div>', unsafe_allow_html=True)
    if m["role"] == "assistant":
        if st.button(f"🔊 Listen", key=f"v_{i}"):
            tts = gTTS(text=m["content"], lang='hi', tld='co.in')
            fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)

# --- INPUT ---
u_input = st.chat_input("Type a message...")
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("..."):
        # System prompt for identity
        sys_prompt = f"Your name is New AI. You were created by {CREATOR_NAME}. Answer in the user's language."
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys_prompt}, 
                      {"role": "user", "content": st.session_state.messages[-1]["content"]}]
        )
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
