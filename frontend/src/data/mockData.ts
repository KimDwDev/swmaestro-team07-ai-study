// 데모/개발용 목 데이터.
// 백엔드 연동 전에 화면을 확인하기 위한 샘플이며, GET /api/users/roadmap 응답 형태와 동일합니다.

import type { RoadmapCreateResponse, RoadmapViewResponse } from '../types/api';

/** 로드맵 단계 메타데이터 (progress / roadmap 키와 매핑) */
const PHASES = [
  { key: 'week1To2', title: '기초 다지기' },
  { key: 'week3To4', title: '핵심 역량 강화' },
  { key: 'week5To6', title: '프로젝트 실전' },
  { key: 'week7To8', title: '포트폴리오 & 준비' },
] as const;

export function parseDurationWeeks(value?: string): number {
  const match = value?.match(/\d+/);
  return match ? Number(match[0]) : 8;
}

export function getRoadmapPhases(durationWeeks: number) {
  return PHASES.map((phase, index) => {
    const start = Math.floor((index * durationWeeks) / PHASES.length) + 1;
    const end = Math.floor(((index + 1) * durationWeeks) / PHASES.length);
    return {
      ...phase,
      range: start === end ? `${start}주차` : `${start}-${end}주차`,
    };
  });
}

export const mockRoadmap: RoadmapViewResponse = {
  recommendedPath: 'AI Product Engineer',
  skillGaps: ['시스템 설계 경험', '배포/운영 경험', 'AI 모델링 이해'],
  skillGap: 3,
  durationWeeks: 8,
  roadmap: {
    week1To2: ['필수 개념 학습', '개발 환경 세팅', '기초 프로젝트 기획', '자료구조/알고리즘 복습'],
    week3To4: ['AI 모델링 이해', 'API 개발 연습', '기초 프로젝트 개선', '데이터 전처리 실습'],
    week5To6: ['프로젝트 개발', '테스트 코드 작성', '테스트 & 개선', '코드 리뷰 반영'],
    week7To8: ['문서화 & README', '포트폴리오 정리', '면접 준비', '직무 과제 대비'],
  },
  progress: { week1To2: 3, week3To4: 2, week5To6: 1, week7To8: 0 },
  currentWeek: 1,
};

export function toRoadmapViewResponse(response: RoadmapCreateResponse, duration?: string): RoadmapViewResponse {
  return {
    recommendedPath: response.recommendedPath,
    skillGaps: response.skillGaps,
    skillGap: response.skillGaps.length,
    durationWeeks: parseDurationWeeks(duration),
    roadmap: response.roadmap,
    progress: { week1To2: 0, week3To4: 0, week5To6: 0, week7To8: 0 },
    currentWeek: 1,
  };
}

/**
 * 초기 완료 항목(전역 인덱스).
 * 전역 인덱스 = 모든 주차 항목을 week1To2 → week7To8 순서로 0부터 나열했을 때의 위치.
 * PATCH /api/users/roadmap 의 completedItems 와 동일한 규칙입니다.
 */
export const mockInitialCompletedItems: number[] = [0, 1, 2, 4, 5, 8];
