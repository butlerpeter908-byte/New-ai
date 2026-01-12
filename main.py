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

st.set_page_config(page_title="Pro AI", layout="wide", initial_sidebar_state="expanded")

# --- CSS: UI ko clean aur professional banane ke liye ---
st.markdown("""
    <style>
    header[data-testid="stHeader"] {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# --- PERMANENT MENU (SIDEBAR) ---
with st.sidebar:
    st.title("📂 Main Menu")
    
    # 1. VOICE SETTINGS
    st.subheader("🔊 Voice Selection")
    voice_type = st.selectbox("Awaz Chunein:", ["Aarti (Female)", "Akash (Male)"], key="voice_sel")
    tld_choice = 'com' if voice_type == "Aarti (Female)" else 'co.in'
    
    st.divider()
    
    # 2. THEME SETTINGS
    st.subheader("🎨 Theme")
    theme_choice = st.radio("App Look:", ["Classic Dark", "Midnight Black"], key="theme_sel")
    if theme_choice == "Midnight Black":
        st.markdown("<style>.stApp {background-color: #000000;}</style>", unsafe_allow_html=True)
    
    st.divider()
    
    # 3. HISTORY
    st.subheader("📜 Chat History")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    
    st.info(f"Total Messages: {len(st.session_state.messages)}")

# --- MAIN CHAT AREA ---
st.title("🚀 Pro AI: Voice + Vision")

# Chat history display
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input area
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Yahan kuch likhiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        instruction = "Respond naturally and fully. DO NOT use abbreviations. Write complete words."
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
            
            # Audio Generation
            tts = gTTS(text=full_res, lang='hi', tld=tld_choice)
            tts.save("temp.mp3")
            with open("temp.mp3", "rb") as f:
                st.session_state.last_audio = f.read()

    except Exception as e:
        st.error(f"Error: {e}")

# Speaker button (Fix)
if st.session_state.last_audio:
    if st.button("🔈 Suniye (Listen)"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
