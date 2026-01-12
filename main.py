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

# --- CSS: RED THEME & CHAT FOCUS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Footer for Terms */
    .legal-footer {
        position: fixed;
        bottom: 80px;
        left: 0;
        width: 100%;
        background: rgba(0,0,0,0.8);
        color: #888;
        font-size: 10px;
        text-align: center;
        padding: 5px;
        z-index: 100;
    }
    
    /* Red Button Styling */
    button[kind="secondary"] {
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

st.title("🚀 Pro AI")

# --- PERMANENT TERMS & ABOUT (TOP) ---
st.info("ℹ️ **About:** Pro AI text/images samajhta hai. **Privacy:** No data saved. **Terms:** Ise legal kaam ke liye hi use karein. AI galat jawab de sakta hai.")

# Chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- FIXED BOTTOM UI ---
st.divider()
c1, c2 = st.columns([2, 1])
with c1:
    # Single voice used internally (No dropdown)
    st.write("🎙️ Voice: Aarti (Active)")
with c2:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()

# Feedback (Small)
with st.expander("📬 Feedback"):
    f_text = st.text_input("Aapka feedback?")
    if st.button("Send"):
        st.toast("Shukriya!")

# Terms & Conditions (Fixed at bottom)
st.markdown('<div class="legal-footer">Terms: Legal use only. User is responsible for content. AI accuracy not guaranteed. No data storage.</div>', unsafe_allow_html=True)

# Input
uploaded_file = st.file_uploader("Image Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        sys_prompt = "Professional AI. Use 100% full words. No shortcuts like 'u' or 'k'."
        content = [{"type": "text", "text": f"{sys_prompt}\n\nUser: {prompt}"}]
        
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})

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
            
            # Fast Voice Generation (Aarti)
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f:
                st.session_state.last_audio = f.read()
            st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

# Audio Button
if st.session_state.last_audio:
    if st.button("🔈 Jawab Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
