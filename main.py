import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import os

# Secrets se API Key uthana
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Pehle Streamlit Settings mein GROQ_API_KEY daalein!")

st.set_page_config(page_title="Pro AI", layout="wide")
st.title("🚀 Pro AI: Voice + Vision")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR (Voice Selection) ---
st.sidebar.title("Settings")
voice_type = st.sidebar.selectbox("Awaz Chunein:", ["Aarti (Female)", "Akash (Male)"])

# Voice settings fix
tld_choice = 'com' if voice_type == "Aarti (Female)" else 'co.in'

# Chat history dikhana
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- CHAT INPUT AUR UPLOAD ---
uploaded_file = st.file_uploader("Upload Image (Optional)", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Mujhse apni bhasha mein baat karein..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        content = [{"type": "text", "text": f"Respond naturally in the same language as the user: {prompt}"}]
        
        if uploaded_file:
            img = base64.b64encode(uploaded_file.read()).decode('utf-8')
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            st.image(uploaded_file, width=150)

        with st.chat_message("assistant"):
            res_box = st.empty()
            full_res = ""
            comp = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "user", "content": content}], 
                stream=True
            )
            for chunk in comp:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    res_box.markdown(full_res + "▌")
            res_box.markdown(full_res)
            
            # --- MANUAL AUDIO OPTION ---
            # Jab tak user button nahi dabayega, awaz nahi aayegi
            if st.button("🔈 Suniye (Listen)"):
                try:
                    tts = gTTS(text=full_res, lang='hi', tld=tld_choice)
                    tts.save("response.mp3")
                    st.audio("response.mp3", format="audio/mp3", autoplay=True)
                except Exception as voice_err:
                    st.error("Audio generate nahi ho paya.")
            
            st.session_state.messages.append({"role": "assistant", "content": full_res})
            
    except Exception as e:
        st.error(f"Error: {e}")
