import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os

# 1. Faltu Theme Code Hata diya (Default Streamlit theme use hogi jo stable hai)
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Pehle Streamlit Settings mein GROQ_API_KEY daalein!")

st.set_page_config(page_title="Pro AI", layout="wide")

# 3. Header Hide aur Watermark removal (Clean UI)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    .stDeployButton {display:none;}
    /* Chat input watermark fix */
    div[data-testid="stChatInput"] label {display: none;}
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Pro AI: Voice + Vision")

# Settings Sidebar
st.sidebar.title("Settings")
voice_type = st.sidebar.selectbox("Awaz Chunein:", ["Aarti (Female)", "Akash (Male)"])
tld_choice = 'com' if voice_type == "Aarti (Female)" else 'co.in'

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# Chat history dikhana
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input area
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Mujhse baat karein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # 4. No Abbreviations (Sakht instruction taki AI 'u', 'r', 'k' use na kare)
        instruction = "Respond naturally and fully in the user's language. IMPORTANT: Do not use any shortcuts, abbreviations, or SMS language. Write every word completely (e.g., use 'you' instead of 'u', 'okay' instead of 'k')."
        
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
            
            # 2. Audio Fix (Session state mein audio bytes save karna taki button kaam kare)
            tts = gTTS(text=full_res, lang='hi', tld=tld_choice)
            tts.save("temp.mp3")
            with open("temp.mp3", "rb") as f:
                st.session_state.last_audio = f.read()

    except Exception as e:
        st.error(f"Error: {e}")

# Speaker button display (Audio fix ka hissa)
if st.session_state.last_audio:
    if st.button("🔈 Suniye (Listen)"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
