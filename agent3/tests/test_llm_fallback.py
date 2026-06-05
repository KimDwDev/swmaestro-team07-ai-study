"""llm.py 규칙기반 폴백 (키 없음) — gap 추출 / 기간 산출 / 패커가 critic을 만족."""

from __future__ import annotations

from agent3.constants import FORBIDDEN_PHRASES, MAX_WEEKS, MIN_WEEKS
from agent3.llm import extract_gaps, generate_roadmap, suggest_total_weeks
from agent3.models import CriticVerdict, JobRequirement
from agent3.roadmap_critic import check_roadmap
from agent3.tools import lookup_skill


def test_fallback_gaps_exclude_strengths(profile_frontend, job_frontend):
    gaps = extract_gaps(profile_frontend, job_frontend, completed_skills=[])
    names = {g.skill for g in gaps}
    assert "React" in names
    assert "TypeScript" in names
    assert "JavaScript" not in names  # 강점이라 제외


def test_fallback_gaps_exclude_completed(profile_frontend, job_frontend):
    gaps = extract_gaps(profile_frontend, job_frontend, completed_skills=["React"])
    assert "React" not in {g.skill for g in gaps}


def test_suggest_total_weeks_bounds(profile_frontend, job_frontend):
    gaps = extract_gaps(profile_frontend, job_frontend)
    records = {g.skill: lookup_skill(g.skill) for g in gaps}
    weeks = suggest_total_weeks(gaps, records, weekly_hours=8)
    assert MIN_WEEKS <= weeks <= MAX_WEEKS


def test_fallback_roadmap_satisfies_critic(profile_frontend, job_frontend):
    gaps = extract_gaps(profile_frontend, job_frontend)
    records = {g.skill: lookup_skill(g.skill) for g in gaps}
    rm = generate_roadmap(gaps, weekly_hours=8, skill_records=records)

    # 규칙기반 패커는 4종을 구조적으로 만족해야 한다
    rep = check_roadmap(rm, gaps, 8, records)
    assert rep.verdict == CriticVerdict.pass_, [v.detail for v in rep.violations]

    # 시간예산 직접 확인
    for w in rm.weeks:
        assert w.planned_hours <= 8

    # 금칙 표현 없음
    blob = rm.model_dump_json()
    assert all(ph not in blob for ph in FORBIDDEN_PHRASES)


def test_fallback_roadmap_empty_gaps():
    rm = generate_roadmap([], weekly_hours=8, skill_records={})
    assert rm.weeks == []
    assert rm.total_weeks == 0
