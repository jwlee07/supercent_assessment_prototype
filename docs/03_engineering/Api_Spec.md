# API 명세 (API Specification)

## 공통

- Base URL: `http://localhost:8000`
- 인증: 없음 (프로토타입)
- 응답 형식: HTML (화면 렌더링) 또는 JSON (API 엔드포인트)
- 에러 응답 형식: `{"error": "에러 메시지"}`

---

## 화면 엔드포인트 (HTML 응답)

### GET `/`
게임 목록 화면

**응답:** `game_list.html` 렌더링

**컨텍스트:**
```python
{
    "games": [
        {
            "id": 1,
            "name": "Snake Clash!",
            "genre": "하이퍼캐주얼",
            "mechanic_count": 3,
            "meeting_count": 5,
            "hypothesis_count": 2
        }
    ]
}
```

---

### GET `/games/<int:game_id>/`
게임 상세 화면

**응답:** `game_detail.html` 렌더링

**컨텍스트:**
```python
{
    "game": {...},
    "mechanics": [...],
    "teams": [...],
    "hypotheses": [...],  # status 포함
    "meetings": [...],
    "graph_data_json": '{"nodes": [...], "edges": [...]}'  # vis.js용
}
```

---

### GET `/ontology/`
전체 온톨로지 그래프 화면

**응답:** `ontology.html` 렌더링

**컨텍스트:**
```python
{
    "games": [...],   # 필터 드롭다운용
    "teams": [...]    # 필터 드롭다운용
}
```

---

### GET `/ask/`
LLM 질문 화면

**응답:** `ask.html` 렌더링

---

### GET `/teams/`
팀 관리 화면

**응답:** `teams.html` 렌더링

**컨텍스트:**
```python
{
    "teams": [
        {
            "id": 1,
            "name": "기획팀",
            "game_count": 2,
            "meeting_count": 5
        }
    ]
}
```

---

### GET `/upload/`
업로드 화면

**응답:** `upload.html` 렌더링

**컨텍스트:**
```python
{
    "games": [...],       # 게임 선택 드롭다운용
    "teams": [...],       # 참여 팀 선택용
    "hypotheses": [...]   # A/B 테스트 연결 가설용
}
```

---

## API 엔드포인트 (JSON 응답)

### GET `/ontology/data/`
전체 온톨로지 그래프 JSON 데이터 (vis.js용)

**쿼리 파라미터:**
- `game_id` (선택): 특정 게임 필터
- `team_id` (선택): 특정 팀 필터

**응답:**
```json
{
    "nodes": [
        {
            "id": "game_1",
            "label": "Snake Clash!",
            "type": "game",
            "color": "#6366f1",
            "size": 30
        },
        {
            "id": "mechanic_5",
            "label": "뱀 이동 루프",
            "type": "mechanic",
            "color": "#8b5cf6",
            "size": 20
        }
    ],
    "edges": [
        {
            "from": "game_1",
            "to": "mechanic_5",
            "label": "HAS_MECHANIC"
        }
    ]
}
```

---

### GET `/api/games/<int:game_id>/graph/`
게임별 서브그래프 JSON

**응답:** 위 `/ontology/data/`와 동일한 형식, 해당 게임 관련 노드/엣지만 포함

---

### POST `/ask/`
LLM 질문 처리

**요청 (JSON):**
```json
{
    "question": "뱀 메카닉 성공 사례 알려줘"
}
```

**처리 과정:**
1. 질문 → text-embedding-3-small → 벡터 변환
2. 모든 노드 테이블에서 pgvector 유사도 검색 (상위 10개)
3. 연결 노드 JOIN 조회
4. gpt-5.4-mini 응답 생성

**응답 (JSON):**
```json
{
    "answer": "Snake Clash!에서 뱀 이동 루프 메카닉을 단순화한 결과 D1 42%를 달성했습니다...",
    "referenced_nodes": [
        {"type": "game", "id": 1, "name": "Snake Clash!"},
        {"type": "mechanic", "id": 5, "name": "뱀 이동 루프"},
        {"type": "result", "id": 3, "name": "D1 42% 달성"}
    ]
}
```

