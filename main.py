import streamlit as st
from groq import Groq
import requests
import base64

# ================= 1. IDENTITY & KEYS =================
GROQ_KEY = "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"
TAVILY_API_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. ALL-IN-ONE CSS (MOBILE MENU + GLASSY LOGIN) =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown(f"""
    <style>
    /* Hide Fork & Streamlit Default Header/Footer */
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* MOBILE MENU BUTTON (Visible & Green) */
    button[data-testid="stSidebarCollapse"] {{
        background-color: #00a884 !important;
        color: white !important;
        border-radius: 50% !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999 !important;
        display: block !important;
    }}

    /* Premium Glassy Background */
    .stApp {{
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    }}
    
    /* WhatsApp Chat Style */
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

    /* Login/Signup Box Styling */
    .auth-container {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 50px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= 3. SESSION STATE & SIDEBAR =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

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

# ================= 4. LOGIN & SIGN UP PAGE (FIXED) =================
if not st.session_state.logged_in:
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.title("🔐 Welcome to New AI")
    st.write(f"Developed by {CREATOR_NAME}")
    
    # Sign Up aur Login ke liye Tabs banaye hain
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        u = st.text_input("Username", key="login_username")
        p = st.text_input("Password", type="password", key="login_password")
        if st.button("Sign In", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else:
                st.error("Invalid Username or Password")
                
    with tab2:
        st.subheader("Create New Account")
        new_u = st.text_input("Choose Username", key="signup_username")
        new_p = st.text_input("Choose Password", type="password", key="signup_password")
        conf_p = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        if st.button("Create Account", use_container_width=True):
            if not new_u or not new_p:
                st.warning("Please fill all fields")
            elif new_p != conf_p:
                st.error("Passwords do not match!")
            elif new_u in st.session_state.user_db:
                st.error("Username already exists!")
            else:
                st.session_state.user_db[new_u] = new_p
                st.success("Account Created! Now go to Login tab.")
                
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================= 5. CHAT SYSTEM =================
if menu == "Chat":
    st.title(f"💬 Chatting as {st.session_state.current_user}")
    
    for m in st.session_state.messages:
        role = "user-bubble" if m["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{role}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Pucho kuch bhi...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        
        # News Search logic
        live_info = ""
        if any(x in q.lower() for x in ["news", "latest", "today", "score"]):
            try:
                r = requests.post("https://api.tavily.com/search", json={"api_key": TAVILY_API_KEY, "query": q})
                live_info = "\n".join([res['content'] for res in r.json().get('results', [])])
            except: live_info = ""

        sys_msg = f"Name: New AI. Creator: {CREATOR_NAME}. Natural behavior. Use same language as user. Data: {live_info}"
        
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": sys_msg}, {"role": "user", "content": q}]
        )
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif menu == "About Creator":
    st.header("👤 Creator Information")
    st.info(f"This AI is proudly developed by **{CREATOR_NAME}**.")
    
