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

# ================= UI CSS =================
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

# ================= MULTI-MODEL VIDEO ENGINE =================
def generate_free_video(prompt):
    # Models ki list jo hum try karenge
    models = [
        "LanguageBind/Video-LLaVA-7B", # Pehla option
        "vdo/zeroscope_v2_576w",        # Dusra option
        "ByteDance/AnimateDiff"         # Teesra option
    ]
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    for model_name in models:
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
        try:
            with st.status(f"🎬 Trying model: {model_name.split('/')[-1]}...", expanded=True) as s:
                response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=120)
                
                if response.status_code == 200:
                    s.update(label="✅ Video Ready!", state="complete")
                    return response.content
                elif response.status_code == 503:
                    s.write("⏳ AI is warming up... wait 15s")
                    time.sleep(15)
                    # Retry once
                    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
                    if response.status_code == 200: return response.content
                
                s.write(f"⚠️ Model {model_name.split('/')[-1]} busy, switching...")
                continue # Next model par jao
        except:
            continue

    return "❌ All free models are busy right now. Please try again in 2 minutes."

# ================= APP LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []
st.title("🚀 Pro AI")

uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="v_ultimate")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='mic_ultimate')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Say 'Generate video of a flying dragon'...")

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
            
