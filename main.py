import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & CREDENTIALS =================
GROQ_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. CLEAN & MINIMAL CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown("""
    <style>
    /* Sabse pehle default UI ko saaf kiya */
    header, footer {visibility: hidden !important;}
    .block-container { padding-top: 2rem !important; }
    
    /* BACKGROUND */
    .stApp { background-color: #0e1117; color: white; }

    /* CIRCULAR PROFILE ICON (Asali Sidebar Button ko Modify kiya) */
    button[data-testid="stSidebarCollapse"] {
        background-color: #00ff88 !important;
        color: black !important;
        border-radius: 50% !important;
        position: fixed !important;
        top: 15px !important;
        right: 15px !important;
        width: 50px !important;
        height: 50px !important;
        z-index: 999999 !important;
        border: 2px solid white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Profile Emoji inside Circle */
    button[data-testid="stSidebarCollapse"]::after {
        content: "👤";
        font-size: 22px;
    }
    button[data-testid="stSidebarCollapse"] svg {
        display: none !important;
    }

    /* Simple Chat Bubbles */
    .chat-box { margin-bottom: 10px; padding: 10px; border-radius: 10px; max-width: 80%; }
    .user-msg { background-color: #005c4b; margin-left: auto; text-align: right; }
    .ai-msg { background-color: #202c33; border-left: 4px solid #00ff88; }
    </style>
    """, unsafe_allow_html=True)

# ================= 3. PERSISTENT LOGIN LOGIC =================
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []

# --- LOGIN / SIGN UP ---
if not st.session_state.logged_in:
    st.title("🔐 New AI Login")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u = st.text_input("User", key="l_u")
        p = st.text_input("Pass", type="password", key="l_p")
        if st.button("Sign In"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
            else: st.error("Wrong details")
    with tab2:
        nu = st.text_input("New User", key="s_u")
        np = st.text_input("New Pass", type="password", key="s_p")
        if st.button("Create"):
            st.session_state.user_db[nu] = np; st.success("Created!")
    st.stop()

# ================= 4. PROFILE SIDEBAR MENU =================
with st.sidebar:
    st.header(f"👤 {st.session_state.current_user}")
    st.markdown("---")
    page = st.selectbox("Menu", ["Chat", "About Creator", "Feedback", "Privacy", "Terms"])
    st.markdown("---")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []; st.rerun()
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ================= 5. MAIN CONTENT =================
if page == "Chat":
    st.subheader("🤖 AI Messenger")
    for m in st.session_state.messages:
        div_class = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="chat-box {div_class}">{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Type here...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
        st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
        st.rerun()

elif page == "About Creator":
    st.header("👤 About")
    st.info(f"Created by: **{CREATOR_NAME}**")

elif page == "Privacy":
    st.header("🛡️ Privacy")
    st.write("Your data is temporary and secure.")

elif page == "Terms":
    st.header("📄 Terms")
    st.write("Use this AI ethically.")

elif page == "Feedback":
    fb = st.text_area("Feedback:")
    if st.button("Send"):
        st.success("Feedback recorded!")
        
