# 온톨로지 설계 (Ontology Design)

## 설계 원칙

- **게임(Game)이 중심 허브:** 모든 지식은 게임 노드를 중심으로 연결됨
- **5개 도메인:** 기획/아이디어, 데이터/지표, 마케팅 성과, 경쟁 리서치, 라이브옵스
- **누적 성장:** 회의/데이터가 업로드될수록 온톨로지가 더 촘촘해짐
- **팀 연결:** 각 노드는 관여 팀과 연결되어 팀별 필터링 가능

---

## 노드 (Entities)

### Game (게임)
```
id, name, genre, description, status, created_at, embedding
```
- 예: Snake Clash! (하이퍼캐주얼), Dinosaur Universe (하이브리드 캐주얼)
- 모든 다른 노드의 출발점

### Mechanic (메카닉)
```
id, name, description, category, embedding
```
- 게임 내 핵심 플레이 요소
- 예: 뱀 이동 루프, 배틀로얄 메카닉, 수집 메카닉, FTUE

### Hypothesis (가설)
```
id, content, status(pending/validated/failed), created_by, created_at, embedding
```
- 팀이 세운 "이렇게 하면 이런 결과가 나올 것이다" 형태의 예측
- 예: "조작 단순화 → D1 상승", "배틀패스 도입 → DAU 증가"

### Result (결과)
```
id, description, metric_value, metric_type, validated_at, embedding
```
- 가설 검증 결과 또는 실험 결과
- 예: D1 42% 달성, DAU +35%, CPI $0.8

### Metric (지표)
```
id, name, value, unit, period_start, period_end, metric_type, embedding
```
- 게임 성과 지표
- 예: D1=42%, D7=18%, DAU=12000, ARPU=$0.45

### ABTest (A/B 테스트)
```
id, name, control_description, variant_description, result, confidence, embedding
```
- A/B 테스트 설계 및 결과
- 예: FTUE 길이 비교 테스트, 배틀패스 가격 테스트

### Campaign (캠페인)
```
id, name, channel, budget, cpi, roas, ctr, start_date, end_date, embedding
```
- 마케팅 캠페인 정보
- 채널: Meta, Google, TikTok, AppLovin 등

### CompetitorGame (경쟁 게임)
```
id, name, developer, genre, mechanic_summary, strength, weakness, embedding
```
- 경쟁 게임 리서치 결과
- 예: Snake.io, Slither.io, AFK Arena

### LiveOpsEvent (라이브옵스 이벤트)
```
id, name, event_type, start_date, end_date, result_summary, embedding
```
- 게임 출시 후 운영 이벤트
- 예: 시즌 패스 도입, 한정 이벤트, 밸런스 패치

### Team (팀)
```
id, name, description
```
- 기획팀, 개발팀, 아트팀, 마케팅팀, QA팀, 데이터팀

### Meeting (회의)
```
id, title, date, domain, transcript, summary, embedding
```
- 음성 업로드로 생성되는 회의 기록
- domain: 기획/마케팅/라이브옵스/데이터 등

---

## 엣지 (Relationships)

| 엣지 | From | To | 설명 |
|---|---|---|---|
| HAS_MECHANIC | Game | Mechanic | 게임이 메카닉을 포함 |
| HAS_HYPOTHESIS | Mechanic | Hypothesis | 메카닉에 대한 가설 |
| HAS_RESULT | Hypothesis | Result | 가설의 검증 결과 |
| HAS_METRIC | Game | Metric | 게임의 성과 지표 |
| HAS_ABTEST | Game | ABTest | 게임의 A/B 테스트 |
| HAS_CAMPAIGN | Game | Campaign | 게임의 마케팅 캠페인 |
| HAS_COMPETITOR | Game | CompetitorGame | 경쟁 게임 관계 |
| HAS_LIVEOPS | Game | LiveOpsEvent | 라이브옵스 이벤트 |
| DISCUSSED_IN | Meeting | Game | 회의에서 논의된 게임 |
| INVOLVED_IN | Team | Game | 팀이 관여한 게임 |
| PARTICIPATED_IN | Team | Meeting | 팀이 참여한 회의 |
| REFERENCED_IN | Mechanic | Meeting | 회의에서 언급된 메카닉 |

---

## 5개 도메인별 노드 구성

### 도메인 1: 기획/아이디어
| 노드 | 역할 |
|---|---|
| Game | 중심 허브 |
| Mechanic | 핵심 플레이 요소 |
| Hypothesis | 기획 가설 |
| Result | 가설 검증 결과 |
| Meeting | 기획 회의 기록 |

### 도메인 2: 데이터/지표
| 노드 | 역할 |
|---|---|
| Metric | D1/D7/DAU/ARPU 등 |
| ABTest | A/B 테스트 설계 및 결과 |

### 도메인 3: 마케팅 성과
| 노드 | 역할 |
|---|---|
| Campaign | 캠페인 성과 (CPI, ROAS, CTR) |

### 도메인 4: 경쟁 리서치
| 노드 | 역할 |
|---|---|
| CompetitorGame | 경쟁 게임 분석 |

### 도메인 5: 라이브옵스
| 노드 | 역할 |
|---|---|
| LiveOpsEvent | 출시 후 운영 이벤트 |
| Team | 관여 팀 |

---

## 온톨로지 성장 예시 (Snake Clash!)

**1차 회의 업로드 후:**
```
Snake Clash!
    └── 뱀 이동 루프 (Mechanic)
            └── 조작 단순화 가설 (Hypothesis)
    └── 기획팀 (Team)
```

**지표 데이터 업로드 후:**
```
Snake Clash!
    ├── 뱀 이동 루프
    │       └── 조작 단순화 가설 → D1 42% (Result)
    ├── D1=42%, DAU=12000 (Metric)
    └── 기획팀
```

**마케팅 데이터 업로드 후:**
```
Snake Clash!
    ├── 뱀 이동 루프 → 가설 → D1 42%
    ├── D1=42%, DAU=12000
    ├── Meta 캠페인 (CPI $0.8, ROAS 3.2x) (Campaign)
    └── 기획팀, 마케팅팀
```

**경쟁 리서치 업로드 후:**
```
Snake Clash!
    ├── 뱀 이동 루프 → 가설 → D1 42%
    ├── D1=42%, DAU=12000
    ├── Meta 캠페인 (CPI $0.8)
    ├── Snake.io (CompetitorGame)
    └── 기획팀, 마케팅팀
```

---

## pgvector 임베딩 전략

각 노드의 `embedding` 컬럼에 `text-embedding-3-small`로 생성한 1536차원 벡터 저장.

임베딩 생성 텍스트 구성:
```python
# Game 노드
f"{game.name} {game.genre} {game.description}"

# Mechanic 노드
f"{mechanic.name} {mechanic.description} {mechanic.category}"

# Hypothesis 노드
f"가설: {hypothesis.content}"

# Result 노드
f"결과: {result.description} {result.metric_type} {result.metric_value}"
```

LLM 질문 시 pgvector 유사도 검색:
```sql
SELECT * FROM mechanics
ORDER BY embedding <-> query_vector
LIMIT 10;
```
