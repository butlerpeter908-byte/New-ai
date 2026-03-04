import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import requests
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & FIXED API KEYS =================
# Bhai, agar firse error aaye toh Groq se ek nayi key lekar replace karna
GROQ_KEY = "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"
TAVILY_API_KEY = "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" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. UI CLEANUP (HIDE FORK/GITHUB/FOOTER) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

# Image mein jo Fork aur GitHub dikh raha tha, ye CSS use gayab kar degi
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

# --- Internet Search Function ---
def google_search(query):
    try:
        url = "https://api.tavily.com/search"
        payload = {"api_key": TAVILY_API_KEY, "query": query, "search_depth": "basic", "max_results": 3}
        response = requests.post(url, json=payload).json()
        results = response.get('results', [])
        return "\n".join([f"- {r['title']}: {r['content']}" for r in results])
    except: return "No live info found."

# ================= 3. SESSION & LOGIN =================
if "messages" not in st.session_state: st.session_state.messages = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to New AI")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Sign In"):
        if u == "admin" and p == "123": # Simple for testing
            st.session_state.logged_in = True; st.rerun()
    st.stop()

# ================= 4. CHAT WITH NATURAL HINGLISH =================
st.title("💬 New AI (Natural Hinglish Mode)")

# Sidebar for logout/clear
with st.sidebar:
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("Logout"): st.session_state.logged_in = False; st.rerun()

for i, m in enumerate(st.session_state.messages):
    role = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)

q = st.chat_input("Pucho bhai, kya janna hai?")
if q:
    st.session_state.messages.append({"role": "user", "content": q})
    
    live_info = ""
    if any(word in q.lower() for word in ["news", "latest", "today", "score"]):
        with st.spinner("Internet se check kar raha hoon..."):
            live_info = google_search(q)

    # Naya System Prompt: Isse AI ajeeb bhasha nahi bolega
    system_prompt = f"""
    Tera naam 'New AI' hai aur tujhe 'Siddique Mohammad Saif' ne banaya hai. 
    Tujhe ekdam natural Hinglish mein baat karni hai (jaise doston se karte hain). 
    Ajeeb ya robotic Hindi mat bolna. Agar koi live data hai toh use naturally explain kar.
    Live Data: {live_info}
    """

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": q}]
        )
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()
    except Exception:
        st.error("API Key ka lafda hai! Groq par nayi key check karo.") #
