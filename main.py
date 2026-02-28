import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & CREDENTIALS =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohammad Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. REFRESH-PROOF SYSTEM =================
if "user_db" not in st.session_state:
    st.session_state.user_db = {"admin": "123"} # Default account

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 3. STYLISH LOGIN PAGE (NEW LOOK) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

# Modern CSS for Login
login_style = """
<style>
    .stApp { background-color: #0b141a; }
    .login-container {
        background: rgba(32, 44, 51, 0.8);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #00a884;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        text-align: center;
    }
    h1 { color: #00a884 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
</style>
"""
st.markdown(login_style, unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown('<div class="login-container"><h1>🤖 Welcome to New AI</h1><p style="color: #e9edef;">Smart AI by Siddique Mohammad Saif</p></div>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with t2:
        nu = st.text_input("Choose a Username", key="s_u")
        np = st.text_input("Choose a Password", type="password", key="s_p")
        if st.button("Create My Account"):
            if nu and np:
                st.session_state.user_db[nu] = np
                st.success(f"Account for {nu} created! Now switch to Login tab.")
            else: st.error("Please fill all fields.")

    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign In"):
                if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u
                    st.rerun()
                else: st.error("Invalid Username or Password")
        
        with col2:
            # FIXED FORGOT LOGIC
            if st.button("Forgot Password?"):
                if u == "":
                    st.warning("Pehle username toh likho bhai!")
                elif u in st.session_state.user_db:
                    st.info(f"Hi {u}, your password is: **{st.session_state.user_db[u]}**")
                else:
                    st.error("Ye username hamare paas nahi hai. Sign Up karein!")
    st.stop()

# ================= 4. SIDEBAR MENU (PERMANENT) =================
with st.sidebar:
    st.title("🤖 New AI Menu")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ================= 5. MAIN CHAT & PAGES =================
if menu == "Chat":
    st.title("💬 New AI")
    st.markdown("""<style>.user-bubble { background-color: #005c4b; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: right; clear: both; } .ai-bubble { background-color: #202c33; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: left; clear: both; border-left: 4px solid #00a884; }</style>""", unsafe_allow_html=True)
    
    for i, m in enumerate(st.session_state.messages):
        div = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant":
            if st.button(f"🔊 Listen", key=f"v_{i}"):
                tts = gTTS(text=m["content"], lang='hi')
                fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
                b64 = base64.b64encode(fp.read()).decode()
                st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    
    q = st.chat_input("Welcome to new ai")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": f"Your name is New AI. You were created by {CREATOR_NAME}."}, {"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content}); st.rerun()

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.write(f"**Developer:** Siddique Mohammad Saif")

elif menu == "Feedback":
    st.header("📝 Feedback")
    if st.button("Submit"): st.success("Thanks for feedback")

elif menu == "Privacy Policy":
    st.header("🔒 Privacy Policy")
    st.write("Secure AI processing by New AI.")

elif menu == "Terms & Conditions":
    st.header("⚖️ Terms & Conditions")
    st.write("Use New AI responsibly.")
        
