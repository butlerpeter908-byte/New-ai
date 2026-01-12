import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing!")

st.set_page_config(page_title="Pro AI", layout="wide")

# --- CUSTOM CSS: PLUS ICON & CLEAN INPUT ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    /* Plus Icon Styling */
    .upload-btn-wrapper {
        position: relative;
        overflow: hidden;
        display: inline-block;
        cursor: pointer;
    }
    
    /* Chat Input ke paas Plus button ko align karna */
    div[data-testid="stChatInput"] {
        padding-left: 45px;
    }
    
    .plus-icon {
        position: absolute;
        bottom: 25px;
        left: 10px;
        background-color: #FF4B4B;
        color: white;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        z-index: 99;
        cursor: pointer;
        border: 2px solid white;
    }

    /* Bada Browse Box Hatan ke liye */
    div[data-testid="stFileUploader"] {
        position: absolute;
        opacity: 0;
        z-index: 100;
        width: 40px;
        height: 40px;
        left: 10px;
        bottom: 25px;
    }
    
    .menu-card {
        background-color: #121212;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #FF4B4B;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False

# --- HEADER & MENU ---
st.title("🚀 Pro AI")
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("🔴 Control Panel")
    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    st.markdown('**Privacy:** No data saved. **Terms:** Legal use only.')
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT AREA ---
chat_placeholder = st.container()
with chat_placeholder:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

# --- PLUS ICON & FILE UPLOADER (HIDDEN) ---
# Ye trick hai: Plus icon ke upar file uploader ko transparent karke bitha diya hai
st.markdown('<div class="plus-icon">+</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    st.toast(f"File selected: {uploaded_file.name}")

# --- CHAT INPUT ---
if prompt := st.chat_input("Yahan puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_placeholder:
        with st.chat_message("user"): st.markdown(prompt)

    try:
        content = [{"type": "text", "text": f"System: Use full words. User: {prompt}"}]
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            with chat_placeholder:
                st.image(uploaded_file, width=150)

        with chat_placeholder:
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
                
                # Audio
                tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
                tts.save("voice.mp3")
                with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
                st.rerun()
    except Exception as e: st.error(f"Error: {e}")

# Audio Button
if st.session_state.last_audio:
    if st.button("🔈 Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
