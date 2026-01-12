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

# --- CSS: PLUS ICON EXACT POSITIONING ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    /* Main container padding */
    .block-container {padding-bottom: 100px;}

    /* Chat Input ki width thodi kam ki taaki plus icon ki jagah bane */
    div[data-testid="stChatInput"] {
        margin-left: 50px !important;
    }
    
    /* Plus Icon Styling - Bilkul Input Bar ke Level Par */
    .plus-icon-container {
        position: fixed;
        bottom: 32px; /* Chat bar ke bilkul center mein align kiya */
        left: 15px;
        background-color: #FF4B4B;
        color: white;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        font-weight: bold;
        z-index: 1000;
        cursor: pointer;
        box-shadow: 0px 0px 10px rgba(255, 75, 75, 0.5);
    }

    /* Transparent File Uploader Over the Plus Icon */
    div[data-testid="stFileUploader"] {
        position: fixed;
        bottom: 32px;
        left: 15px;
        width: 40px;
        height: 40px;
        opacity: 0; /* Invisible but clickable */
        z-index: 1001;
        cursor: pointer;
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

# --- MENU SECTION ---
st.title("🚀 Pro AI")
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    st.markdown('**Privacy:** No data saved. **Terms:** Legal use only.')
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT AREA ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- THE PLUS ICON & HIDDEN UPLOADER ---
st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    st.sidebar.image(uploaded_file, caption="Selected Image", width=100) # Preview in hidden sidebar or toast
    st.toast("📷 Photo Attach Ho Gayi!")

# --- CHAT INPUT ---
if prompt := st.chat_input("Yahan puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    try:
        content = [{"type": "text", "text": f"System: Use full words. User: {prompt}"}]
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            st.image(uploaded_file, width=150)

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
            
            # Voice
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state.last_audio:
    if st.button("🔈 Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
