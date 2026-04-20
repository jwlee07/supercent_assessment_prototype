import os
import json
import tempfile
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from core.models import (
    Game, Team, Mechanic, Hypothesis, Result, Metric,
    ABTest, Campaign, CompetitorGame, LiveOpsEvent, Meeting,
    TeamGame, TeamMeeting, MeetingGame, GameABTest,
)
from core.services import clova_service, gpt_service, ontology_service


def game_list(request):
    games = Game.objects.annotate(
        mechanic_count=Count('mechanics', distinct=True),
        meeting_count=Count('meetings', distinct=True),
        hypothesis_count=Count('hypotheses', distinct=True),
    )
    return render(request, 'game_list.html', {'games': games})


def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    mechanics = game.mechanics.all()
    teams = Team.objects.filter(teamgame__game=game)
    hypotheses = game.hypotheses.all().prefetch_related('results')
    meetings = Meeting.objects.filter(meetinggame__game=game).order_by('-date')
    graph_data = ontology_service.get_graph_data(game_id=game_id)

    return render(request, 'game_detail.html', {
        'game': game,
        'mechanics': mechanics,
        'teams': teams,
        'hypotheses': hypotheses,
        'meetings': meetings,
        'graph_data_json': json.dumps(graph_data, ensure_ascii=False),
    })


def ontology(request):
    games = Game.objects.all()
    teams = Team.objects.all()
    return render(request, 'ontology.html', {'games': games, 'teams': teams})


def ontology_data(request):
    game_id = request.GET.get('game_id')
    team_id = request.GET.get('team_id')
    data = ontology_service.get_graph_data(
        game_id=int(game_id) if game_id else None,
        team_id=int(team_id) if team_id else None,
    )
    return JsonResponse(data)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def ask_view(request):
    if request.method == 'GET':
        return render(request, 'ask.html')

    try:
        body = json.loads(request.body)
        question = body.get('question', '').strip()
    except Exception:
        question = request.POST.get('question', '').strip()

    if not question:
        return JsonResponse({'error': '질문을 입력해주세요.'}, status=400)

    query_vector = gpt_service.embed(question)
    context_nodes = ontology_service.search_similar_nodes(query_vector, limit=10)

    referenced_nodes = [
        {'type': n['type'], 'id': n['id'], 'name': n['name']}
        for n in context_nodes[:5]
    ]

    answer = gpt_service.ask_llm(question, context_nodes)

    return JsonResponse({
        'answer': answer,
        'referenced_nodes': referenced_nodes,
    })


def teams(request):
    teams_qs = Team.objects.annotate(
        game_count=Count('teamgame__game', distinct=True),
        meeting_count=Count('meetings', distinct=True),
    )
    return render(request, 'teams.html', {'teams': teams_qs})


@csrf_exempt
@require_http_methods(['POST'])
def team_create(request):
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'error': '팀 이름을 입력해주세요.'}, status=400)
    team, created = Team.objects.get_or_create(
        name=name,
        defaults={'description': request.POST.get('description', '')}
    )
    if not created:
        return JsonResponse({'error': f'"{name}" 팀이 이미 존재합니다.'}, status=400)
    return JsonResponse({'success': True, 'team_id': team.id, 'team_name': team.name})


