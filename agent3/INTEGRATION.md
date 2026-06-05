# Agent3 통합 협의 체크리스트

> Agent3는 현재 **독립 실행**으로 완성돼 있습니다. 입력 3개(`profile`·`job_requirement`·`weekly_hours`)는
> 요청 본문에 **직접 주입**하고, episodic memory는 **받기만 하고 저장하지 않으며**, gap→job 되먹임은
> **신호만 surface**합니다. 이 문서는 에이전트1·2·백엔드·통합 그래프와 **협의해야 할 접점**을 정리합니다.
>
> 관련 문서: [README.md](README.md)(설계) · [IMPLEMENTATION.md](IMPLEMENTATION.md)(구현 현황) · [../docs/06-data-model.md](../docs/06-data-model.md)(스키마)

---

## 한 줄 요약

> **"입력 3개는 직접 주입 중, 메모리는 받기만 하고 저장 안 함, 되먹임은 신호만 보냄"** — 이 세 가지가 통합 시 실제 연결돼야 할 핵심 접점입니다.

---

## 1. 에이전트1 (profile_diagnosis) 담당자와

현재 `tests/fixtures/profile_*.json` 목으로 `ProfileDiagnosis` 형태를 가정 중.

- [ ] **출력 스키마 일치**: 에이전트1 출력이 `summary / strengths / weaknesses / interests / readiness_level / evidence` 필드와 맞는가
- [ ] **strengths/weaknesses 입도**: Agent3는 이를 **스킬명 수준**(`"JavaScript"`, `"React"`)으로 보고 `strengths`를 갭에서 제외한다. 문장형(`"JS로 앱 만들어봄"`)으로 주면 제외 매칭이 실패 → 입도 합의 필요
- [ ] **readiness_level enum**: `"low" / "mid" / "high"` 동일하게 쓰는가
- [ ] **weakness 정확도**: weaknesses가 부족역량 후보로 직접 쓰이므로 과대/과소 추정 주의

> 코드 위치: `gap_analysis_agent.py`(강점 제외), `llm.py::_build_gap_prompt`, `models.py::ProfileDiagnosis`

---

## 2. 에이전트2 (job_requirement) 담당자와

Agent2의 `JobRequirement`는 필드가 많고(`companies`, `postings` 등) `source="duckduckgo"`를 쓰므로,
Agent3는 `extra="ignore"`로 **그대로 받아** 핵심 필드만 사용한다.

- [ ] **`keywords` 필드 유지**: required_skills가 문장형이라 Agent3는 **`keywords`를 스킬명 추출 힌트로 의존**한다. 에이전트2가 `keywords`에 **깔끔한 기술 토큰**(`["React", "TypeScript"]`)을 계속 채워주는지 보장 필요
- [ ] **`evidence_strength` 정직성**: `"strong" / "weak"` 값이 **`needs_rerun` 트리거**다. weak 남발 시 불필요한 되먹임 발생
- [ ] **gap→job 되먹임 입력 경로**: Agent3가 `needs_rerun=true` + `rerun_reason`을 응답에 surface한다. 에이전트2가 **`rerun_reason`을 컨텍스트로 받아 재추출**하는 입력 경로 필요
- [ ] **핵심 필드명 안정성**: `required_skills / preferred_skills / required_experience / keywords / evidence_strength` 이름 변경 시 **사전 통지**

> 코드 위치: `models.py::JobRequirement`(extra=ignore), `gap_analysis_agent.py`(needs_rerun), `main.py`(응답 surface)

---

## 3. 백엔드 담당자와

- [ ] **영속성(episodic memory)**: 현재 `episodic_memory`를 요청 본문에 받으면 반영하지만 **저장하지 않는다.** DB(SQLite/MySQL)의 `last_roadmap` / `weekly_progress` 테이블 R/W를 누가 구현? (docs/06 §6 스키마)
- [ ] **`user_id` / `session_id`**: `Agent3State`에서 **제외**(단독 실행용)했다. 사용자 식별·메모리 조회 키를 백엔드가 주입할지, State에 다시 넣을지
- [ ] **`/progress` 엔드포인트**: 미구현(주차 완료 체크박스). 진척 기록 → 다음 로드맵 반영 루프. 누가 구현? (docs/06 §7-4)
- [ ] **서비스 경계**: Agent3가 **독립 FastAPI(:8003)**. 백엔드가 모듈 import할지 / 별도 서비스 HTTP 호출할지 / 포트·CORS·인증 정책
- [ ] **시크릿 관리**: 로컬 `agent3/.env`의 `UPSTAGE_API_KEY` → 배포 환경 키 주입 방식
- [ ] **`weekly_hours` 출처**: 현재 요청에 직접 받음. 온보딩 입력의 어느 단계에서 전달되는지

> 코드 위치: `state.py::Agent3State`, `main.py`(엔드포인트·`Agent3Request`)

---

## 4. 통합(전체 LangGraph) 차원에서

- [ ] **State 통합**: `Agent3State`는 docs의 `CareerMateState`의 **부분집합**(triage/clarify 필드 없음). 전체 그래프 합칠 때 단일 State로 통일 — 필드명 정합
- [ ] **루프 카운터 증가 위치(CANON E)**: 단독 실행에선 `main.py` orchestrator가 `revision_count++`/`rerun_count++`를 담당한다. 전체 그래프에선 **conditional edge**가 담당 → **중복 증가 방지** 정리 필요
- [ ] **trace 포맷**: `TraceEntry`로 통일. 에이전트1·2·라우터도 **동일 trace 포맷**을 써야 대시보드 "why-this-path" 타임라인이 일관됨
- [ ] **노드 시그니처**: Agent3는 `state -> state`(async/sync 혼재). LangGraph 노드 규약과 맞추기

---

## 현재 입출력 계약 (참고)

### 입력 — `POST /agent3/roadmap`
```json
{
  "profile":         { "...": "에이전트1 ProfileDiagnosis" },
  "job_requirement": { "...": "에이전트2 JobRequirement (extra 필드 무시)" },
  "weekly_hours":    8,
  "episodic_memory": null,     // 선택 — 있으면 반영(저장은 안 함)
  "rerun_count":     0         // 되먹임 가드용
}
```

### 출력 — `Agent3Response`
```json
{
  "final_output": {
    "profile": {}, "gap_analysis": {}, "roadmap": {},
    "verified": true, "trace_summary": [], "disclaimer": "...", "search_degraded": false
  },
  "needs_rerun":  false,        // true면 통합 그래프가 에이전트2 재실행 필요
  "rerun_reason": null
}
```

---

## 협의 우선순위 제안

1. **에이전트2 `keywords`/`evidence_strength` 계약** — Agent3 품질에 직접 영향 (가장 시급)
2. **백엔드 영속성 + `user_id`** — 재방문 시나리오 실동작에 필요
3. **에이전트1 입도 합의** — 강점 제외 로직 정확도
4. **통합 그래프 State/카운터 통일** — 에이전트1 완성 후
