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

# Aapka Naam Update Kar Diya Gaya Hai
CREATOR_NAME = "Siddique Mohd Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. PROFESSIONAL UI SETUP =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

# Hiding Streamlit Elements
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stToolbar"] {display: none !important;}
    
    /* WhatsApp Chat Bubbles */
    .user-bubble {
        background-color: #005c4b; color: white; padding: 12px; 
        border-radius: 15px 15px 0px 15px; margin: 8px; 
        float: right; clear: both; max-width: 70%;
    }
    .ai-bubble {
        background-color: #202c33; color: white; padding: 12px; 
        border-radius: 15px 15px 15px 0px; margin: 8px; 
        float: left; clear: both; max-width: 70%;
        border-left: 4px solid #00a884;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= 3. SYSTEM FUNCTIONS =================
def google_search(query):
    try:
        url = "https://api.tavily.com/search"
        payload = {"api_key": TAVILY_API_KEY, "query": query, "max_results": 3}
        res = requests.post(url, json=payload).json()
        return "\n".join([f"- {r['content']}" for r in res.get('results', [])])
    except: return ""

# ================= 4. LOGIN & SIDEBAR =================
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

# Sidebar Menu
with st.sidebar:
    st.title("🤖 New AI Menu")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# ================= 5. PAGE LOGIC =================
if menu == "Chat":
    st.title("💬 New AI")
    for i, m in enumerate(st.session_state.messages):
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant":
            if st.button(f"🔊 Listen", key=f"v_{i}"):
                tts = gTTS(text=m["content"], lang='hi')
                fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
                st.markdown(f'<audio src="data:audio/mp3;base64,{base64.b64encode(fp.read()).decode()}" autoplay="true"></audio>', unsafe_allow_html=True)

    q = st.chat_input("Welcome to new ai")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        live_info = google_search(q) if any(x in q.lower() for x in ["news", "today", "score"]) else ""
        
        # Natural Hinglish Prompt
        sys_p = f"Tera naam New AI hai. Tujhe {CREATOR_NAME} ne banaya hai. Ekdam natural Hinglish mein baat kar. Live Data: {live_info}"
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content}); st.rerun()

elif menu == "Feedback":
    st.header("📝 Feedback")
    f_txt = st.text_area("Aapka message...")
    if st.button("Submit"):
        msg = MIMEText(f"User: {st.session_state.current_user}\nMsg: {f_txt}")
        msg['Subject'] = "New AI Feedback"; msg['From'] = MY_GMAIL; msg['To'] = MY_GMAIL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        st.success("Thanks for feedback")

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.info(f"This AI is developed by: **{CREATOR_NAME}**")

elif menu == "Privacy Policy":
    st.header("🔒 Privacy Policy")
    st.write("Aapka data aur chats secure hain.")

elif menu == "Terms & Conditions":
    st.header("⚖️ Terms & Conditions")
    st.write("Use New AI for helpful purposes only.")
            
