import os
import requests
import json


def transcribe(audio_file_path: str) -> str:
    """CLOVA Speech API로 음성 파일을 한국어 텍스트로 변환합니다."""
    invoke_url = os.getenv('NAVER_CLOUD_INVOKE_URL', '')
    api_key = os.getenv('NAVER_CLOUD_API_KEY', '')

    if not invoke_url or not api_key:
        return _mock_transcribe(audio_file_path)

    request_body = {
        'language': 'ko-KR',
        'completion': 'sync',
        'wordAlignment': True,
        'fullText': True,
    }

    try:
        with open(audio_file_path, 'rb') as f:
            response = requests.post(
                invoke_url,
                headers={
                    'X-CLOVASPEECH-API-KEY': api_key,
                    'Accept': 'application/json',
                },
                files={
                    'media': f,
                    'params': (None, json.dumps(request_body), 'application/json'),
                },
                timeout=60,
            )
        response.raise_for_status()
        result = response.json()
        return result.get('text', '')
    except Exception as e:
        print(f"CLOVA Speech 오류: {e}")
        return _mock_transcribe(audio_file_path)


def _mock_transcribe(audio_file_path: str) -> str:
    """CLOVA API 없이 테스트용 더미 텍스트 반환"""
    filename = os.path.basename(audio_file_path).lower()
    if 'snake' in filename:
        return (
            "오늘 Snake Clash! 기획 회의에서 뱀 이동 메카닉의 조작 단순화를 논의했습니다. "
            "기획팀은 조작을 단순하게 만들면 D1 리텐션이 올라갈 것이라는 가설을 세웠습니다. "
            "배틀로얄 메카닉 추가도 논의되었고, 이를 통해 DAU를 35% 높일 수 있다고 판단했습니다."
        )
    return (
        "오늘 회의에서 게임 기획에 대한 다양한 논의가 이루어졌습니다. "
        "팀원들이 메카닉과 가설에 대해 활발히 의견을 나눴습니다."
    )
