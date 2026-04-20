from django.db import transaction
from core.models import (
    Game, Mechanic, Hypothesis, Result, Team, Metric,
    Campaign, CompetitorGame, LiveOpsEvent, Meeting,
    GameMechanic, MechanicHypothesis, GameHypothesis, HypothesisResult,
    GameMetric, GameCampaign, GameCompetitor, GameLiveOps,
    MeetingGame, TeamGame, TeamMeeting,
)
from . import gpt_service


@transaction.atomic
def save_entities(game_id: int, entities: dict, meeting: Meeting = None) -> tuple:
    """GPT 추출 엔티티를 DB에 저장하고 온톨로지 관계를 구성합니다."""
    game = Game.objects.get(id=game_id)
    nodes_created = 0
    edges_created = 0

    node_map = {}

    for node_data in entities.get('nodes', []):
        node_type = node_data.get('type')
        name = node_data.get('name', '').strip()
        description = node_data.get('description', '')
        extra = node_data.get('extra', {})

        if not name:
            continue

        obj = None
        if node_type == 'Game':
            obj, created = Game.objects.get_or_create(
                name=name,
                defaults={'description': description, 'genre': extra.get('genre', '')}
            )
        elif node_type == 'Mechanic':
            obj, created = Mechanic.objects.get_or_create(
                name=name,
                defaults={'description': description, 'category': extra.get('category', '')}
            )
        elif node_type == 'Hypothesis':
            obj = Hypothesis.objects.create(
                content=name if not description else f"{name}: {description}",
                status=extra.get('status', 'pending'),
                created_by=extra.get('created_by', ''),
            )
            created = True
        elif node_type == 'Result':
            obj = Result.objects.create(
                description=name if not description else description,
                metric_type=extra.get('metric_type', ''),
                metric_value=extra.get('metric_value'),
                unit=extra.get('unit', ''),
            )
            created = True
        elif node_type == 'Team':
            # 팀은 새로 생성하지 않고 기존 팀 이름과 매칭만 수행
            try:
                obj = Team.objects.get(name=name)
                created = False
            except Team.DoesNotExist:
                obj = None
                created = False
        elif node_type == 'Metric':
            obj = Metric.objects.create(
                name=name,
                value=extra.get('value'),
                unit=extra.get('unit', ''),
                metric_type=extra.get('metric_type', ''),
            )
            created = True
        elif node_type == 'Campaign':
            obj = Campaign.objects.create(
                name=name,
                channel=extra.get('channel', ''),
                cpi=extra.get('cpi'),
                roas=extra.get('roas'),
                ctr=extra.get('ctr'),
            )
            created = True
        elif node_type == 'CompetitorGame':
            obj, created = CompetitorGame.objects.get_or_create(
                name=name,
                defaults={
                    'developer': extra.get('developer', ''),
                    'mechanic_summary': description,
                    'strength': extra.get('strength', ''),
                    'weakness': extra.get('weakness', ''),
                }
            )
        elif node_type == 'LiveOpsEvent':
            obj = LiveOpsEvent.objects.create(
                name=name,
                event_type=extra.get('event_type', ''),
                result_summary=description,
            )
            created = True

        if obj:
            if created:
                nodes_created += 1
            node_map[name] = (node_type, obj)
            _generate_and_save_embedding(obj, node_type, name, description)

    for edge_data in entities.get('edges', []):
        from_name = edge_data.get('from_name', '').strip()
        to_name = edge_data.get('to_name', '').strip()
        relation = edge_data.get('relation', '')

        from_entry = node_map.get(from_name)
        to_entry = node_map.get(to_name)

        if not from_entry or not to_entry:
            if from_name == game.name:
                from_entry = ('Game', game)
            elif to_name == game.name:
                to_entry = ('Game', game)

        if not from_entry or not to_entry:
            continue

        from_type, from_obj = from_entry
        to_type, to_obj = to_entry

        try:
            if relation == 'HAS_MECHANIC' and from_type == 'Game' and to_type == 'Mechanic':
                GameMechanic.objects.get_or_create(game=from_obj, mechanic=to_obj)
                edges_created += 1
            elif relation == 'HAS_HYPOTHESIS' and from_type == 'Mechanic' and to_type == 'Hypothesis':
                MechanicHypothesis.objects.get_or_create(mechanic=from_obj, hypothesis=to_obj)
                GameHypothesis.objects.get_or_create(game=game, hypothesis=to_obj)
                edges_created += 1
            elif relation == 'HAS_RESULT' and to_type == 'Result':
                if from_type == 'Hypothesis':
                    HypothesisResult.objects.get_or_create(hypothesis=from_obj, result=to_obj)
                    edges_created += 1
            elif relation == 'HAS_METRIC' and to_type == 'Metric':
                GameMetric.objects.get_or_create(game=game, metric=to_obj)
                edges_created += 1
            elif relation == 'HAS_CAMPAIGN' and to_type == 'Campaign':
                GameCampaign.objects.get_or_create(game=game, campaign=to_obj)
                edges_created += 1
            elif relation == 'HAS_COMPETITOR' and to_type == 'CompetitorGame':
                GameCompetitor.objects.get_or_create(game=game, competitor=to_obj)
                edges_created += 1
            elif relation == 'HAS_LIVEOPS' and to_type == 'LiveOpsEvent':
                GameLiveOps.objects.get_or_create(game=game, live_ops_event=to_obj)
                edges_created += 1
            elif relation == 'INVOLVED_IN' and from_type == 'Team':
                TeamGame.objects.get_or_create(team=from_obj, game=game)
                if meeting:
                    TeamMeeting.objects.get_or_create(team=from_obj, meeting=meeting)
                edges_created += 1
        except Exception as e:
            print(f"엣지 저장 오류 ({relation}): {e}")

    if meeting:
        MeetingGame.objects.get_or_create(meeting=meeting, game=game)

    return nodes_created, edges_created


