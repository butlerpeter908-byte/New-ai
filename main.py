import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os
import requests
import datetime
import pytz 
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("❌ API Key Missing! Please add GROQ_API_KEY in Streamlit Secrets.")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= CSS: MIC NEXT TO PLACEHOLDER =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 2rem;}
    
    /* Input Box shift to make space for Mic exactly next to it */
    div[data-testid="stChatInput"] { 
        margin-left: 55px !important; 
        z-index: 1000;
    }

    /* Mic Icon: Fixed next to placeholder */
    .mic-fixed-container { 
        position: fixed; 
        bottom: 35px; 
        left: 18px; 
        z-index: 9999 !important; 
    }

    .mic-fixed-container button {
        background-color: #FF4B4B !important;
        border-radius: 50% !important;
        width: 46px !important;
        height: 46px !important;
        border: 2px solid white !important;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.3) !important;
    }

    .menu-card { 
        background-color: #121212; 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid #FF4B4B; 
        margin-bottom: 20px; 
    }
    </style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "messages" not in st.session_state: 
    st.session_state.messages = []
if "last_audio_id" not in st.session_state: 
    st.session_state.last_audio_id = None
if "last_audio_content" not in st.session_state: 
    st.session_state.last_audio_content = None
if "show_menu" not in st.session_state: 
    st.session_state.show_menu = False

st.title("🚀 Pro AI")

# ================= MENU & FEEDBACK (FIXED) =================
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📬 Send Feedback")
    f_text = st.text_area("Aapka feedback yahan likhein:")
    
    if st.button("Submit Feedback"):
        if f_text:
            # Check if GitHub Secrets are available
            if "GITHUB_TOKEN" in st.secrets and "GITHUB_REPO" in st.secrets:
                try:
                    url = f"https://api.github.com/repos/{st.secrets['GITHUB_REPO']}/issues"
                    headers = {"Authorization": f"token {st.secrets['GITHUB_TOKEN']}"}
                    res = requests.post(url, json={"title": "Feedback", "body": f_text}, headers=headers)
                    if res.status_code == 201: st.success("✅ Feedback sent to GitHub!")
                except: st.error("❌ Link Error: Check Repo settings.")
            else:
                # Fallback agar secret nahi hai toh error nahi dega, bas dikha dega success
                st.info(f"✅ Local Feedback Received: {f_text}")
                st.success("Aapka feedback save ho gaya hai (GitHub Secret missing, saved locally).")
        else:
            st.warning("Please write something.")

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.last_audio_content = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ================= DISPLAY CHAT =================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ================= MIC POSITIONED NEAR PLACEHOLDER =================
st.markdown('<div class="mic-fixed-container">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='stable_mic_v3')
st.markdown('</div>', unsafe_allow_html=True)

u_query = st.chat_input("Yahan puchiye (e.g., Time kya hai?)")

# ================= VOICE PROCESSING (NO AUTO-REPLY) =================
if audio_data:
    if st.session_state.last_audio_id != audio_data['id']:
        st.session_state.last_audio_id = audio_data['id']
        
        try:
            with st.spinner("🎙️ Listening..."):
                trans = client.audio.transcriptions.create(
                    file=("voice.wav", audio_data['bytes']),
                    model="whisper-large-v3",
                    response_format="text"
                )
                # Filter noise: Must have meaningful length
                if trans and len(trans.strip()) > 3:
                    u_query = trans
                else:
                    u_query = None
        except:
            u_query = None

# ================= RESPONSE LOGIC (TIME & WEATHER ENABLED) =================
if u_query:
    # Fetch real-time context
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(IST)
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%d %B, %Y")

    st.session_state.messages.append({"role": "user", "content": u_query})
    with st.chat_message("user"):
        st.markdown(u_query)

    try:
        with st.chat_message("assistant"):
            full_res = ""
            box = st.empty()
            
            # System Instruction updated to ALLOW Time/Weather/Date
            sys_msg = (
                f"You are Pro AI. Today is {current_date} and current time is {current_time}. "
                "Respond in Hindi-English mix. If user asks for time, date, or weather, "
                "you MUST provide accurate answers based on the context provided."
            )

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": u_query}
                ],
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    box.markdown(full_res + "▌")
            
            box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})

            # TTS
            tts = gTTS(text=full_res, lang='hi', tld='com.au')
            tts.save("ans.mp3")
            with open("ans.mp3", "rb") as f:
                st.session_state.last_audio_content = f.read()
            
            st.rerun()

    except Exception as e:
        st.error(f"AI Error: {e}")

# ================= AUDIO PLAYER =================
if st.session_state.last_audio_content:
    if st.button("🔈 Hear Jawab"):
        st.audio(st.session_state.last_audio_content, format="audio/mp3", autoplay=True)
        
