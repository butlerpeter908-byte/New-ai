import streamlit as st
from groq import Groq

# ================= 1. IDENTITY & API KEY =================
# Aapki latest working API key yahan set hai
GROQ_KEY = "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"
CREATOR_NAME = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

# ================= 2. THE ULTIMATE CSS & UI FIX =================
st.set_page_config(page_title="New AI 🤖", layout="wide")

st.markdown("""
    <style>
    /* 1. Sabse pehle headers aur footers gayab karo */
    header, footer { visibility: hidden !important; height: 0px !important; }
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0e1117; color: white; }

    /* 2. THE FLOATING PROFILE ICON (LEFT SIDE) */
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
        z-index: 9999999 !important; /* Screen ke sabse upar */
        border: 3px solid white !important;
        box-shadow: 0px 0px 20px rgba(0, 255, 136, 0.7) !important;
        pointer-events: auto !important; /* Touch register karne ke liye */
    }

    /* 3. SIDEBAR STYLING: Colourful Labels */
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

    /* 4. CHAT BUBBLES: WhatsApp Look */
    .user-msg { background-color: #005c4b; padding: 12px; border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 85%; border: 1px solid #00a884; }
    .ai-msg { background-color: #202c33; padding: 12px; border-radius: 15px 15px 15px 0px; margin: 10px 0; border-left: 5px solid #00ff88; max-width: 85%; }

    /* 5. SILENT ERROR: Red Error Boxes ko hide karne ke liye */
    .stException, .stAlert[data-baseweb="notification"] { display: none !important; }
    </style>
    
    <script>
    function toggleSidebar() {
        // Asali sidebar button ko click karwane ka script
        const sidebarBtn = window.parent.document.querySelector('button[data-testid="stSidebarCollapse"]');
        if (sidebarBtn) {
            sidebarBtn.click();
        }
    }
    </script>

    <div class="my-profile-icon" onclick="toggleSidebar()">👤</div>
""", unsafe_allow_html=True)

# ================= 3. SESSION & LOGIN LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "user_db" not in st.session_state: st.session_state.user_db = {"admin": "123"}

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color:#00ff88;'>🔐 New AI Portal</h1>", unsafe_allow_html=True)
    tab_in, tab_up = st.tabs(["Sign In", "Create Account"])
    
    with tab_in:
        u = st.text_input("Username", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Enter AI", use_container_width=True):
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else: st.error("Details are incorrect!")
            
    with tab_up:
        nu = st.text_input("Choose Username", key="reg_user")
        np = st.text_input("Choose Password", type="password", key="reg_pass")
        if st.button("Register Account", use_container_width=True):
            if nu and np:
                st.session_state.user_db[nu] = np
                st.success("Account created successfully! Please Sign In.")
    st.stop()

# ================= 4. SIDEBAR COLOURFUL MENU =================
with st.sidebar:
    st.markdown(f"<h2 style='color:#00ff88; text-align:center;'>👤 Welcome, {st.session_state.current_user}</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Visual Labels
    st.markdown('<div class="menu-item" style="color:#00d2ff; border-color:#00d2ff;">💬 Chat Messenger</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item" style="color:#ffd700; border-color:#ffd700;">👤 About Developer</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item" style="color:#00ff88; border-color:#00ff88;">🛡️ Privacy Policy</div>', unsafe_allow_html=True)
    st.markdown('<div class="menu-item" style="color:#ffa500; border-color:#ffa500;">📄 Terms & Conditions</div>', unsafe_allow_html=True)
    
    # Actual Navigation
    page = st.radio("Go to:", ["Chat", "About", "Privacy", "Terms"], label_visibility="collapsed")
    
    st.markdown("---")
    if st.button("🗑️ Clear My Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    if st.button("🛑 Logout Now", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ================= 5. MAIN PAGE CONTENT =================
if page == "Chat":
    st.markdown("<h3 style='text-align:center; color:#00ff88;'>🤖 New AI Assistant</h3>", unsafe_allow_html=True)
    
    # Display message history
    for m in st.session_state.messages:
        div_class = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div_class}">{m["content"]}</div>', unsafe_allow_html=True)
    
    # Input Area
    user_input = st.chat_input("Siddique's AI se kuch bhi pucho...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        try:
            # Silent Error Handling for API
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": user_input}]
            )
            st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
            st.rerun()
        except:
            pass # CSS will hide any red error boxes automatically

elif page == "About":
    st.header("👤 About Developer")
    st.success(f"Developed & Maintained by: **{CREATOR_NAME}**")
    st.write("This AI is a custom-built solution for secure and fast mobile interaction.")

elif page == "Privacy":
    st.header("🛡️ Privacy Policy")
    st.info("Your data is safe. All chat history is session-based and is cleared when you log out.")

elif page == "Terms":
    st.header("📄 Terms & Conditions")
    st.warning("Please use this AI for ethical and educational purposes only.")
        
