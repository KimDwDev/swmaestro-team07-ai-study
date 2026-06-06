// CareerMate API 타입 정의
// 백엔드 FastAPI PR 기준 API 타입 정의입니다.

/** 회원가입 / 로그인 공용 요청 바디 */
export interface AuthRequest {
  email: string;
  password: string;
}

/** 단순 메시지 응답 (회원가입 / 로그인 / 할일 체크) */
export interface MessageResponse {
  message: string;
}

/** 로드맵 생성 요청 (온보딩 입력값) — POST /api/users/roadmap */
export interface RoadmapCreateRequest {
  /** 전공/학년 (예: "컴퓨터공학과/3학년") */
  majorAndYear: string;
  /** 현재 상태 (예: "학생 (취업 준비 중)") */
  currentStatus: string;
  /** 관심 분야 (복수) */
  interests: string[];
  /** 목표 직무 */
  targetJob: string;
  /** 희망 회사 유형 */
  preferredCompanyType: string;
  /** 준비 기간 (예: "8주") */
  availableTime: string;
  /** 현재 고민 (복수) */
  concerns: string[];
}

/** 주차별 로드맵 항목 */
export interface Roadmap {
  week1To2: string[];
  week3To4: string[];
  week5To6: string[];
  week7To8: string[];
}

/** 로드맵 생성 응답 — POST /api/users/roadmap */
export interface RoadmapCreateResponse {
  recommendedPath: string;
  skillGaps: string[];
  roadmap: Roadmap;
}

/** 주차별 완료 개수 */
export interface RoadmapProgress {
  week1To2: number;
  week3To4: number;
  week5To6: number;
  week7To8: number;
}

/** 화면에서 사용하는 로드맵 데이터 (POST 응답 + 프론트 기본값으로 구성) */
export interface RoadmapViewResponse {
  recommendedPath: string;
  skillGaps: string[];
  skillGap: number;
  /** 전체 로드맵 기간(주) */
  durationWeeks: number;
  roadmap: Roadmap;
  progress: RoadmapProgress;
  /** 현재 진행 중인 주차 단계 (1~4) */
  currentWeek: number;
}

/** 할일 체크 요청 — PATCH /api/users/roadmap */
export interface RoadmapProgressUpdateRequest {
  /** 완료한 항목들의 전역 인덱스 배열 */
  completedItems: number[];
}
