import {
  Home,
  Route,
  ClipboardList,
  MessageSquareText,
  BookOpen,
  Users,
  User,
  Settings,
  Sparkles,
  ArrowUpRight,
} from 'lucide-react';
import styles from './Sidebar.module.css';

export type NavKey =
  | 'home'
  | 'roadmap'
  | 'planner'
  | 'mentor'
  | 'resources'
  | 'community'
  | 'profile'
  | 'settings';

const NAV_ITEMS: { key: NavKey; label: string; Icon: typeof Home }[] = [
  { key: 'home', label: '홈', Icon: Home },
  { key: 'roadmap', label: '로드맵', Icon: Route },
  { key: 'planner', label: '실행 플래너', Icon: ClipboardList },
  { key: 'mentor', label: '멘토링 코치', Icon: MessageSquareText },
  { key: 'resources', label: '학습 리소스', Icon: BookOpen },
  { key: 'community', label: '커뮤니티', Icon: Users },
  { key: 'profile', label: '내 프로필', Icon: User },
  { key: 'settings', label: '설정', Icon: Settings },
];

interface SidebarProps {
  active: NavKey;
  onNavigate?: (key: NavKey) => void;
}

export default function Sidebar({ active, onNavigate }: SidebarProps) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <div className={styles.logoMark}>
          <Sparkles size={18} strokeWidth={2.4} />
        </div>
        <div>
          <div className={styles.brandName}>CareerMate</div>
          <div className={styles.brandSub}>나만을 위한 커리어 로드맵 에이전트</div>
        </div>
      </div>

      <nav className={styles.nav}>
        {NAV_ITEMS.map(({ key, label, Icon }) => (
          <button
            key={key}
            type="button"
            className={`${styles.navItem} ${active === key ? styles.navItemActive : ''}`}
            onClick={() => onNavigate?.(key)}
          >
            <Icon size={18} strokeWidth={2} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className={styles.proCard}>
        <div className={styles.proTitleRow}>
          <span className={styles.proTitle}>CareerMate Pro</span>
          <ArrowUpRight size={16} />
        </div>
        <p className={styles.proDesc}>더 스마트한 커리어 여정</p>
        <button type="button" className={styles.proButton}>
          업그레이드 하기 →
        </button>
      </div>
    </aside>
  );
}