def upload(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_game':
            name = request.POST.get('name', '').strip()
            if name:
                game, _ = Game.objects.get_or_create(
                    name=name,
                    defaults={
                        'genre': request.POST.get('genre', ''),
                        'description': request.POST.get('description', ''),
                    }
                )
                return JsonResponse({'success': True, 'game_id': game.id})
            return JsonResponse({'error': '게임명을 입력해주세요.'}, status=400)

    games = Game.objects.all()
    teams = Team.objects.all()
    hypotheses = Hypothesis.objects.all()
    preselected_game = request.GET.get('game')
    return render(request, 'upload.html', {
        'games': games,
        'teams': teams,
        'hypotheses': hypotheses,
        'preselected_game': preselected_game,
    })


@csrf_exempt
@require_http_methods(['POST'])
def upload_audio(request):
    game_id = request.POST.get('game_id')
    if not game_id:
        return JsonResponse({'error': '게임을 선택해주세요.'}, status=400)

    audio_file = request.FILES.get('audio_file')
    if not audio_file:
        return JsonResponse({'error': '음성 파일을 업로드해주세요.'}, status=400)

    suffix = os.path.splitext(audio_file.name)[1] or '.mp3'
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in audio_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        transcript = clova_service.transcribe(tmp_path)
    finally:
        os.unlink(tmp_path)

    meeting_date = request.POST.get('meeting_date') or None
    domain = request.POST.get('domain', '기획')

    meeting = Meeting.objects.create(
        title=f"{Game.objects.get(id=game_id).name} {domain} 회의",
        date=meeting_date,
        domain=domain,
        transcript=transcript,
        summary=transcript[:200],
    )

    # 트랜스크립트에서 기존 팀 이름 자동 감지 후 연결
    all_teams = Team.objects.all()
    matched_teams = []
    for team in all_teams:
        if team.name in transcript:
            TeamMeeting.objects.get_or_create(team=team, meeting=meeting)
            matched_teams.append(team.name)

    entities = gpt_service.extract_entities(transcript, 'audio')
    nodes_created, edges_created = ontology_service.save_entities(
        int(game_id), entities, meeting=meeting
    )

    return JsonResponse({
        'success': True,
        'meeting_id': meeting.id,
        'nodes_created': nodes_created,
        'edges_created': edges_created,
        'matched_teams': matched_teams,
        'transcript_preview': transcript[:200],
    })


@csrf_exempt
@require_http_methods(['POST'])
def upload_metrics(request):
    game_id = request.POST.get('game_id')
    if not game_id:
        return JsonResponse({'error': '게임을 선택해주세요.'}, status=400)

    metrics_data = request.POST.get('metrics_data', '')
    csv_file = request.FILES.get('file')

    if csv_file:
        content = csv_file.read().decode('utf-8')
    elif metrics_data:
        content = metrics_data
    else:
        return JsonResponse({'error': '데이터를 입력해주세요.'}, status=400)

    entities = gpt_service.extract_entities(content, 'metrics')
    nodes_created, edges_created = ontology_service.save_entities(int(game_id), entities)

    return JsonResponse({
        'success': True,
        'nodes_created': nodes_created,
        'edges_created': edges_created,
    })


@csrf_exempt
@require_http_methods(['POST'])
def upload_marketing(request):
    game_id = request.POST.get('game_id')
    if not game_id:
        return JsonResponse({'error': '게임을 선택해주세요.'}, status=400)

    csv_file = request.FILES.get('file')
    if csv_file:
        content = csv_file.read().decode('utf-8')
    else:
        campaign_name = request.POST.get('campaign_name', '캠페인')
        channel = request.POST.get('channel', '')
        cpi = request.POST.get('cpi', '')
        roas = request.POST.get('roas', '')
        content = f"캠페인명: {campaign_name}, 채널: {channel}, CPI: {cpi}, ROAS: {roas}"

    from core.models import GameCampaign
    campaign = Campaign.objects.create(
        name=request.POST.get('campaign_name', '캠페인'),
        channel=request.POST.get('channel', ''),
        cpi=request.POST.get('cpi') or None,
        roas=request.POST.get('roas') or None,
        ctr=request.POST.get('ctr') or None,
        budget_usd=request.POST.get('budget_usd') or None,
    )
    embedding = gpt_service.embed(f"캠페인 {campaign.name} {campaign.channel}")
    campaign.embedding = embedding
    campaign.save()
    GameCampaign.objects.get_or_create(game_id=int(game_id), campaign=campaign)

    return JsonResponse({'success': True, 'campaign_id': campaign.id, 'nodes_created': 1})


@csrf_exempt
@require_http_methods(['POST'])
def upload_research(request):
    game_id = request.POST.get('game_id')
    if not game_id:
        return JsonResponse({'error': '게임을 선택해주세요.'}, status=400)

    file = request.FILES.get('file')
    text_content = request.POST.get('text_content', '')
    competitor_name = request.POST.get('competitor_name', '경쟁게임')

    if file:
        content = file.read().decode('utf-8', errors='ignore')
    elif text_content:
        content = text_content
    else:
        return JsonResponse({'error': '내용을 입력해주세요.'}, status=400)

    from core.models import GameCompetitor
    competitor, _ = CompetitorGame.objects.get_or_create(
        name=competitor_name,
        defaults={'mechanic_summary': content[:500]}
    )
    embedding = gpt_service.embed(f"경쟁게임 {competitor_name} {content[:200]}")
    competitor.embedding = embedding
    competitor.save()
    GameCompetitor.objects.get_or_create(game_id=int(game_id), competitor=competitor)

    return JsonResponse({'success': True, 'competitor_id': competitor.id, 'nodes_created': 1})


@csrf_exempt
@require_http_methods(['POST'])
def upload_abtest(request):
    game_id = request.POST.get('game_id')
    if not game_id:
        return JsonResponse({'error': '게임을 선택해주세요.'}, status=400)

    test_name = request.POST.get('test_name', 'A/B 테스트')
    ab_test = ABTest.objects.create(
        name=test_name,
        control_description=request.POST.get('control_description', ''),
        variant_description=request.POST.get('variant_description', ''),
        metric=request.POST.get('metric', ''),
        control_value=request.POST.get('control_value') or None,
        variant_value=request.POST.get('variant_value') or None,
        confidence=request.POST.get('confidence') or None,
        result=request.POST.get('result', ''),
    )

    hypothesis_id = request.POST.get('hypothesis_id')
    if hypothesis_id:
        try:
            hyp = Hypothesis.objects.get(id=hypothesis_id)
            ab_test.hypothesis = hyp
            ab_test.save()
            result_val = request.POST.get('result', '')
            if result_val == 'variant_win':
                hyp.status = 'validated'
            elif result_val == 'control_win':
                hyp.status = 'failed'
            hyp.save()
        except Hypothesis.DoesNotExist:
            pass

    embedding = gpt_service.embed(f"A/B테스트 {test_name}")
    ab_test.embedding = embedding
    ab_test.save()
    GameABTest.objects.get_or_create(game_id=int(game_id), ab_test=ab_test)

    return JsonResponse({'success': True, 'abtest_id': ab_test.id, 'nodes_created': 1})


def game_graph_data(request, game_id):
    data = ontology_service.get_graph_data(game_id=game_id)
    return JsonResponse(data)
