import streamlit as st
from groq import Groq
import requests
import base64
from gtts import gTTS
import io

# ================= 1. IDENTITY & KEYS =================
GROQ_KEY = "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"
TAVILY_API_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. PREMIUM CSS (LOGIN & CHAT) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Hide Fork & Streamlit Elements */
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* Premium Glassy Background */
    .stApp {{
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }}
    
    /* WhatsApp Style Bubbles */
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

# ================= 3. SIDEBAR / MENU (ALWAYS VISIBLE) =================
# Ye sidebar hamesha dikhega, jisme aapka naam aur options honge
with st.sidebar:
    st.title("🤖 New AI Menu")
    st.write(f"Created by: **{CREATOR_NAME}**")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): 
        st.session_state.messages = []
        st.rerun()
    if st.button("Logout"): 
        st.session_state.logged_in = False
        st.rerun()

# ================= 4. LOGIN SYSTEM (FIXED LOOK) =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    # Glassy Login Container
    st.markdown('<div style="text-align: center; color: white;">', unsafe_allow_html=True)
    st.title("🔐 Login to New AI")
    st.write(f"Developed by {CREATOR_NAME}")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    with tab1:
        u = st.text_input("Username", key="l_user")
        p = st.text_input("Password", type="password", key="l_pass")
        if st.button("Sign In"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Invalid Username or Password")
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            if nu and np: st.session_state.user_db[nu] = np; st.success("Account Created!")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= 5. CHAT & GLOBAL LANGUAGE LOGIC =================
if menu == "Chat":
    st.title("💬 Chat Session")
    
    for i, m in enumerate(st.session_state.messages):
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Ask anything in any language...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        
        # Internet Search for Latest Info
        live_data = ""
        if any(x in q.lower() for x in ["news", "latest", "today", "score"]):
            try:
                r = requests.post("https://api.tavily.com/search", json={"api_key": TAVILY_API_KEY, "query": q})
                live_data = "\n".join([res['content'] for res in r.json().get('results', [])])
            except: live_data = ""

        # Global Language System Prompt
        sys_msg = f"Your name is New AI, created by {CREATOR_NAME}. Answer in the SAME language the user asks. Be natural. Data: {live_data}"
        
        try:
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": q}]
            )
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: st.error("API Key Error. Please update GROQ_KEY.")

elif menu == "About Creator":
    st.header("👤 About Creator")
    st.info(f"This AI was built with ❤️ by **{CREATOR_NAME}**.")
        
