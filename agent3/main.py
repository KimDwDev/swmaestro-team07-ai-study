"""Agent3 통합 — 오케스트레이션 + finalize + FastAPI 엔드포인트.

노드 연결(docs/02-agent-graph.md):
  progress_reconciliation → gap_analysis → roadmap_plan ⇄ roadmap_critic(revise 루프) → finalize

조건 엣지 책임(CANON E): revision_count 증가는 이 orchestrator(=route 역할)에서만 수행.
gap→job 되먹임(needs_rerun)은 job_requirement가 Agent3 외부(에이전트2) 입력이므로,
standalone 실행에서는 신호만 surface하고 실제 재실행은 통합 그래프가 담당한다.

실행:
  uvicorn agent3.main:app --reload --port 8003
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .constants import MAX_REVISIONS
from .gap_analysis_agent import run_gap_analysis
from .models import (
    CriticVerdict,
    EpisodicMemory,
    FinalOutput,
    JobRequirement,
    MemoryStatus,
    ProfileDiagnosis,
    Roadmap,
)
from .roadmap_critic import run_roadmap_critic
from .roadmap_plan_agent import run_roadmap_plan
from .state import Agent3State, append_trace

_BASE_DISCLAIMER = "이 로드맵은 학습 방향 제안이며 합격이나 진로를 보장하지 않습니다."
_WEB_DISCLAIMER = "일부 자원은 웹검색 출처로 DB 검수를 거치지 않았습니다."
_UNVERIFIED_DISCLAIMER = "일부 항목은 검증되지 않아 직접 확인이 필요합니다."


# ═════════════════════════════════════════════════════════════
# 오케스트레이션
# ═════════════════════════════════════════════════════════════
async def run_agent3(
    profile: ProfileDiagnosis,
    job_requirement: JobRequirement,
    weekly_hours: int,
    episodic_memory: Optional[EpisodicMemory] = None,
    rerun_count: int = 0,
) -> Agent3State:
    """Agent3 전체 파이프라인을 실행해 최종 state를 반환한다."""
    state = Agent3State(
        profile=profile,
        job_requirement=job_requirement,
        weekly_hours=weekly_hours,
        episodic_memory=episodic_memory,
        rerun_count=rerun_count,
    )

    # 1. progress_reconciliation (episodic memory 반영)
    _reconcile(state)

    # 2. gap_analysis (needs_rerun은 surface만; 실제 job 재실행은 통합 그래프 담당)
    state = await run_gap_analysis(state)

    # 3. roadmap_plan → roadmap_critic (revise 루프)
    state = run_roadmap_plan(state)
    state = run_roadmap_critic(state)
    while (
        state.critic_report is not None
        and state.critic_report.verdict == CriticVerdict.revise
        and state.revision_count < MAX_REVISIONS
    ):
        state.revision_count += 1  # CANON E: route(orchestrator)에서만 증가
        state = run_roadmap_plan(state)   # critic_report=revise → 위반 컨텍스트 주입
        state = run_roadmap_critic(state)

    # 4. finalize
    _finalize(state)
    return state


def _reconcile(state: Agent3State) -> None:
    """progress_reconciliation: 재방문자의 미완료=이월, 완료=보유 컨텍스트 추출."""
    mem = state.episodic_memory
    if mem is None or mem.status != MemoryStatus.returning_user or mem.last_roadmap is None:
        append_trace(
            state,
            "progress_reconciliation",
            input_summary="new_user 또는 직전 로드맵 없음",
            decision="skip_reconcile",
            output_summary="이월/완료 컨텍스트 없음",
        )
        return

    carry: list[str] = []
    done: list[str] = []
    for wp in mem.weekly_progress:
        week = next((w for w in mem.last_roadmap.weeks if w.week_index == wp.week_index), None)
        if week is None:
            continue
        (done if wp.completed else carry).extend(week.covered_skills)

    state.carry_over_skills = list(dict.fromkeys(carry))
    state.completed_skills = list(dict.fromkeys(done))
    append_trace(
        state,
        "progress_reconciliation",
        input_summary=f"returning_user, 진행기록 {len(mem.weekly_progress)}주",
        decision="reconcile",
        output_summary=f"이월 {len(state.carry_over_skills)}개, 완료 {len(state.completed_skills)}개",
    )


def _finalize(state: Agent3State) -> None:
    """FinalOutput 조립 + verified·disclaimer·trace 요약."""
    disclaimer = _BASE_DISCLAIMER
    if state.search_degraded:
        disclaimer += " " + _WEB_DISCLAIMER
    if not state.verified:
        disclaimer += " " + _UNVERIFIED_DISCLAIMER

    roadmap = state.roadmap or Roadmap(weekly_hours_budget=state.weekly_hours)

    # finalize 노드 자신을 먼저 trace에 기록한 뒤 스냅샷 → trace_summary가 전체를 포함
    append_trace(
        state,
        "finalize",
        input_summary=f"verified={state.verified}, revision_count={state.revision_count}",
        output_summary=f"FinalOutput 조립 완료, weeks={roadmap.total_weeks}",
    )
    state.final_output = FinalOutput(
        profile=state.profile,
        gap_analysis=state.gap_analysis or _empty_gap(),
        roadmap=roadmap,
        verified=state.verified,
        trace_summary=list(state.trace),
        disclaimer=disclaimer,
        search_degraded=state.search_degraded,
    )


def _empty_gap():
    from .models import GapAnalysis

    return GapAnalysis()


# ═════════════════════════════════════════════════════════════
# FastAPI
# ═════════════════════════════════════════════════════════════
class Agent3Request(BaseModel):
    """profile은 에이전트1 출력, job_requirement는 에이전트2 출력(extra 무시)."""

    model_config = ConfigDict(extra="ignore")

    profile: ProfileDiagnosis
    job_requirement: JobRequirement
    weekly_hours: int = Field(8, ge=1, le=80)
    episodic_memory: Optional[EpisodicMemory] = None
    rerun_count: int = Field(0, ge=0)


class Agent3Response(BaseModel):
    final_output: FinalOutput
    needs_rerun: bool = False
    rerun_reason: Optional[str] = None


class HealthResponse(BaseModel):
    ok: bool
    service: str


app = FastAPI(title="CareerMate Agent3 — Gap & Roadmap")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(ok=True, service="agent3")


@app.post("/agent3/roadmap", response_model=Agent3Response)
async def roadmap(req: Agent3Request) -> Agent3Response:
    state = await run_agent3(
        profile=req.profile,
        job_requirement=req.job_requirement,
        weekly_hours=req.weekly_hours,
        episodic_memory=req.episodic_memory,
        rerun_count=req.rerun_count,
    )
    assert state.final_output is not None
    return Agent3Response(
        final_output=state.final_output,
        needs_rerun=state.needs_rerun,
        rerun_reason=state.rerun_reason,
    )
