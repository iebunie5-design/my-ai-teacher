import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# [Streamlit 설정] 브라우저 탭 제목, 아이콘, 레이아웃을 설정합니다.
st.set_page_config(
    page_title="My AI Teacher - Modern",
    page_icon="🤖",
    layout="centered"
)

# [프리미엄 모던 메신저 UI 디자인] 커스텀 CSS를 사용하여 앱의 디자인을 고급스럽게 꾸밉니다.
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
    /* 배경색과 기본 폰트(Inter) 설정 */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* 화면 상단 헤더 영역 디자인 */
    .app-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        background: #ffffff;
        border-bottom: 1px solid #f1f5f9;
        margin-bottom: 2rem;
    }
    
    /* 헤더 타이틀 폰트(Outfit) 및 스타일 */
    .app-header h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 1.8rem;
        color: #0f172a;
        margin: 0;
    }
    
    /* 헤더 설명 문구 스타일 */
    .app-header p {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }

    /* 사이드바 배경색 및 테두리 설정 */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* 기본 채팅 메시지 컨테이너의 배경과 테두리를 제거하여 더 깔끔하게 만듦 */
    .stChatMessage {
        border: none !important;
        background-color: transparent !important;
        padding: 0.5rem 0 !important;
    }
    
    /* API 키 미입력 시 나타나는 시스템 알림창 스타일 */
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

    /* 오디오 플레이어의 크기를 줄이고 반투명하게 설정하여 디자인 조화 */
    audio {
        height: 30px;
        width: 200px;
        opacity: 0.7;
        transition: opacity 0.3s;
    }
    audio:hover { opacity: 1; }

    /* 채팅 입력창을 둥글게 만들고 그림자 효과 부여 */
    .stChatInputContainer {
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    
    /* 문법 교정(Correction) 및 제안 답변(Suggestions) 섹션의 인용구 스타일 */
    blockquote {
        border-left: 3px solid #6366f1 !important;
        background-color: #f8faff !important;
        padding: 1rem !important;
        border-radius: 0 12px 12px 0;
        color: #1e293b !important;
    }
    </style>
    
    <!-- 실제 화면에 표시될 커스텀 헤더 HTML -->
    <div class="app-header">
        <h1>🎓 My AI Teacher</h1>
        <p>Simple, Modern, and Intelligent English Learning</p>
    </div>
    """, unsafe_allow_html=True)

# [세션 상태 관리] 페이지가 새로고침되어도 데이터가 유지되어야 하는 변수들을 정의합니다.
if "messages" not in st.session_state:
    st.session_state.messages = [] # 대화 내역 저장
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None # Gemini 채팅 세션 유지
if "current_config" not in st.session_state:
    st.session_state.current_config = {"level": None, "topic": None} # 현재 설정된 레벨/주제
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None # 중복 처리 방지를 위한 마지막 오디오 ID

# [사이드바 설정] 사용자로부터 설정을 입력받는 영역입니다.
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # 보안 로직: 먼저 secrets(Streamlit 설정 또는 파일)에 키가 있는지 확인합니다.
    if "GEMINI_API_KEY" in st.secrets:
        st.success("✅ API Key loaded from secrets")
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        # 설정이 없다면 사이드바에서 수동으로 비밀번호 형태로 입력받습니다.
        api_key = st.text_input("Gemini API Key", type="password", help="Enter your key here or set it in secrets.toml")
    
    # 레벨 및 주제 선택 박스
    level = st.selectbox("Your Level", ["초급", "중급", "고급"])
    topic = st.selectbox("Topic", ["자기소개", "여행", "쇼핑", "음식점", "직장생활", "자유대화"])
    
    # AI 답변을 소리로 들을지 선택 (현재는 자동 생성 기능을 위해 체크박스로 활용)
    auto_speak = st.checkbox("Auto-play voice", value=True)
    
    # 새 대화 시작 버튼: 세션 데이터를 초기화합니다.
    if st.button("🔄 Start New Session"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.session_state.current_config = {"level": level, "topic": topic}
        st.rerun()

    st.markdown("---")
    st.caption("v2.1 Secured Edition")

# [텍스트 음성 변환 함수 (TTS)] AI의 답변 중 핵심 영어 문장만 발음하도록 처리합니다.
def text_to_speech(text):
    # 특수 아이콘(💡, 🎯, 🗣️)이 포함되지 않은 첫 번째 유효한 문장만 추출합니다.
    main_text = ""
    for line in text.split('\n'):
        if line.strip() and not any(symbol in line for symbol in ["💡", "🎯", "🗣️"]):
            main_text = line
            break
    
    if not main_text: return None # 음성으로 변환할 내용이 없으면 중단
    
    try:
        # Google TTS(gTTS)를 사용하여 영어 음성 파일 생성
        tts = gTTS(text=main_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except Exception:
        return None

# [API 키 확인] 키가 없으면 앱 진행을 멈추고 안내 메시지를 표시합니다.
if not api_key:
    st.markdown('<div class="system-notification">🔑 Please enter your Gemini API Key in the sidebar to start learning.</div>', unsafe_allow_html=True)
    st.stop()

# Gemini API 구성 설정
genai.configure(api_key=api_key)

# [시스템 프롬프트 생성] 선택한 레벨과 주제에 맞춰 AI의 페르소나를 정의합니다.
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

# [채팅 세션 초기화] 세션이 없거나 설정이 바뀌면 새로 시작합니다.
if st.session_state.chat_session is None or st.session_state.current_config["level"] != level or st.session_state.current_config["topic"] != topic:
    try:
        # 최신 모델 gemini-2.0-flash 사용
        model = genai.GenerativeModel('gemini-2.0-flash')
        st.session_state.chat_session = model.start_chat(history=[])
        # AI 선생님에게 초기 지침을 전달하고 첫 인사를 받습니다.
        response = st.session_state.chat_session.send_message(f"System Instruction: {get_system_prompt(level, topic)}\n\nHello! Start the conversation.")
        st.session_state.messages = [{"role": "assistant", "content": response.text}]
        st.session_state.current_config = {"level": level, "topic": topic}
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

# [대화 이력 로드] 기존에 주고받은 메시지들을 순서대로 화면에 표시합니다.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # AI 답변의 경우 음성 재생 바를 함께 표시합니다.
        if msg["role"] == "assistant":
            audio_fp = text_to_speech(msg["content"])
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

# [입력 UI 영역] 마이크 버튼과 텍스트 입력창을 배치합니다.
st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns([1, 5])
with c1:
    audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="🛑 Stop", key="mic")
with c2:
    text_input = st.chat_input("Say something to your teacher...")

# [입력 데이터 처리 로직]
user_input = None

# 마이크로부터 새로운 음성 데이터가 들어온 경우 처리
if audio:
    audio_id = audio['id'] if 'id' in audio else hash(audio['bytes'])
    if st.session_state.last_processed_audio != audio_id:
        with st.spinner("Analyzing voice..."):
            try:
                # Gemini의 멀티모달 능력을 사용하여 음성을 직접 텍스트로 변환(STT)
                model = genai.GenerativeModel('gemini-2.0-flash')
                res = model.generate_content([{"mime_type": "audio/wav", "data": audio['bytes']}, "Transcribe as English text."])
                user_input = res.text.strip()
                st.session_state.last_processed_audio = audio_id # 처리된 오디오 중복 확인용
            except:
                st.error("Audio error.")

# 음성 입력이 없으면 텍스트 입력창 확인
if not user_input and text_input:
    user_input = text_input

# [답변 생성 및 화면 갱신]
if user_input:
    # 1. 유저 메시지를 히스토리에 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. AI 응답 생성 및 화면 출력
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 이전 대화 맥락이 유지되는 채팅 세션을 통해 답변 수신
            res = st.session_state.chat_session.send_message(user_input)
            st.markdown(res.text)
            
            # 답변 음성 재생 바 생성
            audio_fp = text_to_speech(res.text)
            if audio_fp: st.audio(audio_fp, format="audio/mp3")
            
            # 최종 AI 답변을 히스토리에 저장 후 화면 갱신
            st.session_state.messages.append({"role": "assistant", "content": res.text})
            st.rerun()
