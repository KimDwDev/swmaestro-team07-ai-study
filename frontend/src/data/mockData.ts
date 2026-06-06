// 데모/개발용 목 데이터.
// 백엔드 연동 전에 화면을 확인하기 위한 샘플이며, GET /api/users/roadmap 응답 형태와 동일합니다.

import type { RoadmapViewResponse, SkillGapScores } from '../types/api';

/** 역량 갭 레이더 차트 축 라벨 (skillGapScores 키 순서와 1:1 대응) */
export const SKILL_LABELS = [
  '프로그래밍',
  'AI/ML',
  '시스템 설계',
  '배포/운영',
  '협업/커뮤니케이션',
  '문제 정의',
] as const;

/** skillGapScores 객체를 레이더 차트용 숫자 배열(라벨 순서)로 변환 */
export function toSkillArray(scores: SkillGapScores): number[] {
  return [
    scores.programming,
    scores.aiMl,
    scores.systemDesign,
    scores.deploymentAndOperations,
    scores.collaborationAndCommunication,
    scores.identifiedProblem,
  ];
}

/**
 * 목표 수준(레이더의 바깥 폴리곤).
 * API는 현재 수준(skillGapScores)만 내려주므로, 목표 수준은 프론트 기준값으로 둡니다.
 * 백엔드에서 목표치를 내려주게 되면 이 상수를 응답값으로 교체하세요.
 */
export const SKILL_TARGETS: number[] = [92, 88, 85, 80, 88, 85];

/** 로드맵 단계 메타데이터 (progress / roadmap 키와 매핑) */
export const PHASES = [
  { key: 'week1To2', range: '1-2주차', title: '기초 다지기' },
  { key: 'week3To4', range: '3-4주차', title: '핵심 역량 강화' },
  { key: 'week5To6', range: '5-6주차', title: '프로젝트 실전' },
  { key: 'week7To8', range: '7-8주차', title: '포트폴리오 & 준비' },
] as const;

export const mockRoadmap: RoadmapViewResponse = {
  recommendedPath: 'AI Product Engineer',
  skillGap: 3,
  skillGapScores: {
    programming: 78,
    aiMl: 55,
    systemDesign: 42,
    deploymentAndOperations: 38,
    collaborationAndCommunication: 64,
    identifiedProblem: 58,
  },
  roadmap: {
    week1To2: ['필수 개념 학습', '개발 환경 세팅', '기초 프로젝트 기획', '자료구조/알고리즘 복습'],
    week3To4: ['AI 모델링 이해', 'API 개발 연습', '기초 프로젝트 개선', '데이터 전처리 실습'],
    week5To6: ['프로젝트 개발', '테스트 코드 작성', '테스트 & 개선', '코드 리뷰 반영'],
    week7To8: ['문서화 & README', '포트폴리오 정리', '면접 준비', '직무 과제 대비'],
  },
  progress: { week1To2: 3, week3To4: 2, week5To6: 1, week7To8: 0 },
  currentWeek: 1,
};

/**
 * 초기 완료 항목(전역 인덱스).
 * 전역 인덱스 = 모든 주차 항목을 week1To2 → week7To8 순서로 0부터 나열했을 때의 위치.
 * PATCH /api/users/roadmap 의 completedItems 와 동일한 규칙입니다.
 */
export const mockInitialCompletedItems: number[] = [0, 1, 2, 4, 5, 8];
