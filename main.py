import streamlit as st
from groq import Groq
import base64
from gtts import gTTS

# Secrets se API Key uthana
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Pehle Streamlit Settings mein GROQ_API_KEY daalein!")

st.set_page_config(page_title="Ultimate Pro AI", layout="wide")
st.title("🚀 Pro AI: Voice + Vision + Fast")

if "usage_count" not in st.session_state: st.session_state.usage_count = 0
if "messages" not in st.session_state: st.session_state.messages = []

# Sidebar
voice_type = st.sidebar.selectbox("Voice Gender:", ["Female (Aarti)", "Male (Akash)"])
uploaded_file = st.sidebar.file_uploader("Photo Upload", type=["jpg", "png", "jpeg"])

# Chat History dikhana
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Limit check (5 Free Chats)
if st.session_state.usage_count < 5:
    if prompt := st.chat_input("Kuch puchiye..."):
        st.session_state.usage_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        try:
            content = [{"type": "text", "text": f"Quickly answer in Hindi: {prompt}"}]
            if uploaded_file:
                img = base64.b64encode(uploaded_file.read()).decode('utf-8')
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
                st.image(uploaded_file, width=150)

            with st.chat_message("assistant"):
                res_box = st.empty()
                full_res = ""
                comp = client.chat.completions.create(model="llama-3.2-11b-vision-preview", messages=[{"role": "user", "content": content}], stream=True)
                for chunk in comp:
                    if chunk.choices[0].delta.content:
                        full_res += chunk.choices[0].delta.content
                        res_box.markdown(full_res + "▌")
                res_box.markdown(full_res)
                
                # Voice Output
                tld = 'co.in' if voice_type == "Male (Akash)" else 'com'
                tts = gTTS(text=full_res, lang='hi', tld=tld)
                tts.save("res.mp3")
                st.audio("res.mp3", format="audio/mp3", autoplay=True)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e: st.error(f"Error: {e}")
else:
    st.warning("Aapka free trial khatam ho gaya hai! Sign Up karein.")
  
