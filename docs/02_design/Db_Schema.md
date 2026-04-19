# DB 스키마 (Database Schema)

## 전체 ERD 개요

```
[games] ──< [game_mechanic] >── [mechanics]
   │                                  │
   │                          [mechanic_hypothesis]
   │                                  │
   ├──< [game_metric] >── [metrics]  [hypotheses]
   │                                  │
   ├──< [game_abtest] >── [ab_tests] [hypothesis_result]
   │                                  │
   ├──< [game_campaign] >── [campaigns] [results]
   │
   ├──< [game_competitor] >── [competitor_games]
   │
   ├──< [game_liveops] >── [live_ops_events]
   │
   ├──< [meeting_game] >── [meetings]
   │
   └──< [team_game] >── [teams] ──< [team_meeting] >── [meetings]
```

---

## 노드 테이블

### games
```sql
CREATE TABLE games (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    genre       VARCHAR(100),
    description TEXT,
    status      VARCHAR(50) DEFAULT 'active',  -- active/archived
    embedding   vector(1536),
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON games USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

**Django Model:**
```python
class Game(models.Model):
    name = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, default='active')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

### mechanics
```sql
CREATE TABLE mechanics (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    category    VARCHAR(100),  -- core/monetization/ux/social
    embedding   vector(1536),
    created_at  TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON mechanics USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

### hypotheses
```sql
CREATE TABLE hypotheses (
    id          SERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    status      VARCHAR(20) DEFAULT 'pending',  -- pending/validated/failed
    created_by  VARCHAR(100),
    embedding   vector(1536),
    created_at  TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON hypotheses USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

### results
```sql
CREATE TABLE results (
    id           SERIAL PRIMARY KEY,
    description  TEXT NOT NULL,
    metric_value DECIMAL(10, 4),
    metric_type  VARCHAR(100),  -- D1/DAU/ARPU/CPI/ROAS/etc
    unit         VARCHAR(50),   -- percent/dollar/count
    validated_at TIMESTAMP,
    embedding    vector(1536),
    created_at   TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON results USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

### metrics
```sql
CREATE TABLE metrics (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    value        DECIMAL(10, 4),
    unit         VARCHAR(50),
    metric_type  VARCHAR(100),  -- D1/D7/D30/DAU/ARPU/Revenue
    period_start DATE,
    period_end   DATE,
    embedding    vector(1536),
    created_at   TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON metrics USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

### ab_tests
```sql
CREATE TABLE ab_tests (
    id                   SERIAL PRIMARY KEY,
    name                 VARCHAR(200) NOT NULL,
    control_description  TEXT,
    variant_description  TEXT,
    metric               VARCHAR(100),
    control_value        DECIMAL(10, 4),
    variant_value        DECIMAL(10, 4),
    confidence           DECIMAL(5, 4),  -- 0.0 ~ 1.0
    result               VARCHAR(20),    -- control_win/variant_win/neutral
    embedding            vector(1536),
    created_at           TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON ab_tests USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

### campaigns
```sql
CREATE TABLE campaigns (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    channel     VARCHAR(100),  -- Meta/Google/TikTok/AppLovin/Unity
    budget_usd  DECIMAL(12, 2),
    cpi         DECIMAL(8, 4),
    roas        DECIMAL(8, 4),
    ctr         DECIMAL(8, 6),
    start_date  DATE,
    end_date    DATE,
    embedding   vector(1536),
    created_at  TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON campaigns USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

### competitor_games
```sql
CREATE TABLE competitor_games (
    id               SERIAL PRIMARY KEY,
    name             VARCHAR(200) NOT NULL,
    developer        VARCHAR(200),
    genre            VARCHAR(100),
    mechanic_summary TEXT,
    strength         TEXT,
    weakness         TEXT,
    monetization     TEXT,
    embedding        vector(1536),
    created_at       TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON competitor_games USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

### live_ops_events
```sql
CREATE TABLE live_ops_events (
    id             SERIAL PRIMARY KEY,
    name           VARCHAR(200) NOT NULL,
    event_type     VARCHAR(100),  -- season/patch/event/feature
    start_date     DATE,
    end_date       DATE,
    result_summary TEXT,
    embedding      vector(1536),
    created_at     TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON live_ops_events USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

### teams
```sql
CREATE TABLE teams (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);
-- 기본 데이터: 기획팀, 개발팀, 아트팀, 마케팅팀, QA팀, 데이터팀
```

---

### meetings
```sql
CREATE TABLE meetings (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200),
    date       DATE,
    domain     VARCHAR(100),  -- 기획/마케팅/라이브옵스/데이터
    transcript TEXT,
    summary    TEXT,
    audio_file VARCHAR(500),  -- 원본 파일 경로
    embedding  vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ON meetings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 엣지 테이블 (관계)

### game_mechanic
```sql
CREATE TABLE game_mechanic (
    game_id     INTEGER REFERENCES games(id) ON DELETE CASCADE,
    mechanic_id INTEGER REFERENCES mechanics(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, mechanic_id)
);
```

### mechanic_hypothesis
```sql
CREATE TABLE mechanic_hypothesis (
    mechanic_id   INTEGER REFERENCES mechanics(id) ON DELETE CASCADE,
    hypothesis_id INTEGER REFERENCES hypotheses(id) ON DELETE CASCADE,
    PRIMARY KEY (mechanic_id, hypothesis_id)
);
```

### hypothesis_result
```sql
CREATE TABLE hypothesis_result (
    hypothesis_id INTEGER REFERENCES hypotheses(id) ON DELETE CASCADE,
    result_id     INTEGER REFERENCES results(id) ON DELETE CASCADE,
    PRIMARY KEY (hypothesis_id, result_id)
);
```

### game_metric
```sql
CREATE TABLE game_metric (
    game_id   INTEGER REFERENCES games(id) ON DELETE CASCADE,
    metric_id INTEGER REFERENCES metrics(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, metric_id)
);
```

### game_abtest
```sql
CREATE TABLE game_abtest (
    game_id    INTEGER REFERENCES games(id) ON DELETE CASCADE,
    abtest_id  INTEGER REFERENCES ab_tests(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, abtest_id)
);
```

### game_campaign
```sql
CREATE TABLE game_campaign (
    game_id     INTEGER REFERENCES games(id) ON DELETE CASCADE,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, campaign_id)
);
```

### game_competitor
```sql
CREATE TABLE game_competitor (
    game_id            INTEGER REFERENCES games(id) ON DELETE CASCADE,
    competitor_game_id INTEGER REFERENCES competitor_games(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, competitor_game_id)
);
```

### game_liveops
```sql
CREATE TABLE game_liveops (
    game_id          INTEGER REFERENCES games(id) ON DELETE CASCADE,
    live_ops_event_id INTEGER REFERENCES live_ops_events(id) ON DELETE CASCADE,
    PRIMARY KEY (game_id, live_ops_event_id)
);
```

### meeting_game
```sql
CREATE TABLE meeting_game (
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    game_id    INTEGER REFERENCES games(id) ON DELETE CASCADE,
    PRIMARY KEY (meeting_id, game_id)
);
```

### team_game
```sql
CREATE TABLE team_game (
    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    role    VARCHAR(100),  -- 기획/개발/마케팅/QA/아트/데이터
    PRIMARY KEY (team_id, game_id)
);
```

### team_meeting
```sql
CREATE TABLE team_meeting (
    team_id    INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    PRIMARY KEY (team_id, meeting_id)
);
```

### mechanic_meeting
```sql
CREATE TABLE mechanic_meeting (
    mechanic_id INTEGER REFERENCES mechanics(id) ON DELETE CASCADE,
    meeting_id  INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    PRIMARY KEY (mechanic_id, meeting_id)
);
```

---

## pgvector 설정

마이그레이션 파일에 아래 포함:
```python
from django.db import migrations

class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS vector;"),
    ]
```

---

## Django ORM 관계 요약

```python
# Game 모델에 ManyToMany 관계 추가
class Game(models.Model):
    mechanics       = models.ManyToManyField('Mechanic', through='GameMechanic')
    metrics         = models.ManyToManyField('Metric', through='GameMetric')
    ab_tests        = models.ManyToManyField('ABTest', through='GameABTest')
    campaigns       = models.ManyToManyField('Campaign', through='GameCampaign')
    competitors     = models.ManyToManyField('CompetitorGame', through='GameCompetitor')
    live_ops_events = models.ManyToManyField('LiveOpsEvent', through='GameLiveOps')
    meetings        = models.ManyToManyField('Meeting', through='MeetingGame')
    teams           = models.ManyToManyField('Team', through='TeamGame')
```