**에러 응답:**
```json
{"error": "질문을 입력해주세요."}
```

---

### POST `/upload/audio/`
회의 음성 업로드

**요청 (multipart/form-data):**
```
game_id: 1
audio_file: <binary>
teams: [1, 2]          # 참여 팀 ID 목록
meeting_date: "2024-01-15"
domain: "기획"
```

**처리 과정:**
1. 음성 파일 서버 저장
2. CLOVA Speech API → 텍스트 변환
3. gpt-5.4-mini Function Calling → 엔티티 추출
4. 온톨로지 노드/엣지 저장
5. text-embedding-3-small → 임베딩 생성

**응답 (JSON):**
```json
{
    "success": true,
    "meeting_id": 12,
    "nodes_created": 5,
    "edges_created": 4,
    "transcript_preview": "오늘 Snake Clash! 기획팀 회의에서..."
}
```

---

### POST `/upload/metrics/`
게임 지표 업로드

**요청 (multipart/form-data):**
```
game_id: 1
file: <CSV/JSON binary>   # 선택 (직접 입력 시 생략)
metrics_data: {...}        # 직접 입력 시 JSON
period_start: "2024-01-01"
period_end: "2024-01-31"
```

**응답 (JSON):**
```json
{
    "success": true,
    "nodes_created": 4,
    "metrics": ["D1=42%", "D7=18%", "DAU=12000", "ARPU=$0.45"]
}
```

---

### POST `/upload/marketing/`
마케팅 성과 업로드

**요청 (multipart/form-data):**
```
game_id: 1
file: <CSV binary>    # 선택
campaign_name: "Snake Q1 UA"
channel: "Meta"
budget_usd: 5000
cpi: 0.8
roas: 3.2
ctr: 0.045
start_date: "2024-01-01"
end_date: "2024-03-31"
```

**응답 (JSON):**
```json
{
    "success": true,
    "campaign_id": 3,
    "nodes_created": 1
}
```

---

### POST `/upload/research/`
경쟁 리서치 업로드

**요청 (multipart/form-data):**
```
game_id: 1
file: <PDF/TXT binary>   # 선택
text_content: "..."       # 직접 입력 시
competitor_name: "Snake.io"
```

**응답 (JSON):**
```json
{
    "success": true,
    "competitor_id": 2,
    "nodes_created": 1
}
```

---

### POST `/upload/abtest/`
A/B 테스트 업로드

**요청 (multipart/form-data):**
```
game_id: 1
file: <CSV binary>          # 선택
test_name: "FTUE 길이 테스트"
control_description: "기존 FTUE (3분)"
variant_description: "단축 FTUE (1분)"
metric: "D1"
control_value: 38
variant_value: 45
confidence: 0.95
result: "variant_win"
hypothesis_id: 3            # 연결 가설 (선택)
```

**응답 (JSON):**
```json
{
    "success": true,
    "abtest_id": 4,
    "nodes_created": 1,
    "hypothesis_updated": true
}
```

---

## 에러 코드

| 코드 | 상황 |
|---|---|
| 400 | 필수 파라미터 누락, 잘못된 파일 형식 |
| 404 | game_id, team_id 등 존재하지 않는 ID |
| 500 | CLOVA API 오류, OpenAI API 오류, DB 오류 |

---

## Django URL 패턴

```python
# core/urls.py
urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
    path('ontology/', views.ontology, name='ontology'),
    path('ontology/data/', views.ontology_data, name='ontology_data'),
    path('ask/', views.ask_view, name='ask'),
    path('teams/', views.teams, name='teams'),
    path('upload/', views.upload, name='upload'),
    path('upload/audio/', views.upload_audio, name='upload_audio'),
    path('upload/metrics/', views.upload_metrics, name='upload_metrics'),
    path('upload/marketing/', views.upload_marketing, name='upload_marketing'),
    path('upload/research/', views.upload_research, name='upload_research'),
    path('upload/abtest/', views.upload_abtest, name='upload_abtest'),
    path('api/games/<int:game_id>/graph/', views.game_graph_data, name='game_graph_data'),
]
```
