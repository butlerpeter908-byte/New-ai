import streamlit as st
from groq import Groq
import requests
import base64

# ================= 1. IDENTITY & KEYS =================
GROQ_KEY = "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"
TAVILY_API_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. MOBILE-FIRST PREMIUM CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Hide Streamlit Default Header/Footer */
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* MOBILE MENU BUTTON VISIBILITY (IMPORTANT) */
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00a884 !important;
        color: white !important;
        border-radius: 50% !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 999999 !important;
        display: block !important;
    }}

    /* Glassy Dark Background */
    .stApp {{
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }}
    
    /* WhatsApp Style Bubbles */
    .user-bubble {{
        background-color: #005c4b; color: white; padding: 12px; 
        border-radius: 15px 15px 0px 15px; margin: 8px; 
        float: right; clear: both; max-width: 85%;
    }}
    .ai-bubble {{
        background-color: #202c33; color: white; padding: 12px; 
        border-radius: 15px 15px 15px 0px; margin: 8px; 
        float: left; clear: both; max-width: 85%;
        border-left: 4px solid #00a884;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. SIDEBAR (MENU) SETUP =================
# Sidebar ko hamesha visible rakhne ke liye settings
with st.sidebar:
    st.title("🤖 New AI Menu")
    st.write(f"By: **{CREATOR_NAME}**")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions"])
    st.markdown("---")
    if st.button("🗑️ Clear Chat"): 
        st.session_state.messages = []
        st.rerun()
    if st.button("Logout"): 
        st.session_state.logged_in = False
        st.rerun()

# ================= 4. LOGIN SYSTEM (GLASSY LOOK) =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.logged_in:
    st.markdown('<div style="margin-top: 50px; text-align: center; color: white;">', unsafe_allow_html=True)
    st.title("🔐 Login to New AI")
    st.write(f"Created by {CREATOR_NAME}")
    
    u = st.text_input("Username", key="l_u")
    p = st.text_input("Password", type="password", key="l_p")
    if st.button("Sign In"):
        if u in st.session_state.user_db and st.session_state.user_db[u] == p:
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("Wrong Username/Password")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= 5. CHAT LOGIC (GLOBAL LANGUAGE) =================
if menu == "Chat":
    st.title("💬 New AI Chat")
    
    # Display messages
    for m in st.session_state.messages:
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Ask me anything...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        
        # Search News logic
        live_data = ""
        if any(x in q.lower() for x in ["news", "latest", "today"]):
            try:
                r = requests.post("https://api.tavily.com/search", json={"api_key": TAVILY_API_KEY, "query": q})
                live_data = "\n".join([res['content'] for res in r.json().get('results', [])])
            except: live_data = ""

        # Global Language Support
        sys_msg = f"Name: New AI. Creator: {CREATOR_NAME}. Answer in the language user uses. Data: {live_data}"
        
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": q}]
        )
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif menu == "About Creator":
    st.header("👤 Creator Info")
    st.success(f"Built by: **{CREATOR_NAME}**")
            
