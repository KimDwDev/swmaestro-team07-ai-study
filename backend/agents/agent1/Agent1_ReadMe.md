# ReadMe: 에이전트 1 (Profile Diagnosis Agent) 연동 가이드

본 문서는 **CareerMate 3주 프로젝트**에서 개편된 **에이전트 1 (프로필 진단 에이전트)**의 구현 사양, API 규격, 입력 및 출력 데이터 스펙, 호출 방법을 정리한 개발자 가이드입니다. 

---

## 1. 개요 및 제공 기능
* **역할**: 온보딩 입력값(7가지 정형/비정형 데이터)을 기반으로 현재 사용자의 취업 준비 상황을 객관적으로 분석하여 **프로필 진단서**를 발행합니다.
* **핵심 지침 (추론 및 가짜 데이터 도출 금지)**: LLM이 사용자가 명시하지 않은 자격증, 스킬, 프로젝트 등을 자의적으로 유추하거나 지어내는 환각(Hallucination) 현상을 원천적으로 차단합니다.
* **동기식 호출 규격**: 백엔드 서버의 메인 라우터 흐름과 맞추기 위해 동기식(Synchronous) 실행 메서드 `default(...)`를 제공합니다.

---

## 2. API 및 환경 구성 (Upstage Solar API)
* **API 모델**: `solar-pro3` (Upstage OpenAI-compatible API)
* **환경 변수 설정**: Upstage API 호출을 위해 시스템 환경변수에 아래의 키가 설정되어 있어야 합니다.
  ```bash
  export UPSTAGE_API_KEY="your-upstage-api-key-here"
  ```

---

## 3. 인터페이스 규격 (API Contracts)

### A. 입력 파라미터 (Input Interface)
`Agent1().default(...)` 메서드는 아래의 7개 파이썬 기본 타입을 순서대로 또는 키워드 인자로 입력받습니다.
(Pydantic 모델 `OnboardingInput`을 통해 내부에서 자동 검증 및 파싱됩니다.)

| 매개변수명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `major` | `str` | 전공 / 학년 정보 (예: `"컴퓨터공학과 4학년 재학"`) |
| `currentStatus` | `str` | 현재 상태 (예: `"취업 준비 중"`, `"재학생"`) |
| `interests` | `list[str]` | 관심사 분야 목록 (복수 선택) (예: `["백엔드 개발", "클라우드"]`) |
| `targetJob` | `str` | 목표 직무 (예: `"백엔드 엔지니어"`) |
| `preferredCompanyType` | `str` | 희망 회사 유형 (예: `"스타트업"`, `"대기업"`) |
| `availableTime` | `str` | 준비 가능 기간 / 주당 시간 (예: `"주당 10시간"`) |
| `concerns` | `list[str]` | 현재 취업/학습 고민 목록 (복수 선택) |

### B. 반환값 스펙 (Output Interface)
메서드 호출 성공 시, Pydantic 모델 `ProfileDiagnosis` 검증을 거친 후 아래의 4개 분석 필드를 가진 **딕셔너리(`dict`)**를 동기식으로 반환합니다. (기타 이월 데이터나 임시 필드는 경량화를 위해 제거되었습니다.)

| 필드명 | 타입 | 설명 |
| :--- | :--- | :--- |
| `summary` | `str` | 사용자의 상황과 고민을 종합한 2~3문장의 정성적 맥락 요약본 |
| `strengths` | `list[str]` | 전공, 직무 일치성 등을 바탕으로 추출된 사용자의 상대적 강점 명칭 목록 |
| `weaknesses` | `list[str]` | 목표 직무 대비 보완해야 할 상대적 약점 명칭 목록 |
| `evidence` | `dict[str, str]` | `strengths`, `weaknesses` 각 리스트 항목의 판단 근거가 된 입력값 매핑 정보 |

---

## 4. 호출 예시 (Python Code Example)

```python
from backend.agents.agent1.Agent1 import Agent1

# 1. 에이전트 1 인스턴스 생성
agent1 = Agent1()

# 2. 동기식 호출 진행
result = agent1.default(
    major="컴퓨터공학과 4학년 재학",
    currentStatus="재학생",
    interests=["프론트엔드 개발", "UI/UX"],
    targetJob="프론트엔드 엔지니어",
    preferredCompanyType="스타트업",
    availableTime="주당 30시간",
    concerns=[
        "실무 프로젝트 협업 경험이 부족합니다.",
        "포트폴리오 작성이 걱정입니다."
    ]
)

# 3. 반환값 확인 (dict 타입)
print(result)
# 출력 예시:
# {
#     "summary": "컴퓨터공학을 전공 중인 4학년 재학생으로 프론트엔드 개발 및 UI/UX에 관심이 있으며 스타트업 취업을 목표로 하고 있습니다. 주당 30시간의 비교적 넉넉한 준비 시간을 확보하고 있으나, 실무 협업 경험 부족과 포트폴리오 작성에 어려움을 느끼고 있습니다.",
#     "strengths": ["전공 일치도", "가용 시간 충분"],
#     "weaknesses": ["실무 협업 경험 부족", "포트폴리오 미비"],
#     "evidence": {
#         "전공 일치도": "major: '컴퓨터공학과 4학년 재학'",
#         "가용 시간 충분": "availableTime: '주당 30시간'",
#         "실무 협업 경험 부족": "concerns: ['실무 프로젝트 협업 경험이 부족합니다.']",
#         "포트폴리오 미비": "concerns: ['포트폴리오 작성이 걱정입니다.']"
#     }
# }
```

---

## 5. 설계 제약 및 가이드라인
1. **Hallucination 차단**: AI 모델이 입력값에 존재하지 않는 실무 역량, 자격증, 기술 스택 등을 자의적으로 매핑하거나 추가적인 정보를 날조하는 것을 방지하기 위해 엄격한 prompt rule이 걸려 있습니다.
2. **Pure Nominal Concept**: `strengths`와 `weaknesses`의 각 항목은 순수 명사형 명칭(예: `"전공 일치도"`, `"포트폴리오 미비"`)으로만 구성되어야 하며, 상세 설명은 `summary` 및 `evidence`에서 제공합니다.
3. **근거 투명성**: `evidence` 딕셔너리는 `strengths`와 `weaknesses` 리스트에 포함된 모든 항목의 키를 반드시 포함해야 하며, 해당 항목을 판단하게 만든 원본 입력 팩트(문항명 및 내용)를 값으로 매핑해야 합니다.
