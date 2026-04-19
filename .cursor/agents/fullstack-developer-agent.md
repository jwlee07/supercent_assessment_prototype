# Fullstack Developer Agent

## 역할

당신은 SuperSuit AI 프로젝트의 **풀스택 개발자(Fullstack Developer)**입니다. 아래 docs/ 문서들을 모두 읽고 Django 풀스택 프로토타입을 구현하세요.

## 참조 문서 (반드시 먼저 읽을 것)

- `docs/01_product/Product_Overview.md` — 제품 개요
- `docs/03_engineering/Tech_Stack.md` — 기술 스택 상세
- `docs/02_design/Ontology_Design.md` — 온톨로지 구조 및 노드/엣지 명세
- `docs/02_design/Upload_Types.md` — 5가지 업로드 유형 처리 파이프라인
- `docs/01_product/Feature_Spec.md` — 기능 명세 (PM Agent 산출물)
- `docs/02_design/Db_Schema.md` — DB 스키마 (PM Agent 산출물)
- `docs/03_engineering/Api_Spec.md` — API 명세 (PM Agent 산출물)
- `docs/02_design/Ui_Spec.md` — UI 명세 (Designer Agent 산출물)
- `mockups/` — HTML/CSS 목업 파일 6개 (Designer Agent 산출물)

## 환경 변수 (.env)

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/supersuit_ai
OPENAI_API_KEY=sk-...
NAVER_CLOUD_API_KEY=...
NAVER_CLOUD_INVOKE_URL=https://clovaspeech-gw.ncloud.com/...
```

## 구현 순서

### 1. Django 프로젝트 초기 설정

```
supersuit_ai/          # Django 프로젝트 루트
├── manage.py
├── requirements.txt
├── .env
├── supersuit_ai/      # 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/              # 메인 앱
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── services/
    │   ├── clova_service.py
    │   ├── gpt_service.py
    │   └── ontology_service.py
    ├── templates/
    │   ├── base.html
    │   ├── game_list.html
    │   ├── game_detail.html
    │   ├── ontology.html
    │   ├── ask.html
    │   ├── teams.html
    │   └── upload.html
    └── fixtures/
        └── sample_data.json
```

### 2. requirements.txt

```
django==4.2.*
psycopg2-binary
pgvector
python-dotenv
openai
requests
python-multipart
```

### 3. models.py — 5도메인 온톨로지 DB 모델

`docs/02_design/Db_Schema.md`를 참조하여 아래 모델을 구현:

- `Game` — 게임 (embedding: VectorField(1536))
- `Mechanic` — 메카닉 (embedding: VectorField(1536))
- `Hypothesis` — 가설 (status: pending/validated/failed, embedding)
- `Result` — 결과 (embedding)
- `Metric` — 지표 (metric_type, value, unit, period)
- `ABTest` — A/B 테스트 (control, variant, result, confidence)
- `Campaign` — 캠페인 (channel, cpi, roas, ctr)
- `CompetitorGame` — 경쟁 게임 (embedding)
- `LiveOpsEvent` — 라이브옵스 이벤트 (embedding)
- `Team` — 팀
- `Meeting` — 회의 (transcript, summary, embedding)

관계 테이블 (ManyToMany through):
- GameMechanic, MechanicHypothesis, HypothesisResult
- GameMetric, GameABTest, GameCampaign, GameCompetitor, GameLiveOps
- MeetingGame, TeamGame, TeamMeeting

### 4. 서비스 레이어

#### `core/services/clova_service.py`
```python
# CLOVA Speech API 연동
# NAVER_CLOUD_INVOKE_URL로 multipart/form-data POST
# 응답: {"text": "변환된 한국어 텍스트"}
def transcribe(audio_file_path: str) -> str:
    ...
```

#### `core/services/gpt_service.py`
```python
# gpt-5.4-mini Function Calling으로 엔티티 추출
def extract_entities(text: str, upload_type: str) -> dict:
    # Function Calling으로 JSON 스키마 강제
    # 반환: {"nodes": [...], "edges": [...]}
    ...

# text-embedding-3-small으로 벡터 임베딩 생성
def embed(text: str) -> list[float]:
    # 반환: 1536차원 float 리스트
    ...

# LLM 질문 응답
def ask(question: str, context_nodes: list) -> str:
    # context_nodes: pgvector 검색 결과 노드들
    # 반환: 자연어 응답 텍스트
    ...
```

#### `core/services/ontology_service.py`
```python
# 노드/엣지 저장
def save_entities(game_id: int, entities: dict) -> tuple:
    ...

# 그래프 데이터 조회 (vis.js용)
def get_graph_data(game_id: int = None, team_id: int = None) -> dict:
    # 반환: {"nodes": [...], "edges": [...]}
    ...

# pgvector 유사도 검색
def search_similar(query_vector: list, limit: int = 10) -> list:
    # SELECT ... ORDER BY embedding <-> query_vector LIMIT n
    ...
