import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import requests
from datetime import datetime
from streamlit_mic_recorder import mic_recorder # Naya library

# API Key check
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing!")

st.set_page_config(page_title="Pro AI", layout="wide")

# --- CSS: MIC & PLUS ICON ALIGNMENT ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px;}

    /* Menu Button */
    div.stButton > button:first-child { 
        margin-top: -40px !important; 
        background-color: #FF4B4B !important;
        color: white !important;
    }

    /* Input box ke liye jagah */
    div[data-testid="stChatInput"] { margin-left: 100px !important; }
    
    /* Plus Icon Position */
    .plus-icon-container {
        position: fixed; bottom: 32px; left: 15px;
        background-color: #FF4B4B; color: white;
        border-radius: 50%; width: 40px; height: 40px;
        display: flex; align-items: center; justify-content: center;
        font-size: 25px; font-weight: bold; z-index: 1000;
        border: 2px solid white;
    }

    /* Mic Button Position (Plus ke thik baaju mein) */
    .mic-container {
        position: fixed; bottom: 32px; left: 65px;
        z-index: 1000;
    }

    div[data-testid="stFileUploader"] {
        position: fixed; bottom: 32px; left: 15px;
        width: 40px; height: 40px; opacity: 0; z-index: 1001;
        cursor: pointer;
    }
    
    .menu-card {
        background-color: #121212; padding: 20px;
        border-radius: 15px; border: 1px solid #FF4B4B;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False

st.title("🚀 Pro AI")

# --- MENU SECTION ---
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.markdown("### 📖 Pro AI Assistant")
    st.write("Voice, Image, aur Text support ke saath. Live Date/Time enabled.")
    st.divider()
    # Feedback GitHub wala logic yahan rahega...
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT AREA ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- MIC & PLUS ICON UI ---
st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

# MIC RECORDER (Whisper integration)
voice_prompt = ""
with st.container():
    st.markdown('<div class="mic-container">', unsafe_allow_html=True)
    audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')
    st.markdown('</div>', unsafe_allow_html=True)

if audio:
    # Voice ko text mein badalna (Groq Whisper)
    with st.spinner("Sun raha hoon..."):
        try:
            # Audio bytes ko temporary file mein save karna
            with open("temp_audio.wav", "wb") as f:
                f.write(audio['bytes'])
            
            with open("temp_audio.wav", "rb") as f:
                transcription = client.audio.transcriptions.create(
                    file=("temp_audio.wav", f.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
            voice_prompt = transcription
        except Exception as e:
            st.error(f"Voice Error: {e}")

# --- AI PROCESSING ---
# User ya toh type kare (prompt) ya bol kar (voice_prompt)
final_input = voice_prompt if voice_prompt else st.chat_input("Yahan puchiye...")

if final_input:
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%d/%m/%Y")

    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"): st.markdown(final_input)

    try:
        sys_info = f"Current Time: {current_time}. Current Date: {current_date}."
        instruction = "Professional AI. Use NUMERIC format for Time/Date. Respond in Hindi/English mix as requested."
        content = [{"type": "text", "text": f"{sys_info}\n{instruction}\nUser: {final_input}"}]
        
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
            
            # Voice response
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state.last_audio:
    if st.button("🔈 Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
        
