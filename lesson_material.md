# [실습 가이드] Gemini와 Streamlit으로 만드는 '나만의 AI 영어 선생님'

본 강의에서는 최신 거대 언어 모델(LLM)인 **Google Gemini**와 파이썬의 **Streamlit** 라이브러리를 활용하여, 실제 대화가 가능한 AI 영어 학습 서비스를 직접 개발해 봅니다.

---

## 📅 학습 목차
1. **환경 구축**: 필요한 도구 설치 및 API 키 발급
2. **기본 챗봇**: Streamlit과 Gemini 연결하기
3. **음성 기능**: 듣기(TTS)와 말하기(STT) 구현
4. **지능형 로직**: 문법 교정 및 답변 유도 프롬프트 설계
5. **UI 디자인**: CSS를 활용한 앱 스타일링
6. **배포**: 깃허브(GitHub)에 내 프로젝트 올리기

---

## 1. 환경 구축 (Preparation)
- **언어**: Python 3.9+
- **주요 라이브러리**:
  - `streamlit`: 웹 인터페이스 제작
  - `google-generativeai`: Gemini AI 모델 사용
  - `gTTS`: 텍스트를 음성으로 변환(TTS)
  - `streamlit-mic-recorder`: 브라우저 마이크 녹음(STT)

### 💻 설치 명령어
```bash
pip install streamlit google-generativeai gTTS streamlit-mic-recorder
```

---

## 2. 핵심 코드 포인트 (Key Logic)

### 💡 포인트 1: 시스템 프롬프트(System Prompt)의 힘
AI에게 단순한 대답을 넘어 '선생님'의 정체성을 부여하는 과정입니다.
- **역할 부여**: "You are a friendly English teacher."
- **규칙 설정**: "Always provide a correction if there is a mistake."
- **흐름 유지**: "Always end with a follow-up question."

### 🎙️ 포인트 2: 음성 기반 대화
- **듣기(TTS)**: 사용자가 AI의 발음을 듣고 따라 할 수 있게 합니다.
- **말하기(STT)**: Gemini 2.0 Flash 모델의 멀티모달 능력을 활용해 음성 데이터를 직접 텍스트로 변환합니다.

### 🎨 포인트 3: 디자인(CSS) 주입
Streamlit의 한계를 넘는 `st.markdown(..., unsafe_allow_html=True)` 기법을 사용합니다.
- **글래스모피즘**: 세련된 반투명 디자인
- **커스텀 폰트**: Google Fonts 연동

---

## 3. 실습 단계별 소스 코드 구성

| 파일명 | 주요 기능 | 학습 포인트 |
| :--- | :--- | :--- |
| `app.py` | 텍스트 기반 기초 챗봇 | Streamlit 세션 상태(session_state) 이해 |
| `app_voice.py` | 음성 인식 및 발음 출력 | 멀티미디어 데이터 처리 및 STT 로직 |
| `app_modern.py` | 고급 디자인 적용 버전 | CSS 주입 및 사용자 경험(UX) 최적화 |

---

## 4. 도전 과제 (Homework)
- **기능 확장**: 사용자가 배운 표현을 나중에 볼 수 있는 '단어장 저장' 기능을 추가해 보세요.
- **다국어 확장**: 영어뿐만 아니라 일본어, 중국어 선생님 버전으로 바꿔보세요.

---

---

## 🚀 5. 내 앱을 실시간 웹사이트로 만들기 (Deployment)
개발한 프로그램을 내 컴퓨터가 아닌 전 세계 누구나 접속할 수 있도록 온라인에 배포해 봅시다.

### 🌐 Streamlit Community Cloud 활용하기
1. **GitHub 업로드**: 이미 진행한 것처럼 깃허브 저장소에 코드를 최신 상태로 올립니다.
2. **Streamlit Cloud 접속**: [share.streamlit.io](https://share.streamlit.io/)에 접속하여 깃허브 계정으로 로그인합니다.
3. **앱 배포**: 
   - 'Create app' 버튼을 누릅니다.
   - 내 저장소(`my-ai-teacher`)와 브랜치(`main`)를 선택합니다.
   - 메인 파일 경로에 `app_modern.py`를 입력합니다.
4. **결과 확인**: 잠시 후 생성되는 고유 URL(예: `my-ai-teacher.streamlit.app`)을 친구들에게 공유해 보세요!

---
**ⓒ 2026 AI 학습 프로젝트 가이드 - My AI Teacher**
