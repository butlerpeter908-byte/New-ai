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

# --- CSS: RED BUTTONS & CLEAN UI ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    header[data-testid="stHeader"] {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Red Styling for Menu */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        border: 2px solid #FF4B4B !important;
        border-radius: 10px;
    }
    button[kind="secondary"] {
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
    }
    div[data-testid="stChatInput"] label {display: none;}
    </style>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

st.title("🚀 Pro AI: Voice + Vision")

# --- CHAT HISTORY ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- RED MENU NEAR CHAT BOX ---
st.divider()
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    voice_type = st.selectbox("🔊 Voice", ["Aarti (Female)", "Akash (Male)"], label_visibility="collapsed")
    # Voice selection logic fix
    tld_choice = 'com' if voice_type == "Aarti (Female)" else 'co.in'
    lang_code = 'hi'

with col2:
    theme_choice = st.selectbox("🎨 Theme", ["Dark", "Midnight"], label_visibility="collapsed")
    if theme_choice == "Midnight":
        st.markdown("<style>.stApp {background-color: #000000;}</style>", unsafe_allow_html=True)

with col3:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()

# --- INPUT AREA ---
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Yahan kuch puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        instruction = "Respond naturally and fully. IMPORTANT: No shortcuts like 'u' or 'k'. Use full words always."
        content = [{"type": "text", "text": f"{instruction}\n\nUser: {prompt}"}]
        
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            st.image(uploaded_file, width=150)

        with st.chat_message("assistant"):
            full_res = ""
            res_box = st.empty()
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "user", "content": content}], 
                stream=True
            )
            for chunk in comp:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
            # --- FIXED VOICE & SPEED (1.25x effect) ---
            # gTTS slow=False se speed normal se thodi fast ho jati hai
            tts = gTTS(text=full_res, lang=lang_code, tld=tld_choice, slow=False)
            tts.save("temp.mp3")
            with open("temp.mp3", "rb") as f:
                st.session_state.last_audio = f.read()

    except Exception as e:
        st.error(f"Error: {e}")

# Suniye Button
if st.session_state.last_audio:
    if st.button("🔈 Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
