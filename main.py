import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from datetime import datetime
from PIL import Image

# ================= API SETUP =================
GROQ_KEY = "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" 
client = Groq(api_key=GROQ_KEY)

# AI ka Naya Naam aur Symbol
st.set_page_config(page_title="New AI 🤖", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= UI CSS (BUBBLES) =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem; background-color: #0E1117;}
    .user-bubble { background-color: #005c4b; color: white; padding: 12px 18px; border-radius: 18px 18px 0 18px; margin: 10px 0; max-width: 80%; float: right; clear: both; }
    .ai-bubble { background-color: #202c33; color: white; padding: 12px 18px; border-radius: 18px 18px 18px 0; margin: 10px 0; max-width: 80%; float: left; clear: both; border-left: 5px solid #FFD700; }
    .stButton>button { border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

# ================= VOICE LOGIC =================
def get_audio_html(text):
    try:
        lang = 'hi' if any(ord(c) > 2300 for c in text) else 'en'
        tts = gTTS(text=text, lang=lang, tld='co.in', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        return f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>'
    except: return ""

# ================= MAIN APP =================
st.title("🤖 New AI") # Naya Naam

now = datetime.now()
current_info = f"Date: {now.strftime('%A, %b %d, %Y')} | Time: {now.strftime('%I:%M %p')}"

# Display Chat
for i, m in enumerate(st.session_state.messages):
    b_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{b_class}">{m["content"]}</div>', unsafe_allow_html=True)
    if m["role"] == "assistant":
        if st.button(f"🔊 Listen", key=f"v_{i}"):
            st.markdown(get_audio_html(m["content"]), unsafe_allow_html=True)

st.markdown("---")

# --- FILE UPLOAD OPTION ---
uploaded_file = st.file_uploader("Upload a photo for solution 📸", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Photo", width=300)
    if st.button("Get Solution from Photo"):
        # Yahan AI Vision Logic aayegi (Llama-3.2-Vision model use kar sakte hain)
        st.session_state.messages.append({"role": "user", "content": "Analyzing this photo..."})
        st.info("Bhai, photo analysis active ho raha hai... (Llama Vision model loading)")

# --- TEXT INPUT ---
u_input = st.chat_input("Ask New AI anything...")

if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are New AI 🤖. Context: {current_info}. Navi Mumbai. Direct answer in user's language. No code."},
                {"role": "user", "content": u_input}
            ]
        )
        reply = res.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")

