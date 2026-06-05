"""build_phases — 주차를 UI 단계 카드로 묶기 (라벨 기반 / 폴백 청크)."""

from __future__ import annotations

from agent3.llm import build_phases
from agent3.models import ResourceItem, SourceOrigin, TaskItem, WeekPlan


def _week(idx, phase, skills):
    return WeekPlan(
        week_index=idx,
        phase=phase,
        covered_skills=skills,
        planned_hours=8,
        tasks=[
            TaskItem(
                title=f"{s} 학습",
                skill=s,
                est_hours=4,
                resources=[ResourceItem(title="r", url="https://x", verified=True, origin=SourceOrigin.db)],
            )
            for s in skills
        ],
    )


def test_semantic_grouping_by_phase_label():
    weeks = [
        _week(1, "기초 다지기", ["JavaScript"]),
        _week(2, "기초 다지기", ["JavaScript"]),
        _week(3, "핵심 역량 강화", ["React"]),
        _week(4, "핵심 역량 강화", ["TypeScript"]),
    ]
    phases = build_phases(weeks)
    assert len(phases) == 2
    assert phases[0].title == "기초 다지기"
    assert phases[0].week_from == 1 and phases[0].week_to == 2
    assert phases[1].title == "핵심 역량 강화"
    assert phases[1].week_from == 3 and phases[1].week_to == 4


def test_checklist_item_ids_and_resources():
    weeks = [_week(1, "기초", ["JavaScript", "HTML/CSS"])]
    phases = build_phases(weeks)
    items = phases[0].items
    assert [it.id for it in items] == ["p1-i1", "p1-i2"]
    assert items[0].label == "JavaScript 학습"
    assert items[0].skill == "JavaScript"
    assert items[0].resources and items[0].resources[0].verified is True
    # completed 필드는 존재하지 않는다 (Agent3는 진행상태를 내보내지 않음)
    assert not hasattr(items[0], "completed")


def test_fallback_chunks_two_weeks_when_no_labels():
    weeks = [_week(i, None, ["React"]) for i in range(1, 5)]  # 라벨 없음
    phases = build_phases(weeks)
    assert len(phases) == 2  # 4주 → 2주씩 2단계
    assert phases[0].week_from == 1 and phases[0].week_to == 2
    assert phases[1].week_from == 3 and phases[1].week_to == 4
    assert phases[0].title  # 커버 스킬에서 파생된 제목


def test_empty_weeks():
    assert build_phases([]) == []
