# 보라님 agent — 갭 분석 + 로드맵 생성 + 자가 검증
"""Agent3 호출 래퍼.

backend/main.py가 agent1·agent2 결과(dict)와 온보딩 request를 넘기면,
내부 파이프라인(run_agent3)을 돌려 프론트가 쓰는 flat 로드맵 dict를 반환한다.

- 동기 메서드(default) 안에서 asyncio.run으로 비동기 파이프라인 실행 (Agent2와 동일 패턴).
- 응답은 RoadmapResponse 형태: recommendedPath / skillGaps[] / roadmap(week1To2..week7To8).
- Agent3의 4단계(phases)가 week1To2/3To4/5To6/7To8에 1:1로 매핑된다.
"""

import asyncio
import re

from .models import JobRequirement, ProfileDiagnosis
from .pipeline import run_agent3

_DEFAULT_WEEKLY_HOURS = 10
_WEEK_KEYS = ["week1To2", "week3To4", "week5To6", "week7To8"]


class Agent3:
    async def default(self, request, agent1_result: dict, agent2_result: dict) -> dict:
        """request(온보딩) + agent1_result + agent2_result → flat 로드맵 dict.

        Args:
            request: RoadmapRequest (majorAndYear, currentStatus, interests, targetJob,
                     preferredCompanyType, availableTime, concerns, ownedSkills).
            agent1_result: {summary, strengths, weaknesses, evidence}.
            agent2_result: {required_skills, preferred_skills, required_experience, keywords, ...}.
        """
        agent1_result = agent1_result or {}
        agent2_result = agent2_result or {}

        weekly_hours = _parse_weekly_hours(getattr(request, "availableTime", None))
        target_role = getattr(request, "targetJob", "") or ""

        profile = ProfileDiagnosis(
            major=getattr(request, "majorAndYear", "") or "",
            current_status=getattr(request, "currentStatus", "") or "",
            interests=getattr(request, "interests", []) or [],
            owned_skills=getattr(request, "ownedSkills", []) or [],
            target_role=target_role,
            company_type=getattr(request, "preferredCompanyType", None),
            weekly_hours=weekly_hours,
            concern=getattr(request, "concerns", []) or [],
            summary=agent1_result.get("summary", ""),
            strengths=agent1_result.get("strengths", []) or [],
            weaknesses=agent1_result.get("weaknesses", []) or [],
            evidence=agent1_result.get("evidence", {}) or {},
        )

        job = JobRequirement(
            required_skills=agent2_result.get("required_skills", []) or [],
            preferred_skills=agent2_result.get("preferred_skills", []) or [],
            required_experience=agent2_result.get("required_experience", []) or [],
            keywords=agent2_result.get("keywords", []) or [],
            # evidence_strength는 에이전트2가 주지 않음 → Agent3가 데이터로 추론
        )

        state = await run_agent3(profile, job, weekly_hours=weekly_hours) # 태환님과 마찬가지로 비동기로 바뀌면서 이 부분을 수정하는게 좋아보여요
        return _to_roadmap_response(state, target_role)


def _parse_weekly_hours(available_time, default: int = _DEFAULT_WEEKLY_HOURS) -> int:
    """availableTime 문자열에서 주당 시간(정수)을 추출. 실패 시 기본값.

    예: "주 15시간" → 15, "20시간 이상" → 20, "15" → 15, None → default.
    """
    if available_time is None:
        return default
    if isinstance(available_time, (int, float)):
        return max(1, int(available_time))
    m = re.search(r"\d+", str(available_time))
    return int(m.group()) if m else default


def _to_roadmap_response(state, target_role: str) -> dict:
    """Agent3 FinalOutput → 프론트 flat 로드맵 dict."""
    fo = state.final_output
    gaps = fo.gap_analysis.gaps if fo and fo.gap_analysis else []
    phases = fo.roadmap.phases if fo and fo.roadmap else []

    roadmap = {key: [] for key in _WEEK_KEYS}
    for i, key in enumerate(_WEEK_KEYS):
        if i < len(phases):
            roadmap[key] = [item.label for item in phases[i].items]

    return {
        "recommendedPath": f"{target_role} 로드맵" if target_role else "맞춤 학습 로드맵",
        "skillGaps": [f"{g.skill} 학습이 필요합니다." for g in gaps],
        "roadmap": roadmap,
    }
