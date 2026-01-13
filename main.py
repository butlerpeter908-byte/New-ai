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
    # Ensure GROQ_API_KEY is in your Streamlit secrets
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("❌ API Key Missing! Please check your secrets.")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= CSS: MIC NEXT TO PLACEHOLDER =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 150px; padding-top: 2rem;}
    
    /* Input Box shift to make space for Mic right next to it */
    div[data-testid="stChatInput"] { 
        margin-left: 52px !important; 
        z-index: 1000;
    }

    /* Mic Icon: Shifted exactly next to placeholder */
    .mic-fixed-container { 
        position: fixed; 
        bottom: 35px; /* Aligned with chat input bar */
        left: 20px; 
        z-index: 9999 !important; 
    }

    .mic-fixed-container button {
        background-color: #FF4B4B !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        border: 2px solid white !important;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.3) !important;
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

# ================= MENU & FEEDBACK FIX =================
if st.button("☰ MENU"):
    st.session_state.show_menu = not st.session_state.show_menu

if st.session_state.show_menu:
    st.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.subheader("📬 Feedback (GitHub)")
    feedback_input = st.text_area("Write your feedback here:")
    
    if st.button("Submit Feedback"):
        if feedback_input:
            try:
                # Correcting the Feedback Logic
                token = st.secrets["GITHUB_TOKEN"]
                repo = st.secrets["GITHUB_REPO"]
                url = f"https://api.github.com/repos/{repo}/issues"
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                data = {"title": "App Feedback", "body": feedback_input}
                response = requests.post(url, json=data, headers=headers)
                
                if response.status_code == 201:
                    st.success("✅ Feedback sent successfully!")
                else:
                    st.error(f"❌ Error: {response.status_code}. Check your Token/Repo.")
            except:
                st.error("❌ Link Error: GITHUB_TOKEN or REPO missing in secrets.")
        else:
            st.warning("Please write something first.")

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
audio = mic_recorder(start_prompt="🎤", stop_prompt="🛑", key='pro_mic_v2')
st.markdown('</div>', unsafe_allow_html=True)

user_input = st.chat_input("Ask me anything...")

# ================= GHOST REPLY & AUTO-TRIGGER FIX =================
if audio:
    # Only process if it's a NEW recording
    if st.session_state.last_audio_id != audio['id']:
        st.session_state.last_audio_id = audio['id']
        
        try:
            with st.spinner("🎙️ Transcription..."):
                transcription = client.audio.transcriptions.create(
                    file=("voice.wav", audio['bytes']),
                    model="whisper-large-v3",
                    response_format="text"
                )
                
                # NO BOLO TO NO REPLY: Check if transcription is valid and long enough
                if transcription and len(transcription.strip()) > 3:
                    user_input = transcription
                else:
                    user_input = None # Ignore background noise/silence
        except Exception as e:
            st.error("Voice failed.")
            user_input = None

# ================= RESPONSE LOGIC =================
if user_input:
    # Adding message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        with st.chat_message("assistant"):
            full_response = ""
            box = st.empty()
            
            # Context and system instruction to stop repeating time
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Pro AI. Respond in Hindi-English mix. Do not show time/date in response."},
                    {"role": "user", "content": user_input}
                ],
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    box.markdown(full_response + "▌")
            
            box.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Voice Generation
            tts = gTTS(text=full_response, lang='hi', tld='com.au')
            tts.save("res.mp3")
            with open("res.mp3", "rb") as f:
                st.session_state.last_audio_content = f.read()
            
            st.rerun()

    except Exception as e:
        st.error(f"AI Error: {e}")

# ================= AUDIO PLAYER =================
if st.session_state.last_audio_content:
    if st.button("🔈 Hear Response"):
        st.audio(st.session_state.last_audio_content, format="audio/mp3", autoplay=True)