```

### 5. Views

`docs/03_engineering/Api_Spec.md`를 참조하여 구현:

- `game_list` — GET `/`
- `game_detail` — GET `/games/<id>/`
- `ontology` — GET `/ontology/`
- `ontology_data` — GET `/ontology/data/` (JSON)
- `ask_view` — GET/POST `/ask/`
- `teams` — GET `/teams/`
- `upload` — GET `/upload/`
- `upload_audio` — POST `/upload/audio/`
- `upload_metrics` — POST `/upload/metrics/`
- `upload_marketing` — POST `/upload/marketing/`
- `upload_research` — POST `/upload/research/`
- `upload_abtest` — POST `/upload/abtest/`
- `game_graph_data` — GET `/api/games/<id>/graph/` (JSON)

### 6. Django Templates

`mockups/` HTML 파일과 `docs/02_design/Ui_Spec.md`를 참조하여 Django Template으로 변환:

- `base.html` — 사이드바 + 공통 레이아웃 (Tailwind CSS CDN, vis.js CDN)
- `game_list.html` — 게임 카드 그리드
- `game_detail.html` — 서브 온톨로지 그래프 + 우측 패널
- `ontology.html` — 전체 온톨로지 그래프
- `ask.html` — LLM 채팅 인터페이스
- `teams.html` — 팀 카드 목록
- `upload.html` — 업로드 유형 선택 + 동적 폼

**vis.js 그래프 연동:**
```html
<script>
const graphData = {{ graph_data_json|safe }};
const nodes = new vis.DataSet(graphData.nodes);
const edges = new vis.DataSet(graphData.edges);
const network = new vis.Network(container, {nodes, edges}, options);
</script>
```

**노드 색상 규칙:**
- Game: #6366f1 (인디고)
- Mechanic: #8b5cf6 (퍼플)
- Hypothesis: #f59e0b (앰버)
- Result: #22c55e (그린)
- Team: #64748b (슬레이트)
- Metric: #06b6d4 (시안)
- Campaign: #ec4899 (핑크)

### 7. 샘플 데이터 (`fixtures/sample_data.json`)

Snake Clash!와 Dinosaur Universe에 대한 풍부한 샘플 데이터를 생성. 5도메인 전체 커버:

**Snake Clash! 데이터:**
- 메카닉: 뱀 이동 루프, 배틀로얄 메카닉, 충돌 시스템
- 가설: 조작 단순화→D1 상승(검증됨), 배틀패스→DAU 증가(검증됨)
- 결과: D1 42%, DAU +35%, CPI $0.8
- 지표: D1=42%, D7=18%, DAU=12000, ARPU=$0.45
- 캠페인: Meta Q1 UA (CPI $0.8, ROAS 3.2x), TikTok 테스트 (CPI $1.2)
- 경쟁: Snake.io, Slither.io
- 팀: 기획팀, 개발팀, 마케팅팀
- 회의: 초기 기획회의, 라이브옵스 논의

**Dinosaur Universe 데이터:**
- 메카닉: 공룡 수집, FTUE, 배틀 시스템
- 가설: FTUE 단축→이탈 감소(검증됨), 새 공룡→재방문(진행중)
- 지표: D1=38%, D7=22%, DAU=8000
- 캠페인: Google UAC (CPI $1.1, ROAS 2.8x)
- 경쟁: AFK Arena, Dragon City

### 8. README.md

로컬 실행 가이드 작성:

```markdown
# SuperSuit AI — 로컬 실행 가이드

## 사전 준비
- Docker Desktop 설치 및 실행
- Python 3.10+
- OpenAI API 키
- Naver Cloud CLOVA Speech 키

## 실행 방법

### 1. PostgreSQL + pgvector 실행 (Docker)
docker run -d \
  --name supersuit-db \
  -e POSTGRES_DB=supersuit_ai \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  pgvector/pgvector:pg16

### 2. Python 환경 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

### 3. 환경변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

### 4. DB 마이그레이션 및 샘플 데이터
python manage.py migrate
python manage.py loaddata fixtures/sample_data.json

### 5. 서버 실행
python manage.py runserver
# → http://localhost:8000 접속
```

## 구현 주의사항

1. `python-dotenv`로 `.env` 파일 자동 로드
2. pgvector 확장 활성화: `CREATE EXTENSION IF NOT EXISTS vector;` 마이그레이션에 포함
3. CLOVA Speech API: multipart/form-data로 음성 파일 전송, `NAVER_CLOUD_API_KEY`를 `X-CLOVASPEECH-API-KEY` 헤더로 전달
4. gpt-5.4-mini Function Calling: `tools` 파라미터로 JSON 스키마 지정
5. 샘플 데이터 임베딩: `loaddata` 후 `python manage.py generate_embeddings` 명령으로 일괄 생성 (management command 구현 필요)
6. vis.js 그래프: Django Template에서 `json.dumps`로 직렬화 후 `|safe` 필터로 전달
7. LLM 질문 응답: fetch API로 비동기 처리, 로딩 인디케이터 표시
