# 기술 스택 (Tech Stack)

## 전체 아키텍처

```
[브라우저]
  Django Template + Tailwind CSS + vis.js
        ↓ HTTP
[Django 서버 (Python)]
  Views → Service Layer → Models
        ↓
[PostgreSQL + pgvector]
  온톨로지 노드/엣지 + 벡터 임베딩
        ↓ (Docker)
[외부 API]
  CLOVA Speech (STT)
  OpenAI gpt-5.4-mini (엔티티 추출, LLM 응답)
  OpenAI text-embedding-3-small (벡터 임베딩)
```

---

## 백엔드

### Django (Python)
- **역할:** 풀스택 웹 프레임워크. API 엔드포인트, 비즈니스 로직, 템플릿 렌더링 담당
- **버전:** Django 5.2 LTS
- **선택 이유:** 빠른 프로토타입 개발, ORM으로 PostgreSQL 연동 용이, 별도 프론트엔드 프레임워크 불필요

### 서비스 레이어
- `clova_service.py` — CLOVA Speech API 호출, 음성 파일 → 한국어 텍스트 변환
- `gpt_service.py` — gpt-5.4-mini 엔티티 추출 (Function Calling), LLM 질문 응답
- `ontology_service.py` — 노드/엣지 DB 저장, 벡터 임베딩 생성, 그래프 데이터 조회

---

## 데이터베이스

### PostgreSQL + pgvector
- **역할:** 온톨로지 노드/엣지 저장 + 벡터 유사도 검색
- **pgvector:** PostgreSQL 확장, 각 노드에 1536차원 벡터 임베딩 저장 및 코사인 유사도 검색
- **실행:** Docker (pgvector/pgvector:pg16 공식 이미지)
- **선택 이유:** 별도 벡터 DB 없이 관계형 DB와 벡터 검색을 하나의 DB에서 처리. 온톨로지의 관계형 구조(노드-엣지)와 벡터 검색을 동시에 지원

```bash
docker run -d \
  --name supersuit-db \
  -e POSTGRES_DB=supersuit_ai \
  -e POSTGRES_PASSWORD=password \
  -p 5433:5432 \
  pgvector/pgvector:pg16
```

> **참고:** Mac에 로컬 PostgreSQL이 설치된 경우 5432 포트 충돌 방지를 위해 5433 포트를 사용합니다.

---

## AI 도구

### CLOVA Speech (Naver Cloud)
- **역할:** 음성 파일(mp3, wav) → 한국어 텍스트 변환 (STT)
- **선택 이유:** 한국어 특화 STT. 게임 개발 회의의 한국어 전문 용어(메카닉, D1, ARPU 등) 인식 정확도가 높음
- **API:** `NAVER_CLOUD_INVOKE_URL` + `NAVER_CLOUD_API_KEY`
- **요금:** 월 4시간 무료

### gpt-5.4-mini (OpenAI)
- **역할 1:** 텍스트 → 온톨로지 엔티티 추출 (Function Calling으로 JSON 스키마 강제)
- **역할 2:** 자연어 질문에 온톨로지 컨텍스트 기반 인사이트 응답
- **선택 이유:** 최신 OpenAI 플래그십 미니 모델. 한국어 처리 성능 우수, Function Calling으로 JSON 구조화 정확도 최상, gpt-5.4 대비 비용 효율적
- **가격:** $0.75 / 1M input tokens, $4.50 / 1M output tokens

### text-embedding-3-small (OpenAI)
- **역할:** 각 온톨로지 노드 텍스트 → 1536차원 벡터 변환
- **용도:** pgvector에 저장 후 LLM 질문 시 의미 기반 유사도 검색
- **선택 이유:** OpenAI 임베딩 모델 중 비용 대비 성능 최적. 한국어 임베딩 품질 우수
- **가격:** $0.02 / 1M tokens

---

## 프론트엔드

### Django Template + Tailwind CSS
- **역할:** 서버사이드 렌더링 HTML. 별도 React/Vue 없이 Django에서 직접 HTML 생성
- **Tailwind CSS:** CDN으로 로드, 별도 빌드 과정 없이 모던 UI 구현
- **선택 이유:** 프로토타입 개발 속도 최우선. 풀스택 Django로 단일 코드베이스 유지

### vis.js Network
- **역할:** 온톨로지 그래프 시각화 (게임 목록, 게임 상세, 온톨로지 전체 화면)
- **기능:** 노드/엣지 인터랙티브 그래프, 클릭 이벤트, 드래그, 줌, 필터링
- **연동:** Django View가 JSON으로 노드/엣지 데이터 전달 → vis.js가 렌더링
- **선택 이유:** 순수 JavaScript 라이브러리, CDN으로 즉시 사용, 네트워크 그래프에 특화

### Vanilla JavaScript + fetch API
- **역할:** LLM 채팅 비동기 통신, 업로드 진행 상태 표시, 그래프 이벤트 처리

---

## 환경 변수 (.env)

```
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5433/supersuit_ai
OPENAI_API_KEY=sk-...
NAVER_CLOUD_API_KEY=...
NAVER_CLOUD_INVOKE_URL=https://clovaspeech-gw.ncloud.com/...
```

---

## 기술 선택 근거 요약

| 기술 | 선택 이유 |
|---|---|
| Django 풀스택 | 빠른 프로토타입, 단일 코드베이스 |
| PostgreSQL + pgvector | 관계형 + 벡터 검색 하나의 DB |
| Docker | 환경 재현성, pgvector 설치 간소화 |
| CLOVA Speech | 한국어 STT 최고 정확도 |
| gpt-5.4-mini | 한국어 + JSON 구조화, 비용 효율 |
| text-embedding-3-small | 한국어 임베딩, 비용 최적화 |
| vis.js | 온톨로지 그래프 시각화 특화 |
| Tailwind CSS | CDN 즉시 사용, 모던 UI |
