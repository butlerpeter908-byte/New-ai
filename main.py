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

# ================= 2. ALL-IN-ONE PREMIUM CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Hide Streamlit Trash */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    div[data-testid="stToolbar"] {{display: none !important;}}
    
    /* Premium Glassy Login Page */
    .stApp {{
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }}
    .login-box {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        color: white;
    }}
    
    /* WhatsApp Chat Bubbles */
    .user-bubble {{
        background-color: #005c4b; color: white; padding: 12px; 
        border-radius: 15px 15px 0px 15px; margin: 8px; 
        float: right; clear: both; max-width: 75%;
    }}
    .ai-bubble {{
        background-color: #202c33; color: white; padding: 12px; 
        border-radius: 15px 15px 15px 0px; margin: 8px; 
        float: left; clear: both; max-width: 75%;
        border-left: 4px solid #00a884;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- Internet Search ---
def google_search(query):
    try:
        url = "https://api.tavily.com/search"
        payload = {"api_key": TAVILY_API_KEY, "query": query, "max_results": 3}
        res = requests.post(url, json=payload).json()
        return "\n".join([f"- {r['content']}" for r in res.get('results', [])])
    except: return ""

# ================= 3. SESSION & LOGIN (GLASSY LOOK) =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.title("🔐 Login to New AI")
    st.write(f"Created by {CREATOR_NAME}")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Sign In"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Invalid Username or Password")
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            if nu and np: st.session_state.user_db[nu] = np; st.success("Account Created! Now Login.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= 4. SIDEBAR MENU (RESTORED) =================
with st.sidebar:
    st.title(f"🤖 New AI")
    st.write(f"By: {CREATOR_NAME}")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# ================= 5. MAIN CHAT & PAGES =================
if menu == "Chat":
    st.title("💬 New AI (Live)")
    for i, m in enumerate(st.session_state.messages):
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant" and st.button(f"🔊 Listen", key=f"v_{i}"):
            tts = gTTS(text=m["content"], lang='hi')
            fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
            st.markdown(f'<audio src="data:audio/mp3;base64,{base64.b64encode(fp.read()).decode()}" autoplay="true"></audio>', unsafe_allow_html=True)

    q = st.chat_input("Kaise ho bhai?")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        live_info = google_search(q) if any(x in q.lower() for x in ["news", "today", "score", "latest"]) else ""
        sys_p = f"Tera naam New AI hai. Tujhe {CREATOR_NAME} ne banaya hai. Natural Hinglish mein baat kar. Live Data: {live_info}"
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content}); st.rerun()

elif menu == "Feedback":
    st.header("📝 Feedback")
    f_txt = st.text_area("Write message...")
    if st.button("Submit"):
        msg = MIMEText(f"User: {st.session_state.current_user}\nMsg: {f_txt}")
        msg['Subject'] = "New AI Feedback"; msg['From'] = MY_GMAIL; msg['To'] = MY_GMAIL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        st.success("Thanks for feedback")

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.info(f"Developed by: **{CREATOR_NAME}**")

elif menu == "Privacy Policy":
    st.header("🔒 Privacy Policy")
    st.write("Aapki privacy hamari priority hai.")

elif menu == "Terms & Conditions":
    st.header("⚖️ Terms & Conditions")
    st.write("Enjoy New AI responsibly.")
        
