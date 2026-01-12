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

# --- CSS: MENU POSITION & LEGAL STYLING ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    .block-container {padding-bottom: 100px;}

    /* Menu Button ko 1cm (approx 40px) upar shift kiya */
    div.stButton > button:first-child {
        margin-top: -40px !important; 
    }

    /* Plus Icon Alignment */
    div[data-testid="stChatInput"] {
        margin-left: 50px !important;
    }
    
    .plus-icon-container {
        position: fixed;
        bottom: 32px;
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
    }

    div[data-testid="stFileUploader"] {
        position: fixed;
        bottom: 32px;
        left: 15px;
        width: 40px;
        height: 40px;
        opacity: 0;
        z-index: 1001;
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

# --- HEADER & UPDATED MENU ---
st.title("🚀 Pro AI")
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("🔴 Control Panel & Legal")
    
    # About Section
    st.markdown("### 📖 About")
    st.write("Pro AI ek advanced vision assistant hai jo Llama 3.3 model ka use karta hai.")

    # Privacy Policy
    st.markdown("### 🔒 Privacy Policy")
    st.write("- Hum aapka koi bhi data ya images save nahi karte.\n- Chats sirf aapke session tak hi rehte hain.")

    # Terms & Conditions
    st.markdown("### ⚖️ Terms & Conditions")
    st.write("1. Ise sirf legal purposes ke liye use karein.\n2. AI ke jawab hamesha 100% sahi nahi ho sakte.\n3. User apne content ke liye khud zimmedar hai.")

    st.divider()
    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT AREA ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- PLUS ICON & UPLOADER ---
st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    st.toast("📷 Photo Attach Ho Gayi!")

# --- CHAT INPUT ---
if prompt := st.chat_input("Yahan puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    try:
        content = [{"type": "text", "text": f"System: Use full words only. User: {prompt}"}]
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
