import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os

# Secrets check
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Pehle Streamlit Settings mein GROQ_API_KEY daalein!")

# --- UI SETTINGS & THEMES ---
st.set_page_config(page_title="Pro AI", layout="wide")

# CSS: GitHub icon aur menu ko chhupane ke liye
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# Sidebar for Theme and Voice
st.sidebar.title("🎨 Customization")
theme_choice = st.sidebar.selectbox("Theme Chunein:", ["Default Dark", "Ocean Blue", "Soft Purple", "Midnight"])

# Theme Colors Setup
if theme_choice == "Ocean Blue":
    st.markdown("<style>body { background-color: #0E1117; color: #E0F2F1; } .stApp { background-image: linear-gradient(to right, #1a2a6c, #b21f1f, #fdbb2d); }</style>", unsafe_allow_html=True)
elif theme_choice == "Soft Purple":
    st.markdown("<style>.stApp { background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%); }</style>", unsafe_allow_html=True)
elif theme_choice == "Midnight":
    st.markdown("<style>.stApp { background-color: #000000; }</style>", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.title("🔊 Audio Settings")
voice_type = st.sidebar.selectbox("Awaz Chunein:", ["Aarti (Female)", "Akash (Male)"])
tld_choice = 'com' if voice_type == "Aarti (Female)" else 'co.in'

st.title("🚀 Pro AI: Voice + Vision")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat history dikhana
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- CHAT INPUT AUR UPLOAD ---
uploaded_file = st.file_uploader("Upload Image (Optional)", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Mujhse apni bhasha mein baat karein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        instruction = "Respond naturally and fully in the user's language. DO NOT use abbreviations/shortcuts. Use professional and clear words."
        content = [{"type": "text", "text": f"{instruction}\n\nUser: {prompt}"}]
        
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            st.image(uploaded_file, width=150)

        with st.chat_message("assistant"):
            res_box = st.empty()
            full_res = ""
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
            
            # --- AUDIO BUTTON ---
            if st.button("🔈 Suniye (Listen)"):
                with st.spinner("Awaz taiyaar ho rahi hai..."):
                    try:
                        if os.path.exists("response.mp3"):
                            os.remove("response.mp3")
                        tts = gTTS(text=full_res, lang='hi', tld=tld_choice)
                        tts.save("response.mp3")
                        st.audio("response.mp3", format="audio/mp3", autoplay=True)
                    except Exception as voice_err:
                        st.error("Audio error!")
            
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
    except Exception as e:
        st.error(f"Error: {e}")
