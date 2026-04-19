import os
import json
from openai import OpenAI

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))
    return _client


ENTITY_EXTRACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_ontology_entities",
        "description": "텍스트에서 게임 개발 온톨로지 엔티티(노드와 관계)를 추출합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "nodes": {
                    "type": "array",
                    "description": "추출된 엔티티 노드 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["Game", "Mechanic", "Hypothesis", "Result", "Team", "Metric", "Campaign", "CompetitorGame", "LiveOpsEvent"]
                            },
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "extra": {
                                "type": "object",
                                "description": "타입별 추가 속성 (status, metric_value, channel, cpi 등)"
                            }
                        },
                        "required": ["type", "name"]
                    }
                },
                "edges": {
                    "type": "array",
                    "description": "노드 간 관계 목록",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from_name": {"type": "string"},
                            "to_name": {"type": "string"},
                            "relation": {
                                "type": "string",
                                "enum": ["HAS_MECHANIC", "HAS_HYPOTHESIS", "HAS_RESULT", "HAS_METRIC", "HAS_CAMPAIGN", "HAS_COMPETITOR", "HAS_LIVEOPS", "INVOLVED_IN", "HAS_ABTEST"]
                            }
                        },
                        "required": ["from_name", "to_name", "relation"]
                    }
                }
            },
            "required": ["nodes", "edges"]
        }
    }
}


def extract_entities(text: str, upload_type: str = 'audio') -> dict:
    """gpt-5.4-mini Function Calling으로 텍스트에서 온톨로지 엔티티를 추출합니다."""
    system_prompt = (
        "당신은 게임 개발 회의와 데이터에서 온톨로지 엔티티를 추출하는 전문가입니다. "
        "텍스트에서 게임(Game), 메카닉(Mechanic), 가설(Hypothesis), 결과(Result), 팀(Team), "
        "지표(Metric), 캠페인(Campaign), 경쟁게임(CompetitorGame), 라이브옵스이벤트(LiveOpsEvent)를 추출하세요. "
        "반드시 실제 텍스트에서 언급된 것만 추출하세요."
    )

    client = _get_client()
    if not os.getenv('OPENAI_API_KEY'):
        return _mock_extract_entities(text, upload_type)

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 텍스트에서 온톨로지 엔티티를 추출하세요:\n\n{text}"}
            ],
            tools=[ENTITY_EXTRACTION_TOOL],
            tool_choice={"type": "function", "function": {"name": "extract_ontology_entities"}},
            temperature=0,
        )
        tool_call = response.choices[0].message.tool_calls[0]
        return json.loads(tool_call.function.arguments)
    except Exception as e:
        print(f"GPT 엔티티 추출 오류: {e}")
        return _mock_extract_entities(text, upload_type)


def embed(text: str) -> list:
    """text-embedding-3-small으로 텍스트를 1536차원 벡터로 변환합니다."""
    client = _get_client()
    if not os.getenv('OPENAI_API_KEY'):
        return [0.0] * 1536

    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"임베딩 생성 오류: {e}")
        return [0.0] * 1536


def ask_llm(question: str, context_nodes: list) -> str:
    """온톨로지 컨텍스트를 기반으로 LLM 응답을 생성합니다."""
    client = _get_client()
    if not os.getenv('OPENAI_API_KEY'):
        return _mock_ask(question, context_nodes)

    context_text = _format_context(context_nodes)
    system_prompt = (
        "당신은 SuperSuit AI의 게임 개발 인사이트 어시스턴트입니다. "
        "주어진 온톨로지 컨텍스트(게임, 메카닉, 가설, 결과, 지표 등)를 기반으로 "
        "사용자의 질문에 구체적이고 실용적인 인사이트를 한국어로 답변하세요. "
        "컨텍스트에 없는 내용은 추측하지 마세요."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"온톨로지 컨텍스트:\n{context_text}\n\n질문: {question}"}
            ],
            temperature=0.3,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM 질문 오류: {e}")
        return _mock_ask(question, context_nodes)


def _format_context(nodes: list) -> str:
    if not nodes:
        return "관련 데이터가 없습니다."
    lines = []
    for node in nodes:
        node_type = node.get('type', '')
        name = node.get('name', '')
        desc = node.get('description', '')
        lines.append(f"[{node_type}] {name}: {desc}")
    return '\n'.join(lines)


def _mock_extract_entities(text: str, upload_type: str) -> dict:
    """API 키 없을 때 테스트용 엔티티"""
    return {
        "nodes": [
            {"type": "Game", "name": "Snake Clash!", "description": "하이퍼캐주얼 뱀 배틀 게임"},
            {"type": "Mechanic", "name": "뱀 이동 루프", "description": "뱀이 먹이를 먹고 성장하는 핵심 루프"},
            {"type": "Hypothesis", "name": "조작 단순화 가설", "description": "조작을 단순화하면 D1이 상승할 것", "extra": {"status": "validated"}},
            {"type": "Team", "name": "기획팀", "description": "게임 기획 담당팀"},
        ],
        "edges": [
            {"from_name": "Snake Clash!", "to_name": "뱀 이동 루프", "relation": "HAS_MECHANIC"},
            {"from_name": "뱀 이동 루프", "to_name": "조작 단순화 가설", "relation": "HAS_HYPOTHESIS"},
            {"from_name": "기획팀", "to_name": "Snake Clash!", "relation": "INVOLVED_IN"},
        ]
    }


def _mock_ask(question: str, context_nodes: list) -> str:
    return (
        f"**질문: {question}**\n\n"
        "온톨로지 데이터를 기반으로 분석한 결과입니다:\n\n"
        "Snake Clash!에서 뱀 이동 루프 메카닉을 단순화한 결과 D1 42%를 달성했습니다. "
        "이는 업계 평균 대비 7% 높은 수치입니다. "
        "배틀로얄 요소와의 결합이 핵심 성공 요인으로 분석됩니다.\n\n"
        "*(API 키가 설정되면 실제 온톨로지 기반 분석이 제공됩니다)*"
    )
