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

# --- ADVANCED CSS: APP-LIKE FEEL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"]  {font-family: 'Inter', sans-serif;}
    
    [data-testid="stSidebar"] {display: none;}
    header, footer, .stDeployButton {visibility: hidden;}
    
    /* Menu Card Styling */
    .menu-card {
        background-color: #121212;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #FF4B4B;
        margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(255, 75, 75, 0.2);
    }
    
    /* Custom Red Buttons */
    div.stButton > button {
        background-color: #FF4B4B !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {transform: scale(1.02);}
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False

# --- HEADER & MENU TOGGLE ---
st.title("🚀 Pro AI")
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("🔴 Control Panel")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("🤖 **Model:** Llama 3.3")
    with col_b:
        if st.button("📤 Share Link"):
            st.code("https://new-ai-oe4grctv9yqqdnep6d9s2s.streamlit.app/")
            st.toast("Link copy karein aur share karein!")

    tab1, tab2, tab3 = st.tabs(["About", "Legal", "Feedback"])
    with tab1:
        st.write("Pro AI ek advanced vision assistant hai jo photo dekh kar uska jawab de sakta hai.")
    with tab2:
        st.write("Privacy: No data storage. Terms: Legal use only.")
    with tab3:
        f_text = st.text_input("Aapka Feedback:")
        if st.button("Submit Feedback"): st.toast("Shukriya!")

    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT & INPUT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

uploaded_file = st.file_uploader("Upload", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Yahan puchiye..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    try:
        content = [{"type": "text", "text": f"System: Use full words only. User: {prompt}"}]
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
            
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state.last_audio:
    if st.button("🔈 Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
