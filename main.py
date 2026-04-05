import streamlit as st
from groq import Groq
import smtplib
import random
import time
from email.mime.text import MIMEText

# ================= 1. SETUP =================
GROQ_KEY = "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"
MY_GMAIL = "butlerpeter908@gmail.com"
APP_PASS = "rkpi toiq sdgj vfvn" 
CREATOR = "Siddique Mohd Saif"

client = Groq(api_key=GROQ_KEY)

st.set_page_config(page_title="New AI 🤖", layout="wide")

# ================= 2. MODERN UI CSS =================
st.markdown(f"""
    <style>
    :root {{ color-scheme: dark; }}
    header, footer {{ visibility: hidden !important; }}
    
    .stApp {{ 
        background: #0e1117 !important;
        background-image: radial-gradient(circle at 20% 30%, rgba(0, 255, 136, 0.05) 0%, transparent 40%),
                          radial-gradient(circle at 80% 70%, rgba(0, 210, 255, 0.05) 0%, transparent 40%) !important;
        color: #e0e0e0 !important;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: rgba(20, 25, 35, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}

    /* Card & Container Style */
    .welcome-card, .thanks-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 24px;
        padding: 40px 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}

    .welcome-text {{
        font-size: 42px;
        font-weight: 900;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #00ff88, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }}

    /* Chat Bubbles - Improved Spacing */
    .chat-container {{
        display: flex;
        flex-direction: column;
        gap: 15px;
        padding-bottom: 120px;
    }}

    .user-msg {{ 
        align-self: flex-end;
        background: linear-gradient(135deg, #00b09b, #96c93d); 
        padding: 12px 18px; 
        border-radius: 20px 20px 4px 20px; 
        color: white;
        max-width: 85%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}

    .ai-msg {{ 
        align-self: flex-start;
        background: rgba(255, 255, 255, 0.07); 
        padding: 12px 18px; 
        border-radius: 20px 20px 20px 4px; 
        border-left: 4px solid #00ff88;
        max-width: 85%;
        backdrop-filter: blur(5px);
    }}

    /* Fixed Bottom Input */
    div[data-testid="stChatInput"] {{
        position: fixed !important;
        bottom: 25px !important;
        left: 5% !important;
        right: 5% !important;
        width: 90% !important;
        z-index: 9999 !important;
        background: rgba(14, 17, 23, 0.95) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        border-radius: 20px !important;
        padding: 5px !important;
    }}

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: transparent;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 8px 16px;
        color: #888;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: rgba(0, 255, 136, 0.1) !important;
        color: #00ff88 !important;
        border: 1px solid rgba(0, 255, 136, 0.5) !important;
    }}

    .stException, .stAlert {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# ================= 3. SESSION LOGIC =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "fb_sent" not in st.session_state: st.session_state.fb_sent = False

def send_mail(to, sub, body):
    try:
        msg = MIMEText(body); msg['Subject'] = sub; msg['From'] = MY_GMAIL; msg['To'] = to
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_GMAIL, APP_PASS); s.send_message(msg)
        return True
    except: return False

# ================= 4. LOGIN SCREEN =================
if not st.session_state.logged_in:
    st.markdown(f'<div class="welcome-card"><div class="welcome-text">NEW AI</div><p style="color:#888; letter-spacing:2px;">SECURE PORTAL BY {CREATOR.upper()}</p></div>', unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        email = st.text_input("Gmail ID:", value=st.session_state.user_email, placeholder="example@gmail.com")
        
        if not st.session_state.otp_sent:
            if st.button("Get Access Code", use_container_width=True):
                if "@gmail.com" in email:
                    otp = str(random.randint(1000, 9999))
                    if send_mail(email, "Login OTP", f"Aapka OTP: {otp}"):
                        st.session_state.generated_otp = otp; st.session_state.user_email = email
                        st.session_state.otp_sent = True; st.rerun()
        else:
            st.success(f"Code sent to {st.session_state.user_email}")
            otp_in = st.text_input("Enter 4-Digit PIN:", type="password", placeholder="****")
            if st.button("Verify & Login", use_container_width=True):
                if otp_in == st.session_state.generated_otp: st.session_state.logged_in = True; st.rerun()
                else: st.error("Wrong PIN!")
            if st.button("Edit Email", variant="secondary"): 
                st.session_state.otp_sent = False; st.rerun()
    st.stop()

# ================= 5. MAIN INTERFACE =================
with st.sidebar:
    st.markdown(f"### Welcome\n**{st.session_state.user_email}**")
    st.divider()
    if st.button("🗑️ Clear History", use_container_width=True): st.session_state.messages = []; st.rerun()
    if st.button("🚪 Sign Out", use_container_width=True): st.session_state.logged_in = False; st.rerun()

tab_chat, tab_settings, tab_feedback = st.tabs(["💬 Messenger", "⚙️ Control", "📩 Support"])

# --- CHAT TAB ---
with tab_chat:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        div = "user-msg" if m["role"] == "user" else "ai-msg"
        st.markdown(f'<div class="{div}">{m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    q = st.chat_input("Kaise madad kar sakta hoon?")
    if q:
        st.session_state.messages.append({"role": "user", "content": q})
        try:
            instruction = {"role": "system", "content": f"You are a helpful AI. ONLY if asked about your creator/owner, say you were developed by {CREATOR}."}
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[instruction] + st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()
        except: st.error("Server down...")

# --- SETTINGS TAB ---
with tab_settings:
    st.markdown(f"### System Status: <span style='color:#00ff88;'>Online</span>", unsafe_allow_html=True)
    st.info(f"Developer: {CREATOR}")
    st.write("Privacy: Session history is cleared after logout.")

# --- FEEDBACK TAB ---
with tab_feedback:
    if st.session_state.fb_sent:
        st.markdown(f'<div class="thanks-card"><div class="thanks-text">SENT!</div><p>Aapka feedback {CREATOR} ko mil gaya hai.</p></div>', unsafe_allow_html=True)
        if st.button("Send New"): st.session_state.fb_sent = False; st.rerun()
    else:
        fb = st.text_area("Hume bataiye hum kaise behtar ban sakte hain...", height=150)
        if st.button(f"Send to {CREATOR.split()[0]}", use_container_width=True):
            if fb and send_mail(MY_GMAIL, "New App Feedback", f"User: {st.session_state.user_email}\n{fb}"):
                st.session_state.fb_sent = True; st.rerun()
    
