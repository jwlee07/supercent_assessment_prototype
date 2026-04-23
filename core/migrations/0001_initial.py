from django.db import migrations, models
import django.db.models.deletion
import pgvector.django


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS vector;"),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('genre', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(default='active', max_length=50)),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Mechanic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('category', models.CharField(blank=True, max_length=100)),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hypothesis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('pending', '진행중'), ('validated', '검증됨'), ('failed', '실패')], default='pending', max_length=20)),
                ('created_by', models.CharField(blank=True, max_length=100)),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('metric_value', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('metric_type', models.CharField(blank=True, max_length=100)),
                ('unit', models.CharField(blank=True, max_length=50)),
                ('validated_at', models.DateTimeField(blank=True, null=True)),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('unit', models.CharField(blank=True, max_length=50)),
                ('metric_type', models.CharField(blank=True, max_length=100)),
                ('period_start', models.DateField(blank=True, null=True)),
                ('period_end', models.DateField(blank=True, null=True)),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ABTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('control_description', models.TextField(blank=True)),
                ('variant_description', models.TextField(blank=True)),
                ('metric', models.CharField(blank=True, max_length=100)),
                ('control_value', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('variant_value', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('confidence', models.DecimalField(blank=True, decimal_places=4, max_digits=5, null=True)),
                ('result', models.CharField(blank=True, choices=[('control_win', '대조군 우세'), ('variant_win', '실험군 우세'), ('neutral', '차이 없음')], max_length=20)),
                ('hypothesis', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ab_tests', to='core.hypothesis')),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('channel', models.CharField(blank=True, max_length=100)),
                ('budget_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('cpi', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('roas', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('ctr', models.DecimalField(blank=True, decimal_places=6, max_digits=8, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CompetitorGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('developer', models.CharField(blank=True, max_length=200)),
                ('genre', models.CharField(blank=True, max_length=100)),
                ('mechanic_summary', models.TextField(blank=True)),
                ('strength', models.TextField(blank=True)),
                ('weakness', models.TextField(blank=True)),
                ('monetization', models.TextField(blank=True)),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='LiveOpsEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('event_type', models.CharField(blank=True, max_length=100)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('result_summary', models.TextField(blank=True)),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('date', models.DateField(blank=True, null=True)),
                ('domain', models.CharField(blank=True, max_length=100)),
                ('transcript', models.TextField(blank=True)),
                ('summary', models.TextField(blank=True)),
                ('audio_file', models.CharField(blank=True, max_length=500)),
                ('embedding', pgvector.django.VectorField(blank=True, dimensions=1536, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        # Through models for ManyToMany
        migrations.CreateModel(
            name='GameMechanic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('mechanic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mechanic')),
            ],
            options={'unique_together': {('game', 'mechanic')}},
        ),
        migrations.AddField(
            model_name='mechanic',
            name='games',
            field=models.ManyToManyField(related_name='mechanics', through='core.GameMechanic', to='core.game'),
        ),
        migrations.CreateModel(
            name='MechanicHypothesis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mechanic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mechanic')),
                ('hypothesis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hypothesis')),
            ],
            options={'unique_together': {('mechanic', 'hypothesis')}},
        ),
        migrations.AddField(
            model_name='hypothesis',
            name='mechanics',
            field=models.ManyToManyField(related_name='hypotheses', through='core.MechanicHypothesis', to='core.mechanic'),
        ),
        migrations.CreateModel(
            name='GameHypothesis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('hypothesis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hypothesis')),
            ],
            options={'unique_together': {('game', 'hypothesis')}},
        ),
        migrations.AddField(
            model_name='hypothesis',
            name='games',
            field=models.ManyToManyField(related_name='hypotheses', through='core.GameHypothesis', to='core.game'),
        ),
        migrations.CreateModel(
            name='HypothesisResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hypothesis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hypothesis')),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.result')),
            ],
            options={'unique_together': {('hypothesis', 'result')}},
        ),
        migrations.AddField(
            model_name='result',
            name='hypotheses',
            field=models.ManyToManyField(related_name='results', through='core.HypothesisResult', to='core.hypothesis'),
        ),
        migrations.CreateModel(
            name='GameMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('metric', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.metric')),
            ],
            options={'unique_together': {('game', 'metric')}},
        ),
        migrations.AddField(
            model_name='metric',
            name='games',
            field=models.ManyToManyField(related_name='metrics', through='core.GameMetric', to='core.game'),
        ),
        migrations.CreateModel(
            name='GameABTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('ab_test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.abtest')),
            ],
            options={'unique_together': {('game', 'ab_test')}},
        ),
        migrations.AddField(
            model_name='abtest',
            name='games',
            field=models.ManyToManyField(related_name='ab_tests', through='core.GameABTest', to='core.game'),
        ),
        migrations.CreateModel(
            name='GameCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.campaign')),
            ],
            options={'unique_together': {('game', 'campaign')}},
        ),
        migrations.AddField(
            model_name='campaign',
            name='games',
            field=models.ManyToManyField(related_name='campaigns', through='core.GameCampaign', to='core.game'),
        ),
        migrations.CreateModel(
            name='GameCompetitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('competitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.competitorgame')),
            ],
            options={'unique_together': {('game', 'competitor')}},
        ),
        migrations.AddField(
            model_name='competitorgame',
            name='games',
            field=models.ManyToManyField(related_name='competitors', through='core.GameCompetitor', to='core.game'),
        ),
        migrations.CreateModel(
            name='GameLiveOps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('live_ops_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.liveopsEvent')),
            ],
            options={'unique_together': {('game', 'live_ops_event')}},
        ),
        migrations.AddField(
            model_name='liveopsEvent',
            name='games',
            field=models.ManyToManyField(related_name='live_ops_events', through='core.GameLiveOps', to='core.game'),
        ),
        migrations.CreateModel(
            name='MeetingGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.meeting')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
            ],
            options={'unique_together': {('meeting', 'game')}},
        ),
        migrations.AddField(
            model_name='meeting',
            name='games',
            field=models.ManyToManyField(related_name='meetings', through='core.MeetingGame', to='core.game'),
        ),
        migrations.CreateModel(
            name='TeamGame',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.team')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('role', models.CharField(blank=True, max_length=100)),
            ],
            options={'unique_together': {('team', 'game')}},
        ),
        migrations.CreateModel(
            name='TeamMeeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.team')),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.meeting')),
            ],
            options={'unique_together': {('team', 'meeting')}},
        ),
        migrations.AddField(
            model_name='meeting',
            name='teams',
            field=models.ManyToManyField(related_name='meetings', through='core.TeamMeeting', to='core.team'),
        ),
    ]
