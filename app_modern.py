import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# [Streamlit 설정]
st.set_page_config(
    page_title="My AI Teacher - Modern",
    page_icon="🤖",
    layout="centered"
)

# [프리미엄 모던 메신저 UI 디자인]
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
    /* 배경 및 전역 폰트 */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* 헤더 디자인 */
    .app-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        background: #ffffff;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 2rem;
    }
    
    .app-header h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 1.8rem;
        color: #0f172a;
        margin: 0;
    }
    
    .app-header p {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* 사이드바 글래스모피즘 */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* 채팅 메시지 디자인 개선 */
    .stChatMessage {
        border: none !important;
        background-color: transparent !important;
        padding: 0.5rem 0 !important;
    }
    
    /* 시스템 알림 스타일 */
    .system-notification {
        background-color: #f1f5f9;
        color: #475569;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        font-size: 0.85rem;
        text-align: center;
        margin: 1rem 0;
        border: 1px dashed #cbd5e1;
    }

    /* 오디오 플레이어 슬림 디자인 */
    audio {
        height: 30px;
        width: 200px;
        opacity: 0.7;
        transition: opacity 0.3s;
    }
    audio:hover { opacity: 1; }

    /* 입력창 디자인 */
    .stChatInputContainer {
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    
    /* 인용구 스타일 (Correction & Suggestions) */
    blockquote {
        border-left: 3px solid #6366f1 !important;
        background-color: #f8faff !important;
        padding: 1rem !important;
        border-radius: 0 12px 12px 0;
        color: #1e293b !important;
    }
    </style>
    
    <div class="app-header">
        <h1>🎓 My AI Teacher</h1>
        <p>Simple, Modern, and Intelligent English Learning</p>
    </div>
    """, unsafe_allow_html=True)

# [세션 상태 관리]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "current_config" not in st.session_state:
    st.session_state.current_config = {"level": None, "topic": None}
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# [사이드바 설정] 최소화된 디자인
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # 1. secrets.toml 또는 Streamlit Cloud Secrets에서 키 확인
    if "GEMINI_API_KEY" in st.secrets:
        st.success("✅ API Key loaded from secrets")
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        # 2. 설정이 없는 경우에만 입력창 표시
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your key here or set it in secrets.toml")
    
    level = st.selectbox("Your Level", ["초급", "중급", "고급"])
    topic = st.selectbox("Topic", ["자기소개", "여행", "쇼핑", "음식점", "직장생활", "자유대화"])
    
    auto_speak = st.checkbox("Auto-play voice", value=True)
    
    if st.button("🔄 Start New Session"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.session_state.current_config = {"level": level, "topic": topic}
        st.rerun()

    st.markdown("---")
    st.caption("v2.1 Secured Edition")

# [핵심 로직]
def text_to_speech(text):
    # '💡 Correction' 이나 '🎯 Suggested' 로 시작하지 않는 첫 문장만 음성으로 변환
    main_text = ""
    for line in text.split('\n'):
        if line.strip() and not any(symbol in line for symbol in ["💡", "🎯", "🗣️"]):
            main_text = line
            break
    
    if not main_text: return None
    
    try:
        tts = gTTS(text=main_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except Exception:
        return None

# API 키가 여전히 없을 때만 안내 메시지 출력
if not api_key:
    st.markdown('<div class="system-notification">🔑 Please enter your Gemini API Key in the sidebar to start learning.</div>', unsafe_allow_html=True)
    st.stop()

genai.configure(api_key=api_key)

def get_system_prompt(level, topic):
    level_instruction = {
        "초급": "Use short, simple sentences.",
        "중급": "Use natural expressions and idioms.",
        "고급": "Use sophisticated vocabulary and complex grammar."
    }
    return f"""
    You are a friendly and encouraging English teacher. 
    Student Level: {level}, Topic: {topic}
    Style: {level_instruction[level]}

    Rules:
    1. Respond naturally and keep the conversation moving.
    2. Be flexible: acknowledge answers even if slightly off-topic and move forward.
    3. If any grammer error occurs, use '💡 Correction'.
    4. End with a NEW question and 2 '🎯 Suggested Answers'.
    """

# 채팅 시작
if st.session_state.chat_session is None or st.session_state.current_config["level"] != level or st.session_state.current_config["topic"] != topic:
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        st.session_state.chat_session = model.start_chat(history=[])
        response = st.session_state.chat_session.send_message(f"System Instruction: {get_system_prompt(level, topic)}\n\nHello! Start the conversation.")
        st.session_state.messages = [{"role": "assistant", "content": response.text}]
        st.session_state.current_config = {"level": level, "topic": topic}
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

# 히스토리 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            audio_fp = text_to_speech(msg["content"])
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

# 입력 UI
st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns([1, 5])
with c1:
    audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="🛑 Stop", key="mic")
with c2:
    text_input = st.chat_input("Say something to your teacher...")

user_input = None
if audio:
    audio_id = audio['id'] if 'id' in audio else hash(audio['bytes'])
    if st.session_state.last_processed_audio != audio_id:
        with st.spinner("Analyzing voice..."):
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
                res = model.generate_content([{"mime_type": "audio/wav", "data": audio['bytes']}, "Transcribe as English text."])
                user_input = res.text.strip()
                st.session_state.last_processed_audio = audio_id
            except:
                st.error("Audio error.")

if not user_input and text_input:
    user_input = text_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            res = st.session_state.chat_session.send_message(user_input)
            st.markdown(res.text)
            audio_fp = text_to_speech(res.text)
            if audio_fp: st.audio(audio_fp, format="audio/mp3")
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()
