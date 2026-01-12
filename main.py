import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os

# API Key check
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Pehle Streamlit Settings mein GROQ_API_KEY daalein!")

st.set_page_config(page_title="Pro AI", layout="wide")

# --- CSS: EK DAM CLEAN LOOK & RED BUTTONS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    header, footer, .stDeployButton {visibility: hidden;}
    
    /* Main Screen padding */
    .block-container {padding-top: 1rem; padding-bottom: 5rem;}

    /* Custom Menu Styling */
    .menu-card {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #FF4B4B;
        margin-bottom: 20px;
    }
    
    /* Red Button Styling */
    div.stButton > button {
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None
if "show_menu" not in st.session_state:
    st.session_state.show_menu = False

st.title("🚀 Pro AI")

# --- CUSTOM MENU BUTTON (POORI SCREEN KHAALI RAKHNE KE LIYE) ---
col_m1, col_m2 = st.columns([1, 4])
with col_m1:
    if st.button("☰ MENU"):
        st.session_state.show_menu = not st.session_state.show_menu

# Jab user Menu click karega tabhi ye dikhega
if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("🔴 App Options")
    
    # Options inside Menu
    st.markdown("**📖 About:** Llama 3.3 Voice & Vision AI.")
    st.markdown("**⚖️ Terms:** Legal use only. No data stored.")
    st.markdown("**🔒 Privacy:** We don't save your images/chats.")
    
    st.divider()
    # Feedback
    feedback = st.text_input("📬 Feedback dein:", placeholder="App kaisa laga?")
    if st.button("Send Feedback"):
        st.toast("Shukriya!")
        
    st.divider()
    # Clear Chat
    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT AREA ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- INPUT AREA (STICKY AT BOTTOM) ---
uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Yahan puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        sys_prompt = "Professional AI. Use 100% full words. No shortcuts."
        content = [{"type": "text", "text": f"{sys_prompt}\n\nUser: {prompt}"}]
        
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})

        with st.chat_message("assistant"):
            full_res = ""
            res_box = st.empty()
            comp = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": content}], stream=True)
            for chunk in comp:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            # Voice Generation
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f:
                st.session_state.last_audio = f.read()
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

# Audio button
if st.session_state.last_audio:
    if st.button("🔈 Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
