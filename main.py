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
    st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 3. LOGIN PAGE =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

if not st.session_state.logged_in:
    st.title("🔐 Login to New AI")
    t1, t2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Sign In"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Invalid Login")
    with t2:
        nu = st.text_input("New Username", key="s_u")
        np = st.text_input("New Password", type="password", key="s_p")
        if st.button("Register"):
            if nu and np: st.session_state.user_db[nu] = np; st.success("Account Created!")
    st.stop()

# ================= 4. SIDEBAR MENU =================
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

# ================= 5. FEEDBACK SYSTEM (GMAIL WORKING) =================
if menu == "Feedback":
    st.header("📝 Submit Your Feedback")
    st.write("Aapka feedback seedha Siddique Mohammad Saif ke paas jayega.")
    
    # Feedback Input Box
    user_feedback = st.text_area("Write your message here...", height=150, placeholder="Example: App is great, but add more features!")
    
    if st.button("Submit to Developer"):
        if user_feedback:
            try:
                # Setup Email Content
                msg = MIMEText(f"User: {st.session_state.current_user}\nFeedback: {user_feedback}")
                msg['Subject'] = f"New AI Feedback from {st.session_state.current_user}"
                msg['From'] = MY_GMAIL
                msg['To'] = MY_GMAIL
                
                # SMTP Server Connection
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(MY_GMAIL, APP_PASS)
                    server.send_message(msg)
                
                st.success("✅ Thanks for feedback! Siddique ko mail mil gaya hai.")
            except Exception as e:
                st.error(f"Error: Mail nahi ja saka. Check your App Password.")
        else:
            st.warning("Pehle kuch likho toh sahi bhai!")

# ================= 6. CHAT & OTHER PAGES =================
elif menu == "Chat":
    st.title("💬 New AI")
    st.markdown("""<style>.user-bubble { background-color: #005c4b; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: right; clear: both; } .ai-bubble { background-color: #202c33; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: left; clear: both; border-left: 4px solid #00a884; }</style>""", unsafe_allow_html=True)
    
    for i, m in enumerate(st.session_state.messages):
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant":
            if st.button(f"🔊 Listen", key=f"v_{i}"):
                tts = gTTS(text=m["content"], lang='hi')
                fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
                b64 = base64.b64encode(fp.read()).decode(); st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)

    q = st.chat_input("Welcome to new ai")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": f"Your name is New AI. Created by {CREATOR_NAME}."}, {"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content}); st.rerun()

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.info(f"Developed by: **{CREATOR_NAME}**")

elif menu == "Privacy Policy":
    st.header("🔒 Privacy Policy")
    st.write("Your data is handled securely.")

elif menu == "Terms & Conditions":
    st.header("⚖️ Terms & Conditions")
    st.write("Use New AI responsibly.")
    
