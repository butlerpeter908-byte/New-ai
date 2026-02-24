import streamlit as st
from groq import Groq
import requests
import time
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
HF_TOKEN = "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" 

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq API Error!")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= UI CSS (GEMINI LOOK) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 1rem;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }

    .stFileUploader {
        position: fixed; bottom: 32px; left: 20px;
        width: 40px !important; height: 40px !important; z-index: 2005;
    }
    .stFileUploader section {
        background-color: #FFD700 !important; border-radius: 50% !important;
        border: none !important; width: 40px !important; height: 40px !important;
    }
    .stFileUploader label, .stFileUploader small { display: none !important; }
    .stFileUploader section::before {
        content: '+'; color: black; font-size: 24px; font-weight: bold;
        display: flex; justify-content: center; align-items: center; height: 100%;
    }

    .mic-wrap { position: fixed; bottom: 28px; left: 65px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= NEW STABLE FREE VIDEO ENGINE =================
def generate_free_video(prompt):
    # Using VideoCrafter - A more stable free model on HF
    API_URL = "https://api-inference.huggingface.co/models/VideoCrafter/VideoCrafter2"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        with st.status("🎬 AI is rendering your video (Free Mode)...", expanded=True) as s:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
            
            # 503 means model is loading
            if response.status_code == 503:
                s.write("⏳ AI Model is waking up... waiting 30 seconds.")
                time.sleep(30)
                response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

            if response.status_code == 200:
                s.update(label="✅ Video Ready!", state="complete")
                return response.content 
            elif response.status_code == 403:
                return "❌ Token Error: Please make sure your token has 'Inference' permissions enabled in HF settings."
            else:
                # If VideoCrafter fails, let's try a fallback model
                return f"❌ Model Busy (Error {response.status_code}). Please try again in a minute."
    except Exception as e:
        return f"❌ System Error: {str(e)}"

# ================= APP LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []
st.title("🚀 Pro AI")

uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="v_final_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='v_final_mic')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Generate a video of...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    if any(x in u_input.lower() for x in ["video", "banao", "generate"]):
        video_data = generate_free_video(u_input)
        if isinstance(video_data, bytes):
            st.video(video_data)
        else:
            st.error(video_data)
    else:
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
            
