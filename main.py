import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import requests
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & LIVE API KEYS =================
GROQ_KEY = "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"
TAVILY_API_KEY = "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" 

MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn"
CREATOR_NAME = "Siddique Mohammad Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. LIVE SEARCH LOGIC =================
def google_search(query):
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": 3
        }
        response = requests.post(url, json=payload).json()
        results = response.get('results', [])
        search_data = "\n".join([f"- {r['title']}: {r['content']}" for r in results])
        return search_data if search_data else "No live info found."
    except Exception:
        return "Search currently unavailable."

# ================= 3. ULTRA CLEAN UI (NO FORK/FOOTER) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

# Hiding Streamlit elements for a professional look
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            button[title="View source on GitHub"] {display:none;}
            div[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ================= 4. LOGIN & SESSION SYSTEM =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.title("🔐 Login to New AI")
    t1, t2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("Sign In"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
            else: st.error("Invalid Login")
        if st.button("Forgot Password?"):
            if u in st.session_state.user_db: st.info(f"Password: {st.session_state.user_db[u]}")
            else: st.error("User not found.")
    with t2:
        nu = st.text_input("New User", key="s_u")
        np = st.text_input("New Pass", type="password", key="s_p")
        if st.button("Register"):
            if nu and np: st.session_state.user_db[nu] = np; st.success("Done!")
    st.stop()

# ================= 5. SIDEBAR MENU =================
with st.sidebar:
    st.title("🤖 New AI Menu")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback", "Privacy Policy"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

# ================= 6. CHAT WITH LIVE NEWS FEATURE =================
if menu == "Chat":
    st.title("💬 New AI (Live Internet)")
    st.markdown("""<style>.user-bubble { background-color: #005c4b; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: right; clear: both; } .ai-bubble { background-color: #202c33; color: white; padding: 10px; border-radius: 10px; margin: 5px; float: left; clear: both; border-left: 4px solid #00a884; }</style>""", unsafe_allow_html=True)
    
    for i, m in enumerate(st.session_state.messages):
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)
        if m["role"] == "assistant" and st.button(f"🔊 Listen", key=f"v_{i}"):
            tts = gTTS(text=m["content"], lang='hi')
            fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
            st.markdown(f'<audio src="data:audio/mp3;base64,{base64.b64encode(fp.read()).decode()}" autoplay="true"></audio>', unsafe_allow_html=True)

    q = st.chat_input("Welcome to new ai")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        
        # Trigger live search for news/latest queries
        live_info = ""
        news_keywords = ["news", "khabar", "today", "score", "weather", "latest", "price", "stock"]
        if any(word in q.lower() for word in news_keywords):
            with st.spinner("Searching live internet..."):
                live_info = google_search(q)
        
        # Final Prompt for AI
        sys_msg = f"Your name is New AI. Created by {CREATOR_NAME}. Use this live data if relevant: {live_info}"
        try:
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": q}]
            )
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except Exception: st.error("Connection issue. Try again.")

elif menu == "Feedback":
    st.header("📝 Feedback")
    f_msg = st.text_area("Message")
    if st.button("Submit"):
        try:
            msg = MIMEText(f"User: {st.session_state.current_user}\nMsg: {f_msg}")
            msg['Subject'] = "New AI Feedback"; msg['From'] = MY_GMAIL; msg['To'] = MY_GMAIL
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
            st.success("Thanks for feedback")
        except: st.error("Email Error")

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.info(f"Developed by: **{CREATOR_NAME}**")

elif menu == "Privacy Policy":
    st.header("🔒 Privacy Policy")
    st.write("We respect your privacy. No data is shared with third parties.")
        
