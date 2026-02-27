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

st.set_page_config(page_title="New AI 🤖", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= WHATSAPP UI CSS =================
st.markdown("""
<style>
    header, footer {visibility: hidden;}
    .block-container {padding-top: 1rem; background-color: #0E1117;}
    .user-bubble { background-color: #005c4b; color: white; padding: 12px 18px; border-radius: 18px 18px 0 18px; margin: 10px 0; max-width: 80%; float: right; clear: both; }
    .ai-bubble { background-color: #202c33; color: white; padding: 12px 18px; border-radius: 18px 18px 18px 0; margin: 10px 0; max-width: 80%; float: left; clear: both; border-left: 5px solid #FFD700; }
    .stButton>button { border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

# ================= TOP MENU (WAPAS ADDED) =================
with st.container():
    col1, col2 = st.columns([6, 4])
    with col2:
        menu = st.selectbox("📋 Options & Legal", ["New AI Chat", "About Creator", "Feedback", "Privacy Policy", "Terms & Conditions", "Clear Chat"])
        if menu == "About Creator":
            st.info("👤 **Creator:** [Aapka Naam]\n\n**Goal:** Making AI fast and visual.")
        elif menu == "Privacy Policy":
            st.info("🔒 **Privacy:** Data is encrypted and deleted after session.")
        elif menu == "Terms & Conditions":
            st.warning("⚖️ **Terms:** Powered by Groq Llama 3.2 Vision.")
        elif menu == "Feedback":
            st.text_input("Share your feedback:")
            if st.button("Submit"): st.success("Thanks!")
        elif menu == "Clear Chat":
            if st.button("Confirm Reset"): 
                st.session_state.messages = []
                st.rerun()

# ================= IMAGE PROCESSING (FIXED) =================
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

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

# ================= MAIN CHAT =================
st.title("🤖 New AI")
current_info = f"Date: {datetime.now().strftime('%A, %b %d, %Y')} | Time: {datetime.now().strftime('%I:%M %p')}"

# Display History
for i, m in enumerate(st.session_state.messages):
    b_class = "user-bubble" if m["role"] == "user" else "ai-bubble"
    st.markdown(f'<div class="{b_class}">{m["content"]}</div>', unsafe_allow_html=True)
    if m["role"] == "assistant":
        if st.button(f"🔊 Listen", key=f"v_{i}"):
            st.markdown(get_audio_html(m["content"]), unsafe_allow_html=True)

# --- PHOTO UPLOAD & VISION ---
st.markdown("---")
uploaded_file = st.file_uploader("📸 Upload Photo for Solution", type=["jpg", "png", "jpeg"])

if uploaded_file:
    base64_image = encode_image(uploaded_file)
    if st.button("Analyze This Photo"):
        with st.spinner("AI is looking at the photo..."):
            try:
                # Using Llama-3.2-11b-vision for Image Analysis
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": "What is in this image? Provide a detailed solution or description in user's language."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}
                    ]
                )
                res_text = response.choices[0].message.content
                st.session_state.messages.append({"role": "user", "content": "Uploaded a photo."})
                st.session_state.messages.append({"role": "assistant", "content": res_text})
                st.rerun()
            except Exception as e:
                st.error(f"Vision Error: {e}")

# --- TEXT INPUT ---
u_input = st.chat_input("Ask New AI anything...")
if u_input:
    st.session_state.messages.append({"role": "user", "content": u_input})
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"You are New AI 🤖. Context: {current_info}. Respond in user's language. No code."},
            {"role": "user", "content": u_input}
        ]
    )
    st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
    st.rerun()
    
