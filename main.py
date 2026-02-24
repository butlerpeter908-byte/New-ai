import streamlit as st
from groq import Groq
import requests
from gtts import gTTS
import base64
import time

# ================= API SETUP =================
GROQ_KEY = "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"
# Is baar hum naya Model use karenge jo User Prompt pe dhyan de
HF_TOKEN = "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" 

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="Custom Pro AI", layout="wide")

# ================= VOICE SYNC ENGINE =================
def play_voice(text):
    tts = gTTS(text=text, lang='hi')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio src="data:audio/mp3;base64,{b64}" autoplay></audio>'
        st.markdown(md, unsafe_allow_html=True)

# ================= CUSTOM VIDEO GENERATOR =================
def generate_custom_video(prompt):
    # Ye API user ke prompt se "Nayi" video banayegi
    API_URL = "https://api-inference.huggingface.co/models/ByteDance/AnimateDiff-Lightning"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

# ================= APP UI =================
st.title("🎬 Custom Video & Voice AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

u_input = st.chat_input("Jaise: 'A bottle talking about health'...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        # 1. Groq se Answer Lo
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": u_input}]
        )
        answer = res.choices[0].message.content
        st.write(answer)
        
        # 2. Voice Play Karo (Wahi jo AI ne likha hai)
        play_voice(answer)

        # 3. Custom Video Generate Karo (Slow but Accurate)
        with st.spinner("⏳ User ke hisab se video bana raha hoon... (Thoda sabr rakhein)"):
            video_bytes = generate_custom_video(u_input)
            
            if video_bytes:
                st.video(video_bytes)
                st.success("✅ Video generated as per your wish!")
            else:
                st.warning("⚠️ Server abhi busy hai, par aap meri awaz sun sakte hain!")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    
