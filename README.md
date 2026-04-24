# SuperSuit AI

> "울트론을 만드는 것이 아닌, 아이언맨 수트를 만드는 일"

게임 개발 조직의 집단 지식을 온톨로지로 축적하고, AI로 누구나 접근할 수 있게 만드는 지식 관리 도구.

---

## 핵심 기능

- **5가지 데이터 업로드**: 회의 음성(STT), 게임 지표, 마케팅 성과, 경쟁 리서치, A/B 테스트 → 자동 온톨로지 축적
- **온톨로지 그래프 시각화**: 게임을 중심으로 메카닉, 가설, 결과, 팀이 연결된 지식 그래프
- **자연어 LLM 질문**: "Snake Clash! 메카닉 성공 사례 알려줘" → pgvector 검색 + GPT 응답
- **팀별 관리**: 기획/개발/아트/마케팅/데이터팀 필터링

---

## 로컬 실행 방법

### 1. 사전 준비

- Docker Desktop 설치 및 실행
- Python 3.11+
- OpenAI API 키 (gpt-5.4-mini, text-embedding-3-small)
- Naver Cloud CLOVA Speech API 키 (선택)

### 2. PostgreSQL + pgvector 실행 (Docker)

```bash
docker run -d \
  --name supersuit-db \
  -e POSTGRES_DB=supersuit_ai \
  -e POSTGRES_PASSWORD=password \
  -p 5433:5432 \
  pgvector/pgvector:pg16
```

> **참고:** Mac에 로컬 PostgreSQL이 설치되어 있으면 5432 포트가 충돌합니다. 5433 포트를 사용합니다.

### 3. Python 환경 설정

```bash
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 환경변수 설정 (.env)

```
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5433/supersuit_ai
OPENAI_API_KEY=sk-...
NAVER_CLOUD_API_KEY=...
NAVER_CLOUD_INVOKE_URL=https://clovaspeech-gw.ncloud.com/...
```

### 5. DB 마이그레이션

```bash
python manage.py migrate
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
├── docs/                    # 기획/설계 문서 (10개)
│   ├── 01_product/          # 제품 기획
│   │   ├── Product_Overview.md
│   │   ├── Problem_Definition.md
│   │   ├── User_Flow.md
│   │   └── Feature_Spec.md
│   ├── 02_design/           # 설계
│   │   ├── Ontology_Design.md
│   │   ├── Upload_Types.md
│   │   ├── Db_Schema.md
│   │   └── Ui_Spec.md
│   └── 03_engineering/      # 기술 구현
│       ├── Tech_Stack.md
│       └── Api_Spec.md
├── submission/              # 발표 자료
│   ├── presentation.html    # 슬라이드 발표 자료
│   └── assets/
├── .cursor/agents/          # Subagent 프롬프트
│   ├── product-manager-agent.md
│   ├── product-designer-agent.md
│   ├── fullstack-developer-agent.md
│   └── presentation-agent.md
├── supersuit_ai/            # Django 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
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
├── static/                  # 정적 파일
├── requirements.txt
└── README.md
```

---

## 기획/설계 문서 (docs/)

과제 산출물 문서 10개가 3개 카테고리로 구성되어 있습니다.

### 01_product/ — 제품 기획

| 파일 | 내용 |
|---|---|
| `Product_Overview.md` | 제품명, 철학, 핵심 문제, 대상 사용자, 포지셔닝 |
| `Problem_Definition.md` | 문제 정의, 인터뷰 근거 (바울/솔/네이선), 불편 사항 |
| `User_Flow.md` | 4가지 시나리오별 사용자 이용 흐름 (업로드/질문/탐색/팀관리) |
| `Feature_Spec.md` | 6개 화면별 기능 명세, UI 요소, 사용자 액션, 시스템 동작 |

### 02_design/ — 설계

| 파일 | 내용 |
|---|---|
| `Ontology_Design.md` | 5도메인 온톨로지 구조, 11개 노드/엣지 명세, pgvector 전략 |
| `Upload_Types.md` | 5가지 업로드 유형별 처리 파이프라인 및 GPT Function Calling 스키마 |
| `Db_Schema.md` | 전체 ERD, SQL 테이블 정의, Django ORM 모델, pgvector 인덱스 |
| `Ui_Spec.md` | 디자인 시스템, 색상 팔레트, 화면별 UI 명세, vis.js 설정 |

### 03_engineering/ — 기술 구현

| 파일 | 내용 |
|---|---|
| `Tech_Stack.md` | 기술 선택 근거, 전체 아키텍처, 환경변수 설명 |
| `Api_Spec.md` | 전체 API 엔드포인트 명세 (요청/응답 형식, URL 패턴) |

---

## 기술 스택

| 기술 | 용도 |
|---|---|
| Django 5.2 | 풀스택 웹 프레임워크 |
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
