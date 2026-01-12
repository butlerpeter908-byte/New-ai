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

# --- CSS: MOBILE OPTIMIZATION & FIXED CHAT BOX ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    header[data-testid="stHeader"] {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Info box ko thoda chhota kiya */
    .info-box {
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 8px;
        border-left: 4px solid #FF4B4B;
        font-size: 14px;
        margin-bottom: 10px;
    }

    /* Red Styling for Selectbox */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        border: 1px solid #FF4B4B !important;
        height: 35px;
    }

    /* Fixed Bottom Container for Chat and Menu */
    .main .block-container {
        padding-bottom: 200px; /* Space for sticky footer */
    }
    
    /* Clear Button styling */
    button[kind="secondary"] {
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 8px;
        height: 35px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

st.title("🚀 Pro AI")

# --- TOP SECTION (About & Feedback) ---
with st.expander("📖 About, Privacy & Feedback", expanded=False):
    st.markdown("""
    <div class="info-box">
        <b>🔒 Privacy:</b> No data saved. <b>⚖️ Terms:</b> Legal use only.<br>
        <b>🚀 Model:</b> Llama 3.3 (Vision + Voice)
    </div>
    """, unsafe_allow_html=True)
    
    feedback = st.text_input("📬 Quick Feedback")
    if st.button("Submit Feedback"):
        st.toast("Shukriya!")

# --- CHAT HISTORY AREA ---
chat_container = st.container()
with chat_container:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# --- STICKY MENU & INPUT (BOTTOM) ---
st.divider()
col1, col2, col3 = st.columns([1,1,1])

with col1:
    v_type = st.selectbox("Voice", ["Aarti", "Akash"], label_visibility="collapsed", key="v_f")
with col2:
    t_type = st.selectbox("Theme", ["Dark", "Midnight"], label_visibility="collapsed", key="t_f")
    if t_type == "Midnight":
        st.markdown("<style>.stApp {background-color: #000000;}</style>", unsafe_allow_html=True)
with col3:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()

# Image Upload (Compact)
uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

# Chat Input - Ye hamesha bottom par stick rahega
if prompt := st.chat_input("Puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    try:
        sys_prompt = "Professional AI. Full words only. No shortcuts like 'u'."
        content = [{"type": "text", "text": f"{sys_prompt}\n\nUser: {prompt}"}]
        
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})

        with chat_container:
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
                tld = 'com.au' if v_type == "Aarti" else 'co.in'
                tts = gTTS(text=full_res, lang='hi', tld=tld, slow=False)
                tts.save("voice.mp3")
                with open("voice.mp3", "rb") as f:
                    st.session_state.last_audio = f.read()
                st.rerun() # Refresh to show audio button

    except Exception as e:
        st.error(f"Error: {e}")

# Audio Button
if st.session_state.last_audio:
    st.button("🔈 Suniye", on_click=lambda: st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True))
