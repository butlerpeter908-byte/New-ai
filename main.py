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

# ================= 2. PREMIUM CSS (GLASSY + WHATSAPP) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Hide Fork & Streamlit Elements */
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    div[data-testid="stToolbar"] {{display: none !important;}}
    
    /* Login Page Glassy Look */
    .stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}
    
    /* WhatsApp Bubbles */
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

# ================= 3. SYSTEM & SEARCH =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

def google_search(query):
    try:
        url = "https://api.tavily.com/search"
        payload = {"api_key": TAVILY_API_KEY, "query": query, "max_results": 3}
        res = requests.post(url, json=payload).json()
        return "\n".join([f"- {r['content']}" for r in res.get('results', [])])
    except: return ""

# ================= 4. LOGIN PAGE =================
if not st.session_state.logged_in:
    st.title("🔐 Login to New AI")
    st.write(f"Created by **{CREATOR_NAME}**")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sign In"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Wrong details")
    with t2:
        nu = st.text_input("New User")
        np = st.text_input("New Pass", type="password")
        if st.button("Register"):
            if nu and np: st.session_state.user_db[nu] = np; st.success("Done!")
    st.stop()

# ================= 5. SIDEBAR MENU (MENU BUTTON HERE) =================
# Ye button top left corner mein dikhega
with st.sidebar:
    st.title("🤖 New AI Menu")
    st.write(f"By: {CREATOR_NAME}")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# ================= 6. CHAT & GLOBAL LANGUAGE =================
if menu == "Chat":
    st.title("💬 New AI (Global Language)")
    for i, m in enumerate(st.session_state.messages):
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Pucho kuch bhi (Ask in any language)...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        live_info = google_search(q) if any(x in q.lower() for x in ["news", "today", "latest"]) else ""
        
        # GLOBAL LANGUAGE PROMPT: Isse AI user ki language follow karega
        sys_p = f"""
        Tera naam New AI hai, creator {CREATOR_NAME} hai.
        User jis language mein sawal puche, tujhe hamesha usi language mein jawab dena hai. 
        English toh English, Hindi toh Hindi, Arabic toh Arabic. 
        Live Info: {live_info}
        """
        
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content}); st.rerun()

elif menu == "Feedback":
    st.header("📝 Feedback")
    f_txt = st.text_area("Message...")
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
    st.write("Data is secure.")

elif menu == "Terms & Conditions":
    st.header("⚖️ Terms & Conditions")
    st.write("Use responsibly.")
        