def _generate_and_save_embedding(obj, node_type: str, name: str, description: str):
    """노드 텍스트로 임베딩을 생성하고 저장합니다."""
    if not hasattr(obj, 'embedding'):
        return
    text = f"{node_type} {name} {description}"
    try:
        embedding = gpt_service.embed(text)
        obj.embedding = embedding
        obj.save(update_fields=['embedding'])
    except Exception as e:
        print(f"임베딩 저장 오류: {e}")


def get_graph_data(game_id: int = None, team_id: int = None) -> dict:
    """vis.js용 그래프 데이터를 반환합니다."""
    nodes = []
    edges = []
    node_ids = set()

    def add_node(node_id, label, node_type, color, size=20):
        if node_id not in node_ids:
            nodes.append({
                'id': node_id,
                'label': label[:30],
                'type': node_type,
                'color': color,
                'size': size,
                'title': label,
            })
            node_ids.add(node_id)

    def add_edge(from_id, to_id, label=''):
        edges.append({'from': from_id, 'to': to_id, 'label': label})

    NODE_COLORS = {
        'game': '#6366f1',
        'mechanic': '#8b5cf6',
        'hypothesis': '#f59e0b',
        'result': '#22c55e',
        'team': '#64748b',
        'metric': '#06b6d4',
        'campaign': '#ec4899',
        'competitor': '#f97316',
        'liveops': '#84cc16',
        'meeting': '#a78bfa',
    }

    if game_id:
        games = Game.objects.filter(id=game_id)
    elif team_id:
        games = Game.objects.filter(teamgame__team_id=team_id)
    else:
        games = Game.objects.all()

    for game in games:
        gid = f"game_{game.id}"
        add_node(gid, game.name, 'game', NODE_COLORS['game'], 35)

        for mechanic in game.mechanics.all():
            mid = f"mechanic_{mechanic.id}"
            add_node(mid, mechanic.name, 'mechanic', NODE_COLORS['mechanic'], 25)
            add_edge(gid, mid, 'HAS_MECHANIC')

            for hyp in mechanic.hypotheses.all():
                hid = f"hypothesis_{hyp.id}"
                color = NODE_COLORS['hypothesis']
                if hyp.status == 'validated':
                    color = NODE_COLORS['result']
                elif hyp.status == 'failed':
                    color = '#ef4444'
                add_node(hid, hyp.content[:40], 'hypothesis', color, 20)
                add_edge(mid, hid, 'HAS_HYPOTHESIS')

                for result in hyp.results.all():
                    rid = f"result_{result.id}"
                    label = result.description[:30]
                    if result.metric_value:
                        label += f" ({result.metric_value}{result.unit})"
                    add_node(rid, label, 'result', NODE_COLORS['result'], 18)
                    add_edge(hid, rid, 'HAS_RESULT')

        for metric in game.metrics.all():
            meid = f"metric_{metric.id}"
            add_node(meid, f"{metric.metric_type}={metric.value}{metric.unit}", 'metric', NODE_COLORS['metric'], 18)
            add_edge(gid, meid, 'HAS_METRIC')

        for campaign in game.campaigns.all():
            cid = f"campaign_{campaign.id}"
            label = f"{campaign.name}\nCPI ${campaign.cpi}" if campaign.cpi else campaign.name
            add_node(cid, label, 'campaign', NODE_COLORS['campaign'], 18)
            add_edge(gid, cid, 'HAS_CAMPAIGN')

        for competitor in game.competitors.all():
            compid = f"competitor_{competitor.id}"
            add_node(compid, competitor.name, 'competitor', NODE_COLORS['competitor'], 18)
            add_edge(gid, compid, 'HAS_COMPETITOR')

        for team in Team.objects.filter(teamgame__game=game):
            tid = f"team_{team.id}"
            add_node(tid, team.name, 'team', NODE_COLORS['team'], 16)
            add_edge(tid, gid, 'INVOLVED_IN')

    return {'nodes': nodes, 'edges': edges}


def search_similar_nodes(query_vector: list, limit: int = 10) -> list:
    """pgvector 코사인 유사도로 관련 노드를 검색합니다."""
    from pgvector.django import CosineDistance

    results = []
    models_to_search = [
        (Game, 'game'), (Mechanic, 'mechanic'), (Hypothesis, 'hypothesis'),
        (Result, 'result'), (Metric, 'metric'), (Campaign, 'campaign'),
        (CompetitorGame, 'competitor'),
    ]

    for Model, node_type in models_to_search:
        try:
            qs = Model.objects.filter(embedding__isnull=False).annotate(
                distance=CosineDistance('embedding', query_vector)
            ).order_by('distance')[:3]

            for obj in qs:
                name = getattr(obj, 'name', None) or getattr(obj, 'content', '')[:50]
                desc = getattr(obj, 'description', '') or getattr(obj, 'content', '')
                results.append({
                    'type': node_type,
                    'id': obj.id,
                    'name': name,
                    'description': desc,
                    'distance': float(obj.distance) if hasattr(obj, 'distance') else 1.0,
                })
        except Exception as e:
            print(f"{Model.__name__} 유사도 검색 오류: {e}")

    results.sort(key=lambda x: x.get('distance', 1.0))
    return results[:limit]
