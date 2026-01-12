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

# --- CSS: SIRF HEADER AUR WATERMARK HATANE KE LIYE (Sidebar ko chhod kar) ---
st.markdown("""
    <style>
    /* Sirf upar ka header aur footer hatane ke liye */
    header[data-testid="stHeader"] {display: none;}
    footer {display: none;}
    
    /* Watermark aur Deploy button hatane ke liye */
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Chat box watermark aur extra space fix */
    div[data-testid="stChatInput"] label {display: none;}
    
    /* Sidebar ko properly dikhane ke liye styling */
    section[data-testid="stSidebar"] {
        background-color: #111;
        border-right: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Pro AI: Voice + Vision")

# --- SIDEBAR (Ab ye dikhai dega) ---
with st.sidebar:
    st.title("⚙️ Settings")
    voice_type = st.selectbox("Awaz Chunein:", ["Aarti (Female)", "Akash (Male)"])
    tld_choice = 'com' if voice_type == "Aarti (Female)" else 'co.in'
    st.info("Yahan se aap voice change kar sakte hain.")

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# Chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input Area
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Mujhse baat karein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # No Abbreviations instruction
        instruction = "Respond naturally and fully. IMPORTANT: Do not use shortcuts like 'u', 'r', 'k'. Use full words."
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
            
            # Audio generation
            tts = gTTS(text=full_res, lang='hi', tld=tld_choice)
            tts.save("temp.mp3")
            with open("temp.mp3", "rb") as f:
                st.session_state.last_audio = f.read()

    except Exception as e:
        st.error(f"Error: {e}")

# Audio Button (Fix)
if st.session_state.last_audio:
    if st.button("🔈 Suniye (Listen)"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
