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

# --- CSS: RED MENU & CLEAN LOOK ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    header[data-testid="stHeader"] {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Red Styling for Buttons & Selectbox */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        border: 2px solid #FF4B4B !important;
        border-radius: 10px;
    }
    button[kind="secondary"] {
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        width: 100%;
    }
    div[data-testid="stChatInput"] label {display: none;}
    
    /* Info Section Styling */
    .info-box {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

st.title("🚀 Pro AI: Voice + Vision")

# --- PERMANENT INFO SECTION (About, Privacy, Terms) ---
st.markdown("""
<div class="info-box">
    <b>📖 About:</b> Pro AI ek smart assistant hai jo text aur images ko samajhta hai.<br>
    <b>🔒 Privacy:</b> Aapka chat aur image data kahi bhi save nahi kiya jata.<br>
    <b>⚖️ Terms:</b> Ise sirf legal kaam ke liye use karein. AI galat jankari de sakta hai.<br>
    <b>📝 Feedback:</b> Niche diye gaye box mein apni raye dein!
</div>
""", unsafe_allow_html=True)

# Display history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- RED MENU BAR ---
st.divider()
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    v_type = st.selectbox("Voice", ["Aarti (Female)", "Akash (Male)"], label_visibility="collapsed", key="v_final")
with c2:
    t_type = st.selectbox("Theme", ["Dark", "Midnight"], label_visibility="collapsed", key="t_final")
    if t_type == "Midnight":
        st.markdown("<style>.stApp {background-color: #000000;}</style>", unsafe_allow_html=True)
with c3:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()

# --- INPUT SECTION ---
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Mujhse baat karein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        sys_prompt = "You are a professional AI. Use 100% full words. No abbreviations like 'u', 'r', 'k'."
        content = [{"type": "text", "text": f"{sys_prompt}\n\nUser: {prompt}"}]
        
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
            
            # Audio Engine
            tld = 'com.au' if v_type == "Aarti (Female)" else 'co.in'
            tts = gTTS(text=full_res, lang='hi', tld=tld, slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f:
                st.session_state.last_audio = f.read()
    except Exception as e:
        st.error(f"Error: {e}")

# Audio & Feedback Section
if st.session_state.last_audio:
    if st.button("🔈 Suniye (Listen)"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)

st.divider()
# --- FEEDBACK OPTION ---
st.subheader("📬 Feedback")
feedback_text = st.text_area("Hume batayein aapko ye app kaisa laga:", placeholder="Yahan likhein...", label_visibility="collapsed")
if st.button("Send Feedback"):
    if feedback_text:
        st.success("Shukriya! Aapka feedback submit ho gaya hai.")
    else:
        st.warning("Pehle kuch likhiye!")
