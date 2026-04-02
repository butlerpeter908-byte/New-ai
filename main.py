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

# ================= 2. CLEAN UI & JAVASCRIPT CLICKER =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown("""
    <style>
    /* Sabse pehle headers aur extra space hatao */
    header, footer {visibility: hidden !important;}
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0e1117; color: white; }
    
    /* CUSTOM LEFT PROFILE ICON (CLICKABLE) */
    .custom-profile-trigger {
        position: fixed;
        top: 15px;
        left: 15px;
        background-color: #00ff88;
        color: black;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        cursor: pointer;
        z-index: 999999;
        border: 2px solid white;
        box-shadow: 0px 0px 15px rgba(0, 255, 136, 0.5);
    }

    /* WhatsApp Style Bubbles */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 4px solid #00ff88; max-width: 80%; }
    </style>
    
    <script>
    function openSidebar() {
        const btn = window.parent.document.querySelector('button[data-testid="stSidebarCollapse"]');
        if (btn) {
            btn.click();
        } else {
            alert("Please swipe from left to right if button is hidden");
        }
    }
    </script>

    <div class="custom-profile-trigger" onclick="openSidebar()">👤</div>
    """, unsafe_allow_html=True)

# ================= 3. PERSISTENT LOGIN (NO REFRESH LOGOUT) =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🔐 New AI Login</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Galat hai bhai!")
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            if nu and np:
                st.session_state.user_db[nu] = np
                st.success("Account Ban Gaya!")
    st.stop()

# ================= 4. SIDEBAR MENU =================
with st.sidebar:
    st.title(f"👤 {st.session_state.current_user}")
    st.markdown("---")
    choice = st.radio("Settings", ["💬 Chat", "👤 About Creator", "📩 Feedback", "🛡️ Privacy", "📄 Terms"])
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ================= 5. MAIN CHAT CONTENT =================
if choice == "💬 Chat":
    st.markdown(f"<p style='text-align:center;'>Logged in as {st.session_state.current_user}</p>", unsafe_allow_html=True)
    
    # Message Display
    for m in st.session_state.messages:
        div_class = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div_class}">{m["content"]}</div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Siddique's AI se kuch pucho...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
            st.rerun()
        except:
            st.error("API Key ka lafda hai shayad!")

elif choice == "👤 About Creator":
    st.info(f"Developed with ❤️ by **{CREATOR_NAME}**")

elif choice == "🛡️ Privacy":
    st.write("Professional English: Your data is 100% temporary and secure.")

elif choice == "📄 Terms":
    st.write("Professional English: Use this AI for ethical purposes only.")

elif choice == "📩 Feedback":
    f_text = st.text_area("Experience kaisa raha?")
    if st.button("Submit"):
        st.success("Siddique ko feedback bhej diya gaya hai! ✅")
                
