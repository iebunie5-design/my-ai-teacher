# 🎓 My AI Teacher: 나만의 AI 영어회화 선생님

> **Streamlit**과 **Google Gemini API**를 활용한 고지능 맞춤형 영어 회화 학습 플랫폼입니다.  
> 텍스트는 물론 음성(TTS/STT)을 통해 실제 선생님과 대화하듯 영어를 학습할 수 있습니다.

---

## ✨ 핵심 기능 (Key Features)

### 🎙️ 스마트 음성 대화 (AI Voice)
- **STT (Speech-to-Text)**: 사용자가 마이크로 말하면 Gemini 모델이 음성을 분석하여 영어 텍스트로 변환합니다.
- **TTS (Text-to-Speech)**: AI 선생님이 답변을 자연스러운 원어민 목소리로 읽어주어 리스닝 연습을 돕습니다.

### 🎨 모던 & 프리미엄 UI
- **글래스모피즘(Glassmorphism)** 디자인 적용으로 현대적이고 깔끔한 사용자 경험 제공.
- **모던 메신저 스타일** 인터페이스로 대화의 몰입감을 극대화했습니다.

### 🤖 수준별 & 주제별 맞춤 학습
- **레벨 선택**: 초급(짧고 쉬운 문장), 중급(일상 표현), 고급(관용어 및 복잡 문장) 설정 가능.
- **다양한 주제**: 자기소개, 여행, 쇼핑, 음식점, 직장생활 등 시나리오 기반 학습.

### 💡 실시간 교정 및 가이드
- **문법 교정(Correction)**: 사용자의 사소한 문법 실수(중복 단어, 관사 누락 등)를 실시간으로 교정해 줍니다.
- **예상 답변(Suggested Answers)**: 대화가 막히지 않도록 다음 질문에 대한 답변 예시를 2-3가지 제공합니다.

---

## 🛠️ 기술 스택 (Tech Stack)

- **Frontend/App**: [Streamlit](https://streamlit.io/)
- **AI Model**: [Google Gemini 2.0 Flash](https://aistudio.google.com/)
- **Libraries**: `google-generativeai`, `gTTS`, `streamlit-mic-recorder`

---

## 🚀 빠른 시작 가이드 (Quick Start)

### 1. 저장소 복제 (Clone)
```bash
git clone https://github.com/iebunie5-design/my-ai-teacher.git
cd my-ai-teacher
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 앱 실행
```bash
# 모던 디자인 버전 적극 추천!
streamlit run app_modern.py
```

---

## 🔑 사용 방법

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키를 발급받습니다.
2. 실행된 웹 페이지 왼쪽 사이드바에 API 키를 입력합니다.
3. 자신의 레벨과 주제를 선택한 후 마이크(🎤) 또는 키보드를 사용해 대화를 시작하세요.

---

## 🌐 웹 서비스로 배포하기 (Deploy to Web)

이 저장소의 코드는 **Streamlit Community Cloud**를 통해 무료로 웹에 배포할 수 있습니다.

1. [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 GitHub 로그인을 합니다.
2. **'New app'** 버튼을 클릭하고 이 저장소를 선택합니다.
3. 메인 파일 경로를 `app_modern.py`로 설정하고 **'Deploy'** 버튼을 누릅니다.
4. 배포가 완료되면 부여된 URL을 통해 스마트폰이나 다른 PC에서도 수업을 진행할 수 있습니다.

---

## 📄 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.
