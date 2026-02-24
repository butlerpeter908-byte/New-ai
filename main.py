import streamlit as st
from groq import Groq
import requests
import random
from streamlit_mic_recorder import mic_recorder

# ================= API SETUP =================
GROQ_KEY = "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"
# Aapki fresh Pexels API Key maine yahan daal di hai
PEXELS_API_KEY = "KepM3s6J4wl9TaIjAFuso1aU2wJStlw06hKNACJnRbYmh831W0r01rmi" 

try:
    client = Groq(api_key=GROQ_KEY)
except Exception as e:
    st.error("❌ Groq Error! Key check karein.")

st.set_page_config(page_title="Pro AI", layout="wide")

# ================= UI CSS (MODERN DARK) =================
st.markdown("""
    <style>
    header, footer, .stDeployButton {visibility: hidden; display: none !important;}
    [data-testid="stSidebar"] {display: none;}
    .block-container {padding-bottom: 120px; padding-top: 1rem; background-color: #0E1117;}
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

# ================= VIDEO SEARCH ENGINE =================
def get_pexels_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    # Search for HD videos
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['videos']:
                # HD Quality video link
                return data['videos'][0]['video_files'][0]['link']
        elif response.status_code == 401:
            return "AUTH_ERROR"
        return None
    except:
        return None

# ================= MAIN FLOW =================
if "messages" not in st.session_state: st.session_state.messages = []
st.title("🚀 Pro AI")

# Floating Buttons
uploaded_file = st.file_uploader("", type=["png", "jpg", "mp4"], key="final_v1")
st.markdown('<div class="mic-wrap">', unsafe_allow_html=True)
audio_data = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key='final_mic_v1')
st.markdown('</div>', unsafe_allow_html=True)

# Chat History
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Try: 'Show video of a beach'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    low_input = u_input.lower()
    
    # 🎬 VIDEO LOGIC (High Speed)
    if any(x in low_input for x in ["video", "dikhao", "show"]):
        with st.chat_message("assistant"):
            with st.spinner("🎬 Searching HD Video Library..."):
                # Clean prompt to get better search results
                search_query = low_input.replace("video", "").replace("show", "").replace("me", "").replace("of", "").strip()
                v_url = get_pexels_video(search_query if search_query else "nature")
                
                if v_url == "AUTH_ERROR":
                    st.error("❌ Pexels Key issue! Please check if your email is verified.")
                elif v_url:
                    st.video(v_url)
                    st.session_state.messages.append({"role": "assistant", "content": f"Loaded HD video for '{search_query}'"})
                else:
                    st.warning("⚠️ No video found. Try another topic!")
    
    # 🖼️ IMAGE LOGIC (Pollinations)
    elif any(x in low_input for x in ["image", "photo", "banao"]):
        with st.chat_message("assistant"):
            with st.spinner("🖼️ Generating Image..."):
                img_url = f"https://image.pollinations.ai/prompt/{u_input.replace(' ','%20')}?nologo=true&seed={random.randint(1,999)}"
                st.image(img_url)
                st.session_state.messages.append({"role": "assistant", "content": "Image generated!"})
    
    # 💬 SMART CHAT (Groq)
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
            
