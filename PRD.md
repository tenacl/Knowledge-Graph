# Product Requirements Document (PRD)

## 프로젝트 개요
Streamlit 커뮤니티 클라우드를 활용하여 사용자가 텍스트를 입력하면 해당 내용을 기반으로 인공지능이 지식 그래프를 생성하는 웹 애플리케이션을 개발한다. 사용자는 여러 AI 모델 중 선택하여 지식 그래프를 생성할 수 있으며, 결과물은 이미지 다운로드 또는 클립보드 복사가 가능하다.

## 주요 기능
### 1. API 키 입력 및 확인
- 첫 화면에서 ChatGPT, Gemini, Claude, DeepSeek API 키 입력 창 제공
- 하나 이상의 API 키 입력 시 다음 화면으로 이동
- 환경변수를 활용하여 API 키 저장

### 2. 지식 그래프 생성
- 텍스트 입력 박스를 제공하여 사용자 입력을 받음
- 선택한 AI 모델을 사용하여 텍스트를 JSON 형태의 지식 그래프 데이터로 변환
- 변환된 데이터를 기반으로 Streamlit에서 지식 그래프 시각화
- 여러 모델을 동시에 선택하면 각각의 그래프를 병렬로 표시

### 3. 사이드바 및 사용자 선택
- 사이드바에 API 키가 입력된 모델만 체크박스로 표시
- 사용자가 체크한 모델만 지식 그래프 생성에 활용
- 여러 모델 선택 시 각 결과를 비교할 수 있도록 배치

### 4. 결과물 저장 및 공유
- 생성된 지식 그래프를 이미지로 다운로드 기능 제공
- 클립보드 복사 기능 추가

## 파일 구조
```
/streamlit_knowledge_graph/
│── app.py  # 메인 스트림릿 앱 파일
│── requirements.txt  # 필요한 패키지 목록
│── .env  # 환경 변수 저장 파일 (API 키 포함)
│── utils/
│   │── api_handler.py  # 각 AI 모델 API 호출 및 데이터 변환 처리
│   │── graph_renderer.py  # 지식 그래프 시각화 처리
│── assets/
│   │── styles.css  # 스타일시트 파일
│── templates/
│   │── index.html  # HTML 템플릿 파일 (선택사항)
│── README.md  # 프로젝트 설명 문서
```

## 기술 스택
- **Backend**: Streamlit, Python
- **Frontend**: Streamlit 내장 UI, Graphviz
- **API 서비스**: OpenAI (ChatGPT), Google Gemini, Anthropic Claude, DeepSeek
- **환경 변수 관리**: python-dotenv

## 실행 방법
1. 프로젝트 클론
```
git clone https://github.com/your-repo/streamlit_knowledge_graph.git
cd streamlit_knowledge_graph
```
2. 가상환경 생성 및 패키지 설치
```
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```
3. 환경 변수 설정 (.env 파일 생성 후 API 키 입력)
```
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
CLAUDE_API_KEY=your_claude_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
```
4. Streamlit 앱 실행
```
streamlit run app.py
```

## 개발 일정
| 날짜 | 작업 내용 |
|------|-----------|
| Week 1 | 프로젝트 구조 설계 및 기본 UI 개발 |
| Week 2 | API 연동 및 지식 그래프 변환 로직 구현 |
| Week 3 | 다중 모델 선택 기능 및 결과 비교 기능 추가 |
| Week 4 | 최종 테스트 및 배포 |

## 향후 개선 사항
- 사용자 인터페이스 개선 (Drag & Drop 기능 추가)
- 그래프 분석 기능 강화
- AI 모델별 결과 비교 및 성능 평가 기능 추가

