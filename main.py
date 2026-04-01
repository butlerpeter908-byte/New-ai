import streamlit as st
from groq import Groq
import requests

# ================= 1. IDENTITY & KEYS =================
GROQ_KEY = "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"
TAVILY_API_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. PREMIUM UI CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Removing Top Space & Branding */
    .block-container {{ padding-top: 0rem !important; }}
    header, footer {{visibility: hidden !important;}}
    
    /* Dark Glassy Theme */
    .stApp {{
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }}

    /* WhatsApp Style Chat Bubbles (Right/Left Alignment) */
    .chat-container {{
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    .user-bubble {{
        background-color: #005c4b; 
        color: white; 
        padding: 12px; 
        border-radius: 15px 15px 0px 15px; 
        margin: 5px; 
        align-self: flex-end; /* User on Right */
        max-width: 80%;
        word-wrap: break-word;
    }}
    .ai-bubble {{
        background-color: #202c33; 
        color: white; 
        padding: 12px; 
        border-radius: 15px 15px 15px 0px; 
        margin: 5px; 
        align-self: flex-start; /* AI on Left */
        max-width: 80%;
        border-left: 4px solid #00a884;
        word-wrap: break-word;
    }}

    .welcome-header {{
        font-size: 1.5rem; font-weight: bold; color: #ffffff;
        text-align: center; margin-top: 20px; padding: 15px;
        background: rgba(255, 255, 255, 0.05); border-radius: 10px;
    }}

    /* Mobile Sidebar Button Visibility */
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00a884 !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. SESSION STATE (SAVE LOGIN) =================
# Isse user ka login status save rahega jab tak session active hai
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "current_user" not in st.session_state: st.session_state.current_user = ""

# ================= 4. AUTHENTICATION PAGE =================
if not st.session_state.logged_in:
    st.markdown('<div style="padding-top: 50px; text-align: center;">', unsafe_allow_html=True)
    st.title("🔐 Welcome to New AI")
    st.write(f"Developed by {CREATOR_NAME}")
    
    tab_l, tab_s = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab_l:
        u = st.text_input("Username", key="l_user")
        p = st.text_input("Password", type="password", key="l_pass")
        if st.button("Sign In", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True # Login State Saved!
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Wrong Details!")

    with tab_s:
        nu = st.text_input("New User", key="s_user")
        np = st.text_input("New Pass", type="password", key="s_pass")
        if st.button("Create Account", use_container_width=True):
            st.session_state.user_db[nu] = np
            st.success("Account Ready! Please Login.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= 5. MAIN APP (AFTER LOGIN) =================
with st.sidebar:
    st.title("🤖 New AI Menu")
    st.write(f"User: **{st.session_state.current_user}**")
    menu = st.radio("Navigation", ["Chat", "About Creator", "Feedback"])
    st.markdown("---")
    if st.button("Logout"): 
        st.session_state.logged_in = False # Logout will clear the save
        st.session_state.current_user = ""
        st.rerun()

if menu == "Chat":
    st.markdown('<div class="welcome-header">🤖 Welcome to New AI</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        role_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role_class}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    q = st.chat_input("Pucho kuch bhi...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        sys_msg = f"Name: New AI. Creator: {CREATOR_NAME}. Answer in same language."
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": q}])
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: st.error("AI connection error.")

elif menu == "About Creator":
    st.title("👤 About")
    st.info(f"Designed by **{CREATOR_NAME}**")
    
