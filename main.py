import streamlit as st
from groq import Groq
import requests

# ================= 1. IDENTITY & KEYS =================
GROQ_KEY = "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"
TAVILY_API_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. ULTIMATE UI CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* 1. Removing Top Blank Space & Streamlit Branding */
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }}
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{background: rgba(0,0,0,0);}}
    
    /* 2. Mobile Menu Button Styling */
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00a884 !important;
        color: white !important;
        border-radius: 50% !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 99999;
    }}

    /* 3. Dark Glassy Background */
    .stApp {{
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }}
    
    /* 4. WhatsApp Chat Bubbles */
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

    /* 5. Clean Welcome Header (No Email) */
    .welcome-header {{
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 10px;
        padding: 15px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. SESSION & LOGIN =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

# Sidebar Menu
with st.sidebar:
    st.title("🤖 New AI Menu")
    st.write(f"By: **{CREATOR_NAME}**")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback"])
    st.markdown("---")
    if st.button("Logout"): 
        st.session_state.logged_in = False
        st.rerun()

# Login / Sign Up Page
if not st.session_state.logged_in:
    st.markdown('<div style="padding-top: 40px; text-align: center;">', unsafe_allow_html=True)
    st.title("🔐 Welcome to New AI")
    st.write(f"Developed by {CREATOR_NAME}")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    with tab1:
        u = st.text_input("Username", key="l_user")
        p = st.text_input("Password", type="password", key="l_pass")
        if st.button("Sign In", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
    with tab2:
        nu = st.text_input("New Username", key="s_user")
        np = st.text_input("New Password", type="password", key="s_pass")
        if st.button("Register Account", use_container_width=True):
            st.session_state.user_db[nu] = np
            st.success("Account Created! Login now.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= 4. CHAT PAGE (CLEAN LOOK) =================
if menu == "Chat":
    # Refined Welcome Header
    st.markdown('<div class="welcome-header">🤖 Welcome to New AI</div>', unsafe_allow_html=True)
    
    for m in st.session_state.messages:
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Pucho kuch bhi...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        
        # News Search logic
        live_info = ""
        if any(x in q.lower() for x in ["news", "today", "score"]):
            try:
                r = requests.post("https://api.tavily.com/search", json={"api_key": TAVILY_API_KEY, "query": q})
                live_info = "\n".join([res['content'] for res in r.json().get('results', [])])
            except: live_info = ""

        sys_msg = f"Name: New AI. Creator: {CREATOR_NAME}. Answer in user's language. Data: {live_info}"
        
        try:
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": q}]
            )
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except:
            st.error("Authentication Error: Please check Groq Key.") #

elif menu == "About Creator":
    st.header("👤 About")
    st.info(f"Designed and Developed by: **{CREATOR_NAME}**")
                                          
