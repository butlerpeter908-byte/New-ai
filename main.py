import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & API KEY =================
GROQ_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. CLEAN CSS & UI FIX =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown("""
    <style>
    header, footer { visibility: hidden !important; height: 0px !important; }
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0e1117; color: white; }

    /* FLOATING PROFILE ICON (LEFT SIDE) */
    .my-profile-icon {
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        background-color: #00ff88 !important;
        color: black !important;
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 26px !important;
        cursor: pointer !important;
        z-index: 9999999 !important;
        border: 3px solid white !important;
        box-shadow: 0px 0px 20px rgba(0, 255, 136, 0.7) !important;
        pointer-events: auto !important;
    }

    /* SideBar Styling */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 2px solid #00ff88 !important;
    }
    
    .menu-item {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-weight: bold;
        font-size: 18px;
        border-left: 5px solid;
        display: block;
    }

    /* Chat Bubbles */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 85%; border: 1px solid #00a884; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 85%; }

    /* Hide Red Error Boxes */
    .stException, .stAlert[data-baseweb="notification"] { display: none !important; }
    </style>
    
    <script>
    function toggleSidebar() {
        const sidebarBtn = window.parent.document.querySelector('button[data-testid="stSidebarCollapse"]');
        if (sidebarBtn) { sidebarBtn.click(); }
    }
    </script>

    <div class="my-profile-icon" onclick="toggleSidebar()">👤</div>
""", unsafe_allow_html=True)

# ================= 3. SESSION & LOGIN =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color:#00ff88;'>🔐 New AI Portal</h1>", unsafe_allow_html=True)
    u = st.text_input("Username", key="login_u")
    p = st.text_input("Password", type="password", key="login_p")
    if st.button("Enter AI", use_container_width=True):
        if u in st.session_state.user_db and st.session_state.user_db[u] == p:
            st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
        else: st.error("Wrong details!")
    st.stop()

# ================= 4. MINIMAL SIDEBAR =================
with st.sidebar:
    st.markdown(f"<h2 style='color:#00ff88; text-align:center;'>👤 {st.session_state.current_user}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown('<div class="menu-item" style="color:#00d2ff; border-color:#00d2ff;">💬 Messenger</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item" style="color:#ff4b4b; border-color:#ff4b4b;">📩 Feedback</div>', unsafe_allow_html=True)
    
    page = st.radio("Go to:", ["Chat", "Feedback"], label_visibility="collapsed")
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []; st.rerun()
    if st.button("🛑 Logout", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ================= 5. MAIN CONTENT =================
if page == "Chat":
    st.markdown("<h3 style='text-align:center; color:#00ff88;'>🤖 New AI Assistant</h3>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        div_class = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div_class}">{m["content"]}</div>', unsafe_allow_html=True)
    
    q = st.chat_input("Ask Siddique's AI...")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": q}])
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: pass

elif page == "Feedback":
    st.header("📩 Send Feedback")
    st.write("Aapka experience kaisa raha? Siddique ko direct message bhein.")
    feedback_text = st.text_area("Write your message here...", height=150)
    
    if st.button("Submit Feedback", use_container_width=True):
        if feedback_text:
            try:
                msg = MIMEText(f"User: {st.session_state.current_user}\nFeedback: {feedback_text}")
                msg['Subject'] = 'New AI User Feedback'
                msg['From'] = MY_GMAIL
                msg['To'] = MY_GMAIL
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(MY_GMAIL, APP_PASS)
                    server.send_message(msg)
                st.success("Feedback sent to Siddique! ✅")
            except:
                st.error("Email sending failed. Please check credentials.")
        else:
            st.warning("Kuch toh likho bhai!")
            
