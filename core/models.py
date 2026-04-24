from django.db import models
from pgvector.django import VectorField


class Game(models.Model):
    """게임 타이틀 노드. 온톨로지의 중심 엔티티."""
    name = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, default='active')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Team(models.Model):
    """팀 노드. 기획/개발/아트/마케팅 등 조직 단위."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Mechanic(models.Model):
    """게임 메카닉 노드. 핵심 루프, 시스템 등 게임플레이 구성 요소."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    games = models.ManyToManyField(Game, through='GameMechanic', related_name='mechanics')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Hypothesis(models.Model):
    """가설 노드. 메카닉에 대한 기획 가설과 검증 상태(pending/validated/failed)."""
    STATUS_CHOICES = [
        ('pending', '진행중'),
        ('validated', '검증됨'),
        ('failed', '실패'),
    ]
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.CharField(max_length=100, blank=True)
    mechanics = models.ManyToManyField(Mechanic, through='MechanicHypothesis', related_name='hypotheses')
    games = models.ManyToManyField(Game, through='GameHypothesis', related_name='hypotheses')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:80]


class Result(models.Model):
    """실험 결과 노드. 가설 검증 수치와 설명을 저장."""
    description = models.TextField()
    metric_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    metric_type = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    hypotheses = models.ManyToManyField(Hypothesis, through='HypothesisResult', related_name='results')
    validated_at = models.DateTimeField(null=True, blank=True)
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description[:80]


class Metric(models.Model):
    """게임 지표 노드. D1/D7 리텐션, ARPU 등 인게임 수치."""
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    metric_type = models.CharField(max_length=100, blank=True)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    games = models.ManyToManyField(Game, through='GameMetric', related_name='metrics')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}: {self.value}{self.unit}"


class ABTest(models.Model):
    """A/B 테스트 노드. 대조군/실험군 수치와 통계적 유의성을 기록."""
    RESULT_CHOICES = [
        ('control_win', '대조군 우세'),
        ('variant_win', '실험군 우세'),
        ('neutral', '차이 없음'),
    ]
    name = models.CharField(max_length=200)
    control_description = models.TextField(blank=True)
    variant_description = models.TextField(blank=True)
    metric = models.CharField(max_length=100, blank=True)
    control_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    variant_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, blank=True)
    games = models.ManyToManyField(Game, through='GameABTest', related_name='ab_tests')
    hypothesis = models.ForeignKey(Hypothesis, null=True, blank=True, on_delete=models.SET_NULL, related_name='ab_tests')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    """마케팅 캠페인 노드. 채널별 예산, CPI, ROAS 등 광고 성과를 저장."""
    name = models.CharField(max_length=200)
    channel = models.CharField(max_length=100, blank=True)
    budget_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cpi = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    roas = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    ctr = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    games = models.ManyToManyField(Game, through='GameCampaign', related_name='campaigns')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CompetitorGame(models.Model):
    """경쟁작 노드. 장르, 메카닉 요약, 강/약점 및 수익화 방식을 기록."""
    name = models.CharField(max_length=200)
    developer = models.CharField(max_length=200, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    mechanic_summary = models.TextField(blank=True)
    strength = models.TextField(blank=True)
    weakness = models.TextField(blank=True)
    monetization = models.TextField(blank=True)
    games = models.ManyToManyField(Game, through='GameCompetitor', related_name='competitors')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LiveOpsEvent(models.Model):
    """라이브 옵스 이벤트 노드. 이벤트 유형, 기간, 결과 요약을 저장."""
    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    result_summary = models.TextField(blank=True)
    games = models.ManyToManyField(Game, through='GameLiveOps', related_name='live_ops_events')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Meeting(models.Model):
    """회의 노드. 회의록·오디오 원문을 연결하는 컨텍스트 단위."""
    title = models.CharField(max_length=200, blank=True)
    date = models.DateField(null=True, blank=True)
    domain = models.CharField(max_length=100, blank=True)
    transcript = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    audio_file = models.CharField(max_length=500, blank=True)
    games = models.ManyToManyField(Game, through='MeetingGame', related_name='meetings')
    teams = models.ManyToManyField(Team, through='TeamMeeting', related_name='meetings')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"회의 {self.date}"


# ───── 관계(Through) 테이블 ─────

class GameMechanic(models.Model):
    """Game ↔ Mechanic 다대다 관계 테이블."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'mechanic')


class MechanicHypothesis(models.Model):
    """Mechanic ↔ Hypothesis 다대다 관계 테이블."""
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE)
    hypothesis = models.ForeignKey(Hypothesis, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('mechanic', 'hypothesis')


class GameHypothesis(models.Model):
    """Game ↔ Hypothesis 다대다 관계 테이블."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    hypothesis = models.ForeignKey(Hypothesis, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'hypothesis')


class HypothesisResult(models.Model):
    """Hypothesis ↔ Result 다대다 관계 테이블."""
    hypothesis = models.ForeignKey(Hypothesis, on_delete=models.CASCADE)
    result = models.ForeignKey(Result, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('hypothesis', 'result')


class GameMetric(models.Model):
    """Game ↔ Metric 다대다 관계 테이블."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'metric')


class GameABTest(models.Model):
    """Game ↔ ABTest 다대다 관계 테이블."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    ab_test = models.ForeignKey(ABTest, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'ab_test')


class GameCampaign(models.Model):
    """Game ↔ Campaign 다대다 관계 테이블."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'campaign')


class GameCompetitor(models.Model):
    """Game ↔ CompetitorGame 다대다 관계 테이블."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    competitor = models.ForeignKey(CompetitorGame, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'competitor')


class GameLiveOps(models.Model):
    """Game ↔ LiveOpsEvent 다대다 관계 테이블."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    live_ops_event = models.ForeignKey(LiveOpsEvent, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'live_ops_event')


class MeetingGame(models.Model):
    """Meeting ↔ Game 다대다 관계 테이블."""
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('meeting', 'game')


class TeamGame(models.Model):
    """Team ↔ Game 다대다 관계 테이블. 팀의 역할(role) 포함."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('team', 'game')


class TeamMeeting(models.Model):
    """Team ↔ Meeting 다대다 관계 테이블."""
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'meeting')
