import streamlit as st
from groq import Groq
import requests

# ================= 1. IDENTITY & KEYS =================
GROQ_KEY = "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"
TAVILY_API_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. ULTIMATE UI CSS (NO BLANK SPACE) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* 1. Removing Extra Space and Streamlit Header */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }}
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{background: rgba(0,0,0,0);}}
    
    /* 2. Custom Green Sidebar Button for Mobile */
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00a884 !important;
        color: white !important;
        border-radius: 50% !important;
    }}

    /* 3. Glassy Background & Chat Bubbles */
    .stApp {{
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }}
    
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

    /* 4. Cleaning the "Chatting as" Header */
    .chat-header {{
        font-size: 1.2rem;
        font-weight: bold;
        color: #00a884;
        text-align: center;
        margin-bottom: 20px;
        padding: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. LOGIC & AUTH =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.title("🤖 New AI Menu")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback"])
    if st.button("Logout"): 
        st.session_state.logged_in = False
        st.rerun()

# --- Login / Sign Up Page ---
if not st.session_state.logged_in:
    # Blank space fix: Title starts higher up
    st.title("🔐 Welcome to New AI")
    st.write(f"Developed by **{CREATOR_NAME}**")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sign In"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            st.session_state.user_db[nu] = np
            st.success("Account Created!")
    st.stop()

# ================= 4. REFINED CHAT PAGE =================
if menu == "Chat":
    # Refined Header instead of large blue text
    st.markdown(f'<div class="chat-header">💬 Chatting as {st.session_state.current_user}</div>', unsafe_allow_html=True)
    
    for m in st.session_state.messages:
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Pucho kuch bhi...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        # AI Response Logic (Same as before but with Global Language support)
        sys_p = f"Name: New AI. Creator: {CREATOR_NAME}. Match user's language."
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": q}])
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except:
            st.error("Authentication Error: Groq key check karo bhai!")

elif menu == "About Creator":
    st.title("👤 Creator")
    st.info(f"Made by **{CREATOR_NAME}**")
    
