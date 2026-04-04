import streamlit as st
from groq import Groq

# ================= 1. IDENTITY & API KEY =================
GROQ_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

# ================= 2. FORCE ENABLE SIDEBAR & CSS =================
# initial_sidebar_state="expanded" se ye pehli baar mein hi khula rahega
st.set_page_config(
    page_title="New AI 🤖", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

st.markdown("""
    <style>
    /* Sabse pehle headers aur extra space hatao */
    header, footer {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0e1117; color: white; }
    
    /* STYLING THE NATIVE BUTTON (Ab ye left side mein bada aur green dikhega) */
    button[data-testid="stSidebarCollapse"] {
        background-color: #00ff88 !important;
        color: black !important;
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999 !important;
        border: 2px solid white !important;
        box-shadow: 0px 0px 15px #00ff88 !important;
    }
    
    /* Sidebar ke andar ka text colourful aur bada */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 2px solid #00ff88;
    }
    
    .sidebar-label {
        font-weight: bold;
        font-size: 20px;
        margin: 10px 0;
    }

    /* Chat Bubbles */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; max-width: 85%; margin-left: auto; border: 1px solid #00a884; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 85%; }
    </style>
    """, unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color:#00ff88;'>🔐 New AI Portal</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Sign In", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
            else: st.error("Login Failed")
    with t2:
        nu = st.text_input("New User", key="reg_u")
        np = st.text_input("New Pass", type="password", key="reg_p")
        if st.button("Create Account", use_container_width=True):
            st.session_state.user_db[nu] = np; st.success("Ready!")
    st.stop()

# ================= 4. COLOURFUL SIDEBAR =================
with st.sidebar:
    st.markdown(f"<h2 style='color:#00ff88;'>👤 {st.session_state.current_user}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<div class='sidebar-label' style='color:#00d2ff;'>💬 Chat</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label' style='color:#ffd700;'>👤 About</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label' style='color:#00ff88;'>🛡️ Privacy</div>", unsafe_allow_html=True)
    
    choice = st.radio("Menu", ["Chat", "About", "Privacy"], label_visibility="collapsed")
    
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []; st.rerun()
    if st.button("🛑 Logout", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ================= 5. MAIN CONTENT =================
if choice == "Chat":
    st.markdown("<h3 style='text-align:center; color:#00ff88;'>🤖 Siddique's AI</h3>", unsafe_allow_html=True)
    
    for m in st.session_state.messages:
        div_class = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div_class}">{m["content"]}</div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Ask me anything...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            # Silent Error Handling: Agar API response ke baad phat-ti hai toh error hide rahega
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except:
            # No red box anymore
            st.info("Thinking...") 

elif choice == "About":
    st.success(f"Developed by: **{CREATOR_NAME}**")

elif choice == "Privacy":
    st.info("Your data is secure and session-based.")
    
