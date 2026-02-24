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

# ================= STABLE VIDEO ENGINE =================
def generate_free_video(prompt):
    # Sabse stable models ka naya order
    models = [
        "ali-vilab/modelscope-damo-text-to-video-dynamics",
        "guoyww/AnimateDiff",
        "strangerzonehf/Animov-0.1"
    ]
    
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    for model_name in models:
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
        try:
            with st.status(f"🚀 Connecting to: {model_name.split('/')[-1]}...", expanded=True) as s:
                # Prompt ko clean karna
                payload = {"inputs": prompt, "parameters": {"num_frames": 16}}
                response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
                
                if response.status_code == 200:
                    s.update(label="✅ Video Ready!", state="complete")
                    return response.content
                elif response.status_code == 503:
                    s.write("⏳ Model is starting up (Cold Start)... Waiting 20s")
                    time.sleep(20)
                    response = requests.post(API_URL, headers=headers, json=payload)
                    if response.status_code == 200: return response.content
                
                s.write(f"⚠️ {model_name.split('/')[-1]} is under heavy load, switching...")
                continue
        except:
            continue

    return "❌ Servers are very busy. Pro Tip: Try a shorter prompt or wait 2 minutes."

# ================= APP LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []
st.title("🚀 Pro AI")

uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="v_pro_fix")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='mic_pro_fix')
st.markdown('</div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me or 'Generate video of...'")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    if any(x in u_input.lower() for x in ["video", "banao", "generate"]):
        video_data = generate_free_video(u_input)
        if isinstance(video_data, bytes):
            st.video(video_data)
        else:
            st.warning(video_data)
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
            
