from django.db import models
from pgvector.django import VectorField


class Game(models.Model):
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
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Mechanic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    games = models.ManyToManyField(Game, through='GameMechanic', related_name='mechanics')
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Hypothesis(models.Model):
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
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'mechanic')


class MechanicHypothesis(models.Model):
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE)
    hypothesis = models.ForeignKey(Hypothesis, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('mechanic', 'hypothesis')


class GameHypothesis(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    hypothesis = models.ForeignKey(Hypothesis, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'hypothesis')


class HypothesisResult(models.Model):
    hypothesis = models.ForeignKey(Hypothesis, on_delete=models.CASCADE)
    result = models.ForeignKey(Result, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('hypothesis', 'result')


class GameMetric(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'metric')


class GameABTest(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    ab_test = models.ForeignKey(ABTest, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'ab_test')


class GameCampaign(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'campaign')


class GameCompetitor(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    competitor = models.ForeignKey(CompetitorGame, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'competitor')


class GameLiveOps(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    live_ops_event = models.ForeignKey(LiveOpsEvent, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'live_ops_event')


class MeetingGame(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('meeting', 'game')


class TeamGame(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('team', 'game')


class TeamMeeting(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('team', 'meeting')
