# 업로드 유형 명세 (Upload Types)

## 개요

SuperSuit AI는 5가지 데이터 유형을 업로드받아 온톨로지를 축적한다.

**v1 구현 범위 (현재 활성화):**
- 유형 1 회의 음성 — 풀 파이프라인 구현 (CLOVA STT → GPT 엔티티 추출 → 임베딩)

**v2 로드맵 (비활성화, 향후 구현):**
- 유형 2 게임 지표, 유형 3 마케팅 성과, 유형 4 경쟁 리서치, 유형 5 A/B 테스트

---

## 유형 1: 회의 음성 🎙️

### 입력
- 파일 형식: mp3, wav, m4a, webm
- 최대 파일 크기: 100MB
- 추가 입력: 참여 팀 선택 (다중), 회의 날짜, 회의 도메인 (기획/마케팅/라이브옵스/데이터)

### 처리 파이프라인
```
음성 파일 업로드
    ↓
CLOVA Speech API
(NAVER_CLOUD_INVOKE_URL로 전송)
    ↓
한국어 텍스트 변환
    ↓
gpt-5.4-mini Function Calling
(엔티티 추출: Game, Mechanic, Hypothesis, Result, Team)
    ↓
온톨로지 노드/엣지 저장
    ↓
text-embedding-3-small 임베딩 생성
```

### 생성되는 온톨로지 노드
- Meeting, Game, Mechanic, Hypothesis, Team
- 관계: DISCUSSED_IN, HAS_MECHANIC, HAS_HYPOTHESIS, PARTICIPATED_IN

### 브라우저 녹음 지원
- 업로드 화면에서 마이크 버튼으로 직접 녹음 가능
- MediaRecorder API → WebM → 서버 전송

---

## 유형 2: 게임 지표 📊

### 입력
- 파일 형식: CSV, JSON
- 직접 입력: 폼으로 개별 지표 입력 가능
- 추가 입력: 지표 기간 (시작일~종료일), 지표 유형 선택

### CSV 형식 예시
```csv
metric_type,value,unit,period_start,period_end
D1,42,percent,2024-01-01,2024-01-31
D7,18,percent,2024-01-01,2024-01-31
DAU,12000,count,2024-01-15,2024-01-15
ARPU,0.45,dollar,2024-01-01,2024-01-31
```

### 처리 파이프라인
```
CSV/JSON 업로드 또는 직접 입력
    ↓
gpt-5.4-mini 해석
(지표 의미 분석, 비정형 컬럼명 표준화)
    ↓
Metric 노드 생성
    ↓
게임 노드와 HAS_METRIC 관계 연결
    ↓
임베딩 생성
```

### 생성되는 온톨로지 노드
- Metric (D1, D7, D30, DAU, ARPU, Revenue 등)
- 관계: HAS_METRIC (Game → Metric)

---

## 유형 3: 마케팅 성과 📣

### 입력
- 파일 형식: CSV
- 직접 입력: 캠페인명, 채널, CPI, ROAS, CTR, 예산, 집행 기간
- 채널 선택: Meta, Google, TikTok, AppLovin, Unity Ads, 기타

### CSV 형식 예시
```csv
campaign_name,channel,budget_usd,cpi,roas,ctr,start_date,end_date
Snake Q1 UA,Meta,5000,0.8,3.2,0.045,2024-01-01,2024-03-31
Snake TikTok Test,TikTok,1000,1.2,2.1,0.062,2024-02-01,2024-02-28
```

### 처리 파이프라인
```
CSV 업로드 또는 직접 입력
    ↓
gpt-5.4-mini 분석
(성과 해석, 채널 정규화)
    ↓
Campaign 노드 생성
    ↓
게임 노드와 HAS_CAMPAIGN 관계 연결
    ↓
임베딩 생성
```

### 생성되는 온톨로지 노드
- Campaign (채널, CPI, ROAS, CTR 포함)
- 관계: HAS_CAMPAIGN (Game → Campaign)

---

## 유형 4: 경쟁 리서치 🔍

### 입력
- 파일 형식: PDF, TXT, DOCX
- 직접 입력: 텍스트 에디터로 직접 입력
- 추가 입력: 경쟁 게임명

### 입력 텍스트 예시
```
[경쟁 게임: Snake.io]
핵심 메카닉: 뱀 성장 루프, 타 플레이어 충돌
수익화: 광고 위주, 배너/전면 광고
강점: 간단한 조작, 즉각적인 경쟁감
약점: 깊이 있는 콘텐츠 부재, 장기 리텐션 낮음
```

### 처리 파이프라인
```
파일/텍스트 업로드
    ↓
gpt-5.4-mini 분석
(경쟁 게임 정보 구조화: 메카닉, 강점, 약점, 수익화)
    ↓
CompetitorGame 노드 생성
    ↓
우리 게임 노드와 HAS_COMPETITOR 관계 연결
    ↓
임베딩 생성
```

### 생성되는 온톨로지 노드
- CompetitorGame (메카닉 요약, 강점, 약점 포함)
- 관계: HAS_COMPETITOR (Game → CompetitorGame)

---

## 유형 5: A/B 테스트 🧪

### 입력
- 파일 형식: CSV, JSON
- 직접 입력: 테스트명, 가설 연결 (드롭다운), 대조군/실험군 결과
- 추가 입력: 신뢰도(confidence level), 샘플 수

### CSV 형식 예시
```csv
test_name,control,variant,metric,control_value,variant_value,confidence,result
FTUE 길이 테스트,기존 FTUE (3분),단축 FTUE (1분),D1,38,45,0.95,variant_win
배틀패스 가격 테스트,$4.99,$2.99,구매전환율,0.02,0.04,0.90,variant_win
```

### 처리 파이프라인
```
CSV 업로드 또는 직접 입력
    ↓
가설 노드와 연결 (선택 시)
    ↓
ABTest 노드 생성
    ↓
게임 노드와 HAS_ABTEST 관계 연결
    ↓
Hypothesis 노드의 status 업데이트 (validated/failed)
    ↓
임베딩 생성
```

### 생성되는 온톨로지 노드
- ABTest (대조/실험군, 결과, 신뢰도 포함)
- 관계: HAS_ABTEST (Game → ABTest), 기존 Hypothesis.status 업데이트

---

## 공통 처리 흐름

```python
# 모든 유형 공통 처리
def process_upload(game_id, upload_type, data):
    # 1. 텍스트 추출 (유형별)
    text = extract_text(upload_type, data)

    # 2. GPT 엔티티 추출
    entities = gpt_service.extract_entities(text, upload_type)

    # 3. 온톨로지 저장
    nodes, edges = ontology_service.save(game_id, entities)

    # 4. 임베딩 생성
    for node in nodes:
        embedding = gpt_service.embed(node.text)
        node.embedding = embedding
        node.save()

    return nodes, edges
```

---

## GPT Function Calling 스키마 예시

```json
{
  "name": "extract_ontology_entities",
  "description": "텍스트에서 게임 개발 온톨로지 엔티티를 추출합니다",
  "parameters": {
    "type": "object",
    "properties": {
      "nodes": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "type": {"type": "string", "enum": ["Game", "Mechanic", "Hypothesis", "Result", "Team", "Metric"]},
            "name": {"type": "string"},
            "description": {"type": "string"}
          }
        }
      },
      "edges": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "from_name": {"type": "string"},
            "to_name": {"type": "string"},
            "relation": {"type": "string"}
          }
        }
      }
    }
  }
}
```
