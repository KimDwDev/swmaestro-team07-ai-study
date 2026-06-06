import { useEffect, useMemo, useState } from 'react';
import {
  Bell,
  ChevronDown,
  Route,
  Layers,
  CircleCheck,
  TrendingUp,
  ArrowRight,
  Rocket,
  Users,
  BookOpen,
  MessagesSquare,
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import ProgressBar from '../components/ProgressBar';
import RadarChart from '../components/RadarChart';
import { roadmapApi } from '../api/client';
import type { RoadmapViewResponse } from '../types/api';
import {
  SKILL_LABELS,
  SKILL_TARGETS,
  PHASES,
  toSkillArray,
  mockRoadmap,
  mockInitialCompletedItems,
} from '../data/mockData';
import styles from './Dashboard.module.css';

interface DashboardProps {
  onRestart?: () => void;
}

export default function Dashboard({ onRestart }: DashboardProps) {
  const [data, setData] = useState<RoadmapViewResponse>(mockRoadmap);
  const [completed, setCompleted] = useState<Set<number>>(new Set(mockInitialCompletedItems));

  // 진입 시 실제 로드맵을 조회. 실패하면(미연동) 목 데이터를 그대로 사용합니다.
  useEffect(() => {
    let alive = true;
    roadmapApi
      .get()
      .then((res) => {
        if (!alive) return;
        setData(res);
      })
      .catch((err) => {
        console.warn('로드맵 조회 실패 — 데모 데이터를 사용합니다:', err?.message ?? err);
      });
    return () => {
      alive = false;
    };
  }, []);

  // 주차별 항목을 전역 인덱스와 함께 평탄화
  const flatItems = useMemo(() => {
    const result: { phaseIndex: number; localIndex: number; globalIndex: number; label: string }[] = [];
    let g = 0;
    PHASES.forEach((phase, phaseIndex) => {
      const items = data.roadmap[phase.key];
      items.forEach((label, localIndex) => {
        result.push({ phaseIndex, localIndex, globalIndex: g, label });
        g += 1;
      });
    });
    return result;
  }, [data]);

  const itemsByPhase = useMemo(
    () => PHASES.map((_, i) => flatItems.filter((it) => it.phaseIndex === i)),
    [flatItems]
  );

  const phaseStats = itemsByPhase.map((items) => {
    const total = items.length;
    const done = items.filter((it) => completed.has(it.globalIndex)).length;
    return { total, done, percent: total === 0 ? 0 : Math.round((done / total) * 100) };
  });

  const totalItems = flatItems.length;
  const totalDone = flatItems.filter((it) => completed.has(it.globalIndex)).length;
  const overallPercent = totalItems === 0 ? 0 : Math.round((totalDone / totalItems) * 100);

  const currentPhaseIndex = Math.max(0, Math.min(PHASES.length - 1, data.currentWeek - 1));
  const currentStat = phaseStats[currentPhaseIndex] ?? { total: 0, done: 0, percent: 0 };

  const toggleItem = (globalIndex: number) => {
    setCompleted((prev) => {
      const next = new Set(prev);
      if (next.has(globalIndex)) next.delete(globalIndex);
      else next.add(globalIndex);

      // 진행 상황을 백엔드에 반영 (PATCH). 미연동이면 조용히 무시.
      roadmapApi
        .updateProgress({ completedItems: Array.from(next).sort((a, b) => a - b) })
        .catch((err) => console.warn('진행 상황 저장 실패:', err?.message ?? err));

      return next;
    });
  };

  return (
    <div className="app-shell">
      <Sidebar active="roadmap" onNavigate={(key) => key === 'home' && onRestart?.()} />

      <main className="app-main">
        {/* 상단 바 */}
        <div className={styles.topbar}>
          <div className={styles.greetingBlock}>
            <h1 className={styles.greeting}>
              민지님, 오늘도 성장하는 하루 되세요! <Rocket size={20} className={styles.rocket} />
            </h1>
            <p className={styles.greetingSub}>{data.recommendedPath}를 향한 여정을 응원해요.</p>
          </div>
          <div className={styles.topbarRight}>
            <button type="button" className={styles.iconButton} aria-label="알림">
              <Bell size={18} />
            </button>
            <button type="button" className={styles.userChip}>
              <span className={styles.avatar}>김</span>
              <span>김민지</span>
              <ChevronDown size={15} />
            </button>
          </div>
        </div>

        {/* 요약 카드 4개 */}
        <div className={styles.statGrid}>
          <StatCard
            icon={<Route size={18} />}
            label="추천 경로"
            value={data.recommendedPath}
            valueAccent
            action="경로 자세히 보기"
          />
          <StatCard
            icon={<Layers size={18} />}
            label="역량 갭"
            value={`${data.skillGap}개 부족 역량`}
            action="상세 보기"
          />
          <StatCard
            icon={<CircleCheck size={18} />}
            label="이번 주 목표"
            value={`${currentStat.done} / ${currentStat.total} 완료`}
            action="목표 보기"
          />
          <StatCard
            icon={<TrendingUp size={18} />}
            label="전체 진행률"
            value={`${overallPercent}%`}
            action="자세히 보기"
            footer={<ProgressBar percent={overallPercent} variant="primary" />}
          />
        </div>

        <div className={styles.middleRow}>
          {/* 역량 갭 분석 (레이더) */}
          <section className={`card ${styles.radarCard}`}>
            <div className={styles.cardHead}>
              <h2 className={styles.cardTitle}>역량 갭 분석</h2>
              <div className={styles.legend}>
                <span className={styles.legendItem}>
                  <i className={styles.dotCurrent} /> 현재 수준
                </span>
                <span className={styles.legendItem}>
                  <i className={styles.dotTarget} /> 목표 수준
                </span>
              </div>
            </div>
            <div className={styles.radarWrap}>
              <RadarChart
                labels={SKILL_LABELS}
                current={toSkillArray(data.skillGapScores)}
                target={SKILL_TARGETS}
                size={300}
              />
            </div>
          </section>

          {/* 8주 로드맵 */}
          <section className={`card ${styles.roadmapCard}`}>
            <div className={styles.cardHead}>
              <h2 className={styles.cardTitle}>8주 커리어 로드맵</h2>
            </div>
            <div className={styles.roadmapGrid}>
              {PHASES.map((phase, i) => {
                const stat = phaseStats[i];
                const items = itemsByPhase[i];
                return (
                  <div key={phase.key} className={styles.phaseCol}>
                    <div className={styles.phaseRange}>{phase.range}</div>
                    <div className={styles.phaseTitle}>{phase.title}</div>
                    <ul className={styles.taskList}>
                      {items.map((it) => {
                        const done = completed.has(it.globalIndex);
                        return (
                          <li key={it.globalIndex}>
                            <button
                              type="button"
                              className={`${styles.task} ${done ? styles.taskDone : ''}`}
                              onClick={() => toggleItem(it.globalIndex)}
                            >
                              <span className={`${styles.checkbox} ${done ? styles.checkboxOn : ''}`} />
                              <span>{it.label}</span>
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                    <div className={styles.phaseProgress}>
                      <span className={styles.phaseProgressLabel}>진행률 {stat.percent}%</span>
                      <ProgressBar percent={stat.percent} />
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </div>

        {/* 이번 단계 주요 카드 */}
        <h2 className={styles.sectionLabel}>이번 단계 주요 카드</h2>
        <div className={styles.actionGrid}>
          <ActionCard
            icon={<Rocket size={16} />}
            label="주력 프로젝트"
            title="AI 기반 미팅 요약 서비스"
            action="자세히 보기"
          />
          <ActionCard
            icon={<Users size={16} />}
            label="멘토 & 팀 준비"
            title="1:1 멘토링 미팅 준비하기"
            action="준비하기"
          />
          <ActionCard
            icon={<BookOpen size={16} />}
            label="학습 리소스"
            title="맞춤 학습 자료 12개"
            action="보기"
          />
          <ActionCard
            icon={<MessagesSquare size={16} />}
            label="커뮤니티 질문"
            title="유사 고민을 가진 동료와 소통"
            action="바로 가기"
          />
        </div>
      </main>
    </div>
  );
}

/* ───────── 보조 컴포넌트 ───────── */

function StatCard({
  icon,
  label,
  value,
  action,
  valueAccent,
  footer,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  action: string;
  valueAccent?: boolean;
  footer?: React.ReactNode;
}) {
  return (
    <div className={`card ${styles.statCard}`}>
      <div className={styles.statTop}>
        <span className={styles.statIcon}>{icon}</span>
        <span className={styles.statLabel}>{label}</span>
      </div>
      <div className={`${styles.statValue} ${valueAccent ? styles.statValueAccent : ''}`}>{value}</div>
      {footer}
      <button type="button" className="link-action">
        {action} <ArrowRight size={13} />
      </button>
    </div>
  );
}

function ActionCard({
  icon,
  label,
  title,
  action,
}: {
  icon: React.ReactNode;
  label: string;
  title: string;
  action: string;
}) {
  return (
    <div className={`card ${styles.actionCard}`}>
      <div className={styles.actionLabel}>
        <span className={styles.actionIcon}>{icon}</span>
        {label}
      </div>
      <div className={styles.actionTitle}>{title}</div>
      <button type="button" className="link-action">
        {action} <ArrowRight size={13} />
      </button>
    </div>
  );
}
