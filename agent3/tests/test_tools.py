"""tools.py — lookup_skill / normalize_skill_name / list_skills_for_role / web_search 예산."""

from __future__ import annotations

import asyncio

from agent3.models import SkillStatus, SourceOrigin
from agent3.tools import (
    list_skills_for_role,
    lookup_skill,
    normalize_skill_name,
    web_search,
    web_search_budgeted,
)


# ── normalize_skill_name ──────────────────────────────────────
def test_normalize_alias_and_case():
    assert normalize_skill_name("react.js") == "React"
    assert normalize_skill_name("fast api") == "FastAPI"
    assert normalize_skill_name("파이썬") == "Python"
    assert normalize_skill_name("PYTHON") == "Python"
    assert normalize_skill_name("  ts  ") == "TypeScript"


def test_normalize_passthrough_on_miss():
    assert normalize_skill_name("React") == "React"
    assert normalize_skill_name("UnknownLib") == "UnknownLib"


def test_normalize_empty():
    assert normalize_skill_name("") == ""


# ── lookup_skill ──────────────────────────────────────────────
def test_lookup_known():
    r = lookup_skill("react.js")
    assert r.status == SkillStatus.known
    assert r.name == "React"
    assert r.verified is True
    assert "JavaScript" in r.prereqs
    assert r.typical_hours == 40
    assert r.resources[0].origin == SourceOrigin.db


def test_lookup_unknown_fallback():
    r = lookup_skill("SomeObscureLib")
    assert r.status == SkillStatus.unknown
    assert r.verified is False
    assert r.resources == [] and r.prereqs == [] and r.typical_hours == 0


def test_lookup_empty_no_throw():
    assert lookup_skill("").status == SkillStatus.unknown


# ── list_skills_for_role ──────────────────────────────────────
def test_list_skills_backend():
    skills = list_skills_for_role("백엔드 개발자")
    names = {s.name for s in skills}
    assert "FastAPI" in names and "PostgreSQL" in names
    assert all(s.status == SkillStatus.known for s in skills)


def test_list_skills_unknown_role():
    assert list_skills_for_role("존재하지 않는 직무") == []


# ── web_search 예산/캐시 (네트워크 없이) ──────────────────────
def test_web_search_empty_query():
    assert asyncio.run(web_search("")) == []
    assert asyncio.run(web_search("   ")) == []


def test_budget_cache_hit_no_count_increase():
    from agent3.models import SearchHit

    cache = {"q": [SearchHit(title="t", url="https://x.com")]}
    hits, cnt, deg = asyncio.run(web_search_budgeted("q", cache, 3))
    assert cnt == 3 and deg is False and hits[0].url == "https://x.com"


def test_budget_max_search_guard_no_api_call():
    # search_count가 MAX_SEARCH(8) 이상이면 API 호출 없이 [] + degraded
    hits, cnt, deg = asyncio.run(web_search_budgeted("new", {}, 8))
    assert hits == [] and cnt == 8 and deg is True
