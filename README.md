# SuperSuit AI

> "울트론을 만드는 것이 아닌, 아이언맨 수트를 만드는 일"

게임 개발 조직의 집단 지식을 온톨로지로 축적하고, AI로 누구나 접근할 수 있게 만드는 지식 관리 도구.

---

## 핵심 기능

- **5가지 데이터 업로드**: 회의 음성(STT), 게임 지표, 마케팅 성과, 경쟁 리서치, A/B 테스트 → 자동 온톨로지 축적
- **온톨로지 그래프 시각화**: 게임을 중심으로 메카닉, 가설, 결과, 팀이 연결된 지식 그래프
- **자연어 LLM 질문**: "뱀 메카닉 성공 사례 알려줘" → pgvector 검색 + GPT 응답
- **팀별 관리**: 기획/개발/아트/마케팅/데이터팀 필터링

---

## 로컬 실행 방법

### 1. 사전 준비

- Docker Desktop 설치 및 실행
- Python 3.9+
- OpenAI API 키 (gpt-5.4-mini, text-embedding-3-small)
- Naver Cloud CLOVA Speech API 키 (선택)

### 2. PostgreSQL + pgvector 실행 (Docker)

```bash
docker run -d \
  --name supersuit-db \
  -e POSTGRES_DB=supersuit_ai \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

### 3. Python 환경 설정

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 환경변수 설정 (.env)

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/supersuit_ai
OPENAI_API_KEY=sk-...
NAVER_CLOUD_API_KEY=...
NAVER_CLOUD_INVOKE_URL=https://clovaspeech-gw.ncloud.com/...
```

### 5. DB 마이그레이션 및 샘플 데이터

```bash
python manage.py migrate
python manage.py loaddata fixtures/sample_data.json
```

### 6. 서버 실행

```bash
python manage.py runserver
```

→ http://localhost:8000 접속

---

## 프로젝트 구조

```
supercent_assessment_prototype/
├── docs/                    # 기획/설계 문서 (9개)
│   ├── Product_Overview.md
│   ├── Problem_Definition.md
│   ├── User_Flow.md
│   ├── Tech_Stack.md
│   ├── Ontology_Design.md
│   ├── Upload_Types.md
│   ├── Feature_Spec.md
│   ├── Db_Schema.md
│   ├── Api_Spec.md
│   └── Ui_Spec.md
├── mockups/                 # HTML/CSS 목업 (6개 화면)
│   ├── 01_game_list.html
│   ├── 02_game_detail.html
│   ├── 03_ontology.html
│   ├── 04_llm.html
│   ├── 05_team.html
│   └── 06_upload.html
├── .cursor/agents/          # Subagent 프롬프트
│   ├── product-manager-agent.md
│   ├── product-designer-agent.md
│   └── fullstack-developer-agent.md
├── core/                    # Django 앱
│   ├── models.py            # 온톨로지 DB 모델 (11개 노드 + 관계)
│   ├── views.py             # 화면 + API 뷰
│   ├── urls.py              # URL 라우팅
│   ├── services/
│   │   ├── clova_service.py # CLOVA Speech STT
│   │   ├── gpt_service.py   # GPT 엔티티추출 + LLM + 임베딩
│   │   └── ontology_service.py # 온톨로지 저장/조회/검색
│   └── migrations/
├── templates/               # Django 템플릿 (Tailwind + vis.js)
│   ├── base.html
│   ├── game_list.html
│   ├── game_detail.html
│   ├── ontology.html
│   ├── ask.html
│   ├── teams.html
│   └── upload.html
├── fixtures/
│   └── sample_data.json     # Snake Clash!, Dinosaur Universe 샘플
├── requirements.txt
└── README.md
```

---

## 기술 스택

| 기술 | 용도 |
|---|---|
| Django 4.2 | 풀스택 웹 프레임워크 |
| PostgreSQL + pgvector | 온톨로지 DB + 벡터 유사도 검색 |
| Docker | pgvector DB 실행 |
| CLOVA Speech | 한국어 음성 STT |
| gpt-5.4-mini | 엔티티 추출 + LLM 응답 |
| text-embedding-3-small | 노드 벡터 임베딩 |
| vis.js | 온톨로지 그래프 시각화 |
| Tailwind CSS | 모던 UI |

---

## 화면 구성

| 화면 | URL | 설명 |
|---|---|---|
| 게임 목록 | `/` | 게임 카드 그리드, 새 게임 추가 |
| 게임 상세 | `/games/<id>/` | vis.js 서브그래프 + 메카닉/가설/회의 |
| 온톨로지 | `/ontology/` | 전체 지식 그래프 (게임/팀 필터) |
| LLM 질문 | `/ask/` | 자연어 질문 → 온톨로지 기반 인사이트 |
| 팀 관리 | `/teams/` | 팀별 관여 게임/회의 통계 |
| 업로드 | `/upload/` | 5가지 유형 데이터 업로드 |

---

## Cursor Subagent 방법론

이 프로젝트는 Cursor Subagents를 활용한 AI 협업 개발 방법론으로 구현되었습니다:

1. **Product Manager Agent** → Feature_Spec, Db_Schema, Api_Spec 작성
2. **Product Designer Agent** → 6개 HTML/CSS 목업 + Ui_Spec 작성
3. **Fullstack Developer Agent** → Django 풀스택 구현

각 Agent 프롬프트는 `.cursor/agents/` 폴더에 있습니다.
