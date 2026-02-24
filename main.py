import streamlit as st
from groq import Groq
import requests
import datetime
import pytz 
import time
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
REPLICATE_TOKEN = "R8_IAbdjeQkoGq2XmgP9VBN11OpmC1qfAw1IVij9"

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq API Error!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= ADVANCED CSS (FIXED ALIGNMENT) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 1rem;}

    /* Chat Input Padding for Icons */
    div[data-testid="stChatInput"] { padding-left: 90px !important; }

    /* Yellow Plus Icon - Inside Input Box Corner */
    .stFileUploader {
        position: fixed; bottom: 32px; left: 20px;
        width: 38px !important; height: 38px !important; z-index: 2005;
    }
    .stFileUploader section {
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important; width: 38px !important; height: 38px !important;
        min-height: 38px !important;
    }
    .stFileUploader label, .stFileUploader small { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 22px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 100%;
    }

    /* Mic Button - Perfectly Aligned */
    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= APP LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🚀 Pro AI")

# Icons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="v4_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='v4_mic')
st.markdown('</div>', unsafe_allow_html=True)

# Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me or say 'Generate video of...'")

# ================= FIXED VIDEO ENGINE =================
def generate_video_stable(prompt):
    headers = {"Authorization": f"Token {REPLICATE_TOKEN}", "Content-Type": "application/json"}
    
    # Using Luma Dream Machine (Very stable for text-to-video)
    payload = {
        "version": "a71f032252c416187766b1e6b52c3c662e0868f00d235c249495c2e9b980e03e",
        "input": {"prompt": prompt}
    }
    
    try:
        response = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
        data = response.json()
        
        # Check if 'urls' exists in response
        if "urls" in data:
            poll_url = data["urls"]["get"]
            with st.status("🎬 AI is rendering your video... (60s)", expanded=True) as s:
                while True:
                    result = requests.get(poll_url, headers=headers).json()
                    if result["status"] == "succeeded":
                        s.update(label="✅ Video Ready!", state="complete")
                        return result["output"]
                    elif result["status"] == "failed":
                        return f"❌ Failed: {result.get('error', 'Unknown error')}"
                    time.sleep(5)
        else:
            return f"❌ API Error: {data.get('detail', 'Check API Token or Credits')}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

# ================= PROCESS INPUT =================
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    # VIDEO CHECK
    if any(x in u_input.lower() for x in ["video", "banao", "generate"]):
        video_url = generate_video_stable(u_input)
        if "http" in str(video_url):
            st.video(video_url)
            st.session_state.messages.append({"role": "assistant", "content": "Generated Video."})
        else:
            st.error(video_url)
    else:
        # NORMAL CHAT
        with st.chat_message("assistant"):
            full_res = ""
            box = st.empty()
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": u_input}],
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    box.markdown(full_res + "▌")
            box.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
