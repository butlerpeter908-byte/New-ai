import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz 
from streamlit_mic_recorder import mic_recorder

# API Key check
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API Key missing!")

st.set_page_config(page_title="Pro AI", layout="wide")

# --- CSS: UI FIXES ---
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px;}
    div.stButton > button:first-child { margin-top: -40px !important; background-color: #FF4B4B !important; color: white !important;}
    div[data-testid="stChatInput"] { margin-left: 100px !important; }
    .plus-icon-container { position: fixed; bottom: 32px; left: 15px; background-color: #FF4B4B; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-size: 25px; font-weight: bold; z-index: 1000; border: 2px solid white; }
    .mic-container { position: fixed; bottom: 32px; left: 65px; z-index: 1000; }
    div[data-testid="stFileUploader"] { position: fixed; bottom: 32px; left: 15px; width: 40px; height: 40px; opacity: 0; z-index: 1001; cursor: pointer; }
    .menu-card { background-color: #121212; padding: 25px; border-radius: 15px; border: 1px solid #FF4B4B; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "show_menu" not in st.session_state: st.session_state.show_menu = False
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None

st.title("🚀 Pro AI")

if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    
    # --- DETAILED ABOUT SECTION ---
    st.subheader("📖 About Pro AI")
    st.write("""
    Pro AI ek advanced artificial intelligence assistant hai jo cutting-edge Vision aur Voice technology par kaam karta hai. 
    Ye platform Llama 3.3 aur Whisper model ka upyog karke aapke text, images, aur voice commands ko smartly samajhta hai. 
    Hamara maksad user ko ek seamless assistant provide karna hai jo na sirf sawalo ke jawab de sake, balki images ko analyze karke unka varnan bhi kar sake. 
    Is app mein Indian users ke liye khas taur par IST time integration aur Hindi-English voice responses diye gaye hain. 
    Ye ek complete personal assistant hai jo aapke digital experience ko fast aur efficient banata hai.
    """)

    # --- DETAILED PRIVACY POLICY ---
    st.subheader("🔒 Privacy Policy")
    st.write("""
    Aapki privacy hamari sabse pehli priority hai aur hum is baare mein bilkul transparent hain. 
    Pro AI kisi bhi tarah ka user data, personal information, ya chat history ko apne servers par permanent save nahi karta hai. 
    Aap jo bhi images upload karte hain ya voice commands dete hain, wo sirf temporary session ke liye process kiye jaate hain. 
    Jaise hi aap chat clear karte hain ya page refresh karte hain, sara data system se turant remove ho jata hai. 
    Hum kisi bhi third-party ko aapka data nahi bechte aur ye platform puri tarah se encrypted aur secure environment mein chalta hai.
    """)

    # --- DETAILED TERMS & CONDITIONS ---
    st.subheader("⚖️ Terms & Conditions")
    st.write("""
    Is application ka upyog karte samay aapko kuch rules aur guidelines ka palan karna anivarya hai. 
    User ko is platform ka upyog sirf legal aur ethical purposes ke liye hi karna chahiye, kisi bhi illegal activity ke liye nahi. 
    AI dwara diye gaye jawab hamesha 100% accurate nahi ho sakte, isliye mahatvapoorn faislo ke liye in par puri tarah nirbhar na rahein. 
    App mein kisi bhi tarah ka abusive content ya harmful material upload karna sakht mana hai aur ye policy ka उल्लंघन mana jayega. 
    Hum bina kisi purv suchna ke platform mein badlav karne ya services ko modify karne ka adhikar rakhte hain.
    Ise use karke aap maan rahe hain ki aap in sabhi sharto se sehmat hain.
    """)

    st.divider()
    if st.button("🗑️ Clear All Chat"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- CHAT AREA ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# --- INPUT UI ---
st.markdown('<div class="plus-icon-container">+</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

voice_prompt = None
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='recorder')
st.markdown('</div>', unsafe_allow_html=True)

if audio_data:
    if st.session_state.last_audio_id != audio_data['id']:
        st.session_state.last_audio_id = audio_data['id']
        with st.spinner("Sun raha hoon..."):
            try:
                with open("temp.wav", "wb") as f: f.write(audio_data['bytes'])
                with open("temp.wav", "rb") as f:
                    transcription = client.audio.transcriptions.create(file=("temp.wav", f.read()), model="whisper-large-v3", response_format="text")
                voice_prompt = transcription
            except Exception as e: st.error(f"Mic Error: {e}")

user_input = voice_prompt if voice_prompt else st.chat_input("Yahan puchiye...")

if user_input:
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    cur_time, cur_date = now.strftime("%I:%M %p"), now.strftime("%d/%m/%Y")

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    try:
        sys_info = f"CURRENT_SYSTEM_TIME: {cur_time}, CURRENT_SYSTEM_DATE: {cur_date}."
        instruction = "Professional AI. Use numeric time ONLY if asked. Respond in Hindi-English mix. About/Privacy/Terms are now detailed in the menu."
        content = [{"type": "text", "text": f"{sys_info}\n{instruction}\nUser: {user_input}"}]
        
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
            
            tts = gTTS(text=full_res, lang='hi', tld='com.au', slow=False)
            tts.save("voice.mp3")
            with open("voice.mp3", "rb") as f: st.session_state.last_audio = f.read()
            st.rerun()
    except Exception as e: st.error(f"Error: {e}")

if st.session_state.last_audio:
    if st.button("🔈 Jawab Suniye"):
        st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
            
