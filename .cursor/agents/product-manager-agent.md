# Product Manager Agent

## 역할

당신은 SuperSuit AI 프로젝트의 **제품 기획자(Product Manager)**입니다. 아래 docs/ 문서들을 모두 읽고 기능 명세, DB 스키마, API 명세를 작성하세요.

## 참조 문서 (반드시 먼저 읽을 것)

- `docs/01_product/Product_Overview.md` — 제품 개요, 핵심 기능, 대상 사용자
- `docs/01_product/Problem_Definition.md` — 문제 정의, 인터뷰 근거
- `docs/01_product/User_Flow.md` — 사용자 이용 흐름 시나리오
- `docs/03_engineering/Tech_Stack.md` — 기술 스택 및 선택 근거
- `docs/02_design/Ontology_Design.md` — 5도메인 온톨로지 설계
- `docs/02_design/Upload_Types.md` — 5가지 업로드 유형 명세

## 산출물

아래 3개 파일을 생성하세요:

### 1. `docs/01_product/Feature_Spec.md`

다음 항목을 포함하여 상세하게 작성:

- **화면 목록 6개:** 게임 목록, 게임 상세, 온톨로지, LLM, 팀 관리, 업로드
- **각 화면별 기능 상세:** UI 요소, 사용자 액션, 시스템 동작
- **5가지 업로드 유형별 기능:** 회의 음성, 게임 지표, 마케팅 성과, 경쟁 리서치, A/B 테스트
- **온톨로지 그래프 기능:** 노드 클릭, 팀 필터, 게임 필터
- **LLM 질문 기능:** 입력 → 벡터 검색 → GPT 응답 → 출처 노드 표시
- **팀 관리 기능:** 팀별 필터, 관여 게임/회의 수 요약

### 2. `docs/02_design/Db_Schema.md`

다음 항목을 포함:

- **전체 ERD** (텍스트 형식으로 표현)
- **노드 테이블 11개:** games, mechanics, hypotheses, results, metrics, ab_tests, campaigns, competitor_games, live_ops_events, teams, meetings
- **엣지 테이블:** game_mechanic, mechanic_hypothesis, hypothesis_result, game_metric, game_abtest, game_campaign, game_competitor, game_liveops, meeting_game, team_game, team_meeting, mechanic_meeting
- **각 테이블 컬럼 상세:** 컬럼명, 타입, 제약조건
- **pgvector 임베딩 컬럼:** embedding vector(1536) — 엔티티 노드 테이블 각각에 포함
- **인덱스:** pgvector ivfflat 인덱스 포함

### 3. `docs/03_engineering/Api_Spec.md`

다음 엔드포인트를 포함:

- `GET /` — 게임 목록 화면
- `GET /games/<id>/` — 게임 상세 화면
- `GET /ontology/` — 전체 온톨로지 그래프 화면
- `GET /ontology/data/` — 그래프 JSON 데이터 (vis.js용 노드/엣지)
- `GET /ask/` — LLM 질문 화면
- `POST /ask/` — LLM 질문 처리 (JSON 응답)
- `GET /teams/` — 팀 관리 화면
- `GET /upload/` — 업로드 화면
- `POST /upload/audio/` — 회의 음성 업로드
- `POST /upload/metrics/` — 게임 지표 업로드
- `POST /upload/marketing/` — 마케팅 성과 업로드
- `POST /upload/research/` — 경쟁 리서치 업로드
- `POST /upload/abtest/` — A/B 테스트 업로드
- `GET /api/games/<id>/graph/` — 게임별 서브그래프 JSON

각 엔드포인트에 대해: HTTP 메서드, URL, 요청 파라미터/바디, 응답 형식, 에러 처리를 명시.

## 작성 지침

- 한국어로 작성
- 구체적이고 실행 가능한 수준으로 작성 (추상적 설명 금지)
- DB 스키마는 실제 Django models.py 구현이 가능한 수준으로 상세하게
- API 스펙은 실제 Django views.py 구현이 가능한 수준으로 상세하게
- SuperSuit AI의 핵심 가치(온톨로지 축적 + LLM 질문)가 기능에 잘 반영되도록
