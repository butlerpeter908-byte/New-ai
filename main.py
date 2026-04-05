import streamlit as st
from groq import Groq
import smtplib
import random
from email.mime.text import MIMEText

# ================= 1. SETUP =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="New AI 🤖", layout="wide")

# ================= 2. THE PERMANENT CSS (OTP Square Fix) =================
st.markdown(f"""
    <style>
    :root {{ color-scheme: dark; }}
    header, footer {{ visibility: hidden !important; }}
    .stApp {{ 
        background: radial-gradient(circle at top, #1a1f25 0%, #0e1117 100%) !important;
        color: #e0e0e0 !important;
    }}

    /* CHAT INPUT BOTTOM FIX */
    div[data-testid="stChatInput"] {{
        position: fixed !important;
        bottom: 30px !important;
        z-index: 9999 !important;
    }}

    /* OTP SQUARE BOX LOGIC */
    .otp-input-container {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
    }}
    
    /* Styling the Streamlit Input to look like Squares */
    div[data-testid="stTextInput"] > div > div > input {{
        text-align: center;
        font-size: 30px !important;
        letter-spacing: 25px !important; /* Space between numbers to align with squares */
        font-weight: bold;
        background: transparent !important;
        border: none !important;
        color: #00ff88 !important;
        width: 250px !important;
        caret-color: transparent; /* Cursor hide kar diya */
    }}

    .square-bg {{
        position: absolute;
        display: flex;
        gap: 15px;
        z-index: -1;
    }}

    .box {{
        width: 50px; height: 60px;
        border: 2px solid rgba(0, 255, 136, 0.3);
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.05);
    }}

    .welcome-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
    }}

    .user-msg {{ background: linear-gradient(135deg, #00b09b, #96c93d); padding: 12px; border-radius: 18px 18px 2px 18px; margin: 10px 0; text-align: right; margin-left: auto; max-width: 80%; }}
    .ai-msg {{ background: rgba(255, 255, 255, 0.08); padding: 12px; border-radius: 18px 18px 18px 2px; margin: 10px 0; border-left: 4px solid #00ff88; max-width: 80%; }}
    
    .stException, .stAlert {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.markdown('<div class="welcome-card"><h1 style="color:#00ff88;">WELCOME</h1><p>Siddique\'s AI Secure Portal</p></div>', unsafe_allow_html=True)
    
    if not st.session_state.otp_sent:
        email = st.text_input("Gmail ID:", value=st.session_state.user_email)
        if st.button("Send Secure OTP", use_container_width=True):
            if "@gmail.com" in email:
                otp = str(random.randint(1000, 9999))
                if send_mail(email, "Login OTP", f"Aapka OTP: {otp}"):
                    st.session_state.generated_otp = otp; st.session_state.user_email = email
                    st.session_state.otp_sent = True; st.rerun()
    else:
        st.markdown(f"<p style='text-align:center;'>OTP Sent to {st.session_state.user_email}</p>", unsafe_allow_html=True)
        
        # --- NEW SINGLE OTP UI ---
        st.write("### ENTER PIN")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            # Squares Background
            st.markdown("""
                <div style="display: flex; gap: 15px; margin-bottom: -65px; margin-left: 15px;">
                    <div class="box"></div><div class="box"></div><div class="box"></div><div class="box"></div>
                </div>
            """, unsafe_allow_html=True)
            
            # Single Input that overlays on squares
            otp_in = st.text_input("", value="", max_chars=4, key="otp_entry", label_visibility="collapsed")
        
        if st.button("Verify & Enter", use_container_width=True):
            if otp_in == st.session_state.generated_otp: 
                st.session_state.logged_in = True; st.rerun()
            else: st.error("Invalid PIN!")
            
        if st.button("Change Email"):
            st.session_state.otp_sent = False; st.rerun()
    st.stop()

# ================= 5. MAIN APP =================
with st.sidebar:
    st.write(f"👤 {st.session_state.user_email}")
    if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.session_state.otp_sent = False; st.rerun()

tab_chat, tab_set, tab_fb = st.tabs(["💬 Messenger", "⚙️ Settings", "📩 Feedback"])

with tab_chat:
    chat_box = st.container()
    with chat_box:
        for m in st.session_state.messages:
            div = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)

    q = st.chat_input("Type your message here...")
    if q:
        # Identity Logic: Only if asked
        instr = {"role": "system", "content": f"Be helpful. ONLY if asked about owner/creator, say {CREATOR} made you."}
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[instr] + st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: pass

with tab_fb:
    fb = st.text_area("Feedback for Siddique:")
    if st.button("Submit"):
        if fb and send_mail(MY_GMAIL, "Feedback", fb):
            st.success("Sent!"); time.sleep(1); st.rerun()
                  
