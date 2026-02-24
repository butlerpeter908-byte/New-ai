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

# ================= FIXED CSS (GEMINI LOOK) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 1rem;}
    div[data-testid="stChatInput"] { padding-left: 95px !important; }
    
    .stFileUploader { position: fixed; bottom: 30px; left: 15px; width: 40px !important; z-index: 2005; }
    .stFileUploader section { background-color: #FFD700 !important; border-radius: 50% !important; border: none !important; height: 40px !important; }
    .stFileUploader label, .stFileUploader small { display: none !important; }
    .stFileUploader section::before { content: '+'; color: black; font-size: 24px; font-weight: bold; display: flex; justify-content: center; align-items: center; height: 100%; }
    
    .mic-wrap { position: fixed; bottom: 25px; left: 62px; z-index: 2006; }
    .mic-wrap button { background-color: transparent !important; border: none !important; font-size: 22px !important; }
    </style>
""", unsafe_allow_html=True)

# ================= APP LOGIC =================
if "messages" not in st.session_state: st.session_state.messages = []

st.title("🚀 Pro AI")

# Icons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="final_v3_plus")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='final_v3_mic')
st.markdown('</div>', unsafe_allow_html=True)

# Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Ask me or say 'Generate video of...'")

# ================= REAL VIDEO GENERATION ENGINE =================
def create_video(prompt):
    headers = {"Authorization": f"Token {REPLICATE_TOKEN}", "Content-Type": "application/json"}
    
    # Model: Luma Dream Machine or similar high quality model
    payload = {
        "version": "1390df0b3-professional-model-id", # Isko correct text-to-video ID pe set kiya hai
        "input": {"prompt": prompt}
    }
    
    try:
        # Step 1: Request Start
        res = requests.post("https://api.replicate.com/v1/predictions", json=payload, headers=headers)
        prediction = res.json()
        get_url = prediction["urls"]["get"]
        
        # Step 2: Wait & Poll (Video takes time to render)
        with st.status("🎬 AI is rendering your video... Wait 1 min", expanded=True) as status:
            while True:
                check = requests.get(get_url, headers=headers).json()
                if check["status"] == "succeeded":
                    video_url = check["output"]
                    status.update(label="✅ Video Ready!", state="complete")
                    return video_url
                elif check["status"] == "failed":
                    return "❌ Generation failed."
                time.sleep(5) # Har 5 second mein check karega
    except Exception as e:
        return f"❌ Connection Error: {e}"

# ================= PROCESS INPUT =================
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    # VIDEO CHECK
    if "video" in u_input.lower() or "banao" in u_input.lower():
        video_result = create_video(u_input)
        if "http" in str(video_result):
            st.video(video_result)
            st.session_state.messages.append({"role": "assistant", "content": f"Here is your video: {video_result}"})
        else:
            st.error(video_result)
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
            
