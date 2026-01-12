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

st.set_page_config(page_title="Pro AI", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: POORI SCREEN KHAALI RAKHNE KE LIYE ---
st.markdown("""
    <style>
    /* Header, Footer aur Deploy button gayab */
    header, footer, .stDeployButton {visibility: hidden;}
    
    /* Sidebar (Menu) ki styling */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 2px solid #FF4B4B;
    }
    
    /* Main Chat Area ko clean rakhna */
    .block-container {padding-top: 2rem;}
    
    /* Red Button for Sidebar Toggle (Custom Look) */
    div[data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- MENU BUTTON (SIDEBAR KE ANDAR) ---
with st.sidebar:
    st.title("🔴 Pro AI Menu")
    st.divider()
    
    # Options inside Menu
    with st.expander("ℹ️ About & Model"):
        st.write("Pro AI Llama 3.3 model par chalta hai jo text aur images samajhta hai.")
    
    with st.expander("⚖️ Terms & Conditions"):
        st.write("1. Legal use only.\n2. No data storage.\n3. AI can be wrong.\n4. User is responsible.")
    
    with st.expander("🔒 Privacy Policy"):
        st.write("Hum aapka koi bhi personal data ya images save nahi karte.")
    
    st.divider()
    
    # Feedback inside Menu
    st.subheader("📬 Feedback")
    f_text = st.text_input("App kaisa laga?")
    if st.button("Submit"):
        st.toast("Shukriya!")
    
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()

# --- MAIN SCREEN (KHAALI AUR CLEAN) ---
st.title("🚀 Pro AI")

# Chat container
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input area (Bottom)
uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Yahan puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        sys_prompt = "Professional AI. Use full words only. No shortcuts."
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
            
            # Voice Generation (Aarti)
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f:
                st.session_state.last_audio = f.read()
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

# Audio button (Sirf jawab ke baad dikhega)
if st.session_state.last_audio:
    if st.button("🔈 Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
