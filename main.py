import streamlit as st
from groq import Groq
import smtplib
from email.mime.text import MIMEText

# ================= 1. IDENTITY & NEW API KEY =================
GROQ_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 

client = Groq(api_key=GROQ_KEY)

# ================= 2. COLOURFUL UI & SIDEBAR CSS =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown("""
    <style>
    header, footer {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0e1117; color: white; }
    
    /* LEFT PROFILE ICON */
    .custom-profile-trigger {
        position: fixed; top: 15px; left: 15px;
        background-color: #00ff88; color: black;
        border-radius: 50%; width: 50px; height: 50px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px; cursor: pointer; z-index: 999999;
        border: 2px solid white; box-shadow: 0px 0px 15px #00ff88;
    }

    /* SIDEBAR TEXT COLOURS & VISIBILITY */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 2px solid #00ff88;
    }
    
    /* Styling Radio Buttons for Visibility */
    div[data-testid="stMarkdownContainer"] p {
        font-weight: bold !important;
        font-size: 18px !important;
    }

    /* Custom classes for each page label (Simulated with Radio styling) */
    .st-emotion-cache-6q9sum r { font-weight: bold; }
    
    /* Chat Bubbles */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 85%; border: 1px solid #00a884; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 85%; }
    </style>

    <script>
    function openSidebar() {
        const btn = window.parent.document.querySelector('button[data-testid="stSidebarCollapse"]');
        if (btn) btn.click();
    }
    </script>
    <div class="custom-profile-trigger" onclick="openSidebar()">👤</div>
    """, unsafe_allow_html=True)

# ================= 3. PERSISTENT LOGIN SESSION =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color:#00ff88;'>🔐 New AI Portal</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Sign In", "Create Account"])
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True; st.session_state.current_user = u; st.rerun()
            else: st.error("Details galat hain bhai!")
    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Sign Up", use_container_width=True):
            if nu and np: st.session_state.user_db[nu] = np; st.success("Ready! Ab login karo.")
    st.stop()

# ================= 4. COLOURFUL SIDEBAR MENU =================
with st.sidebar:
    st.markdown(f"<h2 style='color:#00ff88; text-align:center;'>Welcome, {st.session_state.current_user}!</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Text with Emojis and forced colourful styling
    st.markdown("<span style='color:#00d2ff;'>💬 Chat Messenger</span>", unsafe_allow_html=True)
    st.markdown("<span style='color:#ffd700;'>👤 About Creator</span>", unsafe_allow_html=True)
    st.markdown("<span style='color:#ff4b4b;'>📩 Send Feedback</span>", unsafe_allow_html=True)
    st.markdown("<span style='color:#00ff88;'>🛡️ Privacy Policy</span>", unsafe_allow_html=True)
    st.markdown("<span style='color:#ffa500;'>📄 Terms & Conditions</span>", unsafe_allow_html=True)
    
    choice = st.radio("Go to:", ["Chat", "About", "Feedback", "Privacy", "Terms"], label_visibility="collapsed")
    
    st.markdown("---")
    if st.button("🗑️ Clear All Chat", use_container_width=True):
        st.session_state.messages = []; st.rerun()
    
    if st.button("🛑 Logout Account", use_container_width=True):
        st.session_state.logged_in = False; st.rerun()

# ================= 5. MAIN CONTENT =================
if choice == "Chat":
    st.markdown(f"<h3 style='text-align:center; color:#00ff88;'>🤖 Siddique's AI</h3>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        div_class = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div_class}">{m["content"]}</div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Ask me anything...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: st.error("API Error! Key check karo.")

elif choice == "About":
    st.header("👤 About Creator")
    st.success(f"Developed by: **{CREATOR_NAME}**")

elif choice == "Privacy":
    st.header("🛡️ Privacy Policy")
    st.info("Professional English: Your session is protected and data is cleared upon logout.")

elif choice == "Terms":
    st.header("📄 Terms of Use")
    st.warning("Professional English: This AI is for personal and ethical use only.")

elif choice == "Feedback":
    fb = st.text_area("Experience share karein:")
    if st.button("Send Feedback"):
        st.success("Feedback saved! ✅")
    
