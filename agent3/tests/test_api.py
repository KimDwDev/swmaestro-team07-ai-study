"""FastAPI 엔드포인트 (키 없음 폴백) — health + roadmap, agent2 풍부 JSON 호환."""

from __future__ import annotations

from fastapi.testclient import TestClient

from agent3.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True, "service": "agent3"}


def test_roadmap_endpoint_accepts_agent2_rich_json():
    payload = {
        "profile": {
            "major": "컴퓨터공학과 3학년",
            "current_status": "재학 중",
            "interests": ["프론트엔드 개발"],
            "owned_skills": ["JavaScript", "HTML/CSS"],
            "target_role": "프론트엔드 개발자",
            "weekly_hours": 8,
            "concern": ["프레임워크 경험이 없습니다."],
            "summary": "JS 기초 보유, 프레임워크 미경험",
            "strengths": ["전공 일치도"],
            "weaknesses": ["프레임워크 경험 부족"],
        },
        "job_requirement": {
            "required_skills": ["React 컴포넌트 구현", "TypeScript 타입 안전"],
            "preferred_skills": ["상태관리"],
            "keywords": ["React", "TypeScript", "상태관리"],
            "evidence_strength": "strong",
            "source": "duckduckgo",
            "companies": [{"name": "A", "url": "https://a.com"}],  # extra
            "postings": [{"title": "t", "url": "u"}],  # extra
            "summary": "요약",  # extra
            "llm_used": True,  # extra
        },
        "weekly_hours": 8,
    }
    r = client.post("/agent3/roadmap", json=payload)
    assert r.status_code == 200
    data = r.json()
    fo = data["final_output"]

    assert fo["roadmap"]["total_weeks"] >= 1
    assert fo["trace_summary"][0]["node"] == "progress_reconciliation"
    assert fo["trace_summary"][-1]["node"] == "finalize"

    covered = set()
    for w in fo["roadmap"]["weeks"]:
        covered.update(w["covered_skills"])
    for g in fo["gap_analysis"]["gaps"]:
        assert g["skill"] in covered


def test_roadmap_endpoint_validation_error():
    # weekly_hours 범위 밖 → 422
    r = client.post(
        "/agent3/roadmap",
        json={"profile": {}, "job_requirement": {}, "weekly_hours": 0},
    )
    assert r.status_code == 422
