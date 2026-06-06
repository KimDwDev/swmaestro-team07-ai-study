// 의존성 없이 SVG로 그리는 레이더 차트.
// 현재 수준(primary)과 목표 수준(faint) 두 폴리곤을 겹쳐 그립니다.

interface RadarChartProps {
  labels: readonly string[];
  /** 0~100 */
  current: number[];
  /** 0~100 */
  target: number[];
  size?: number;
}

export default function RadarChart({ labels, current, target, size = 260 }: RadarChartProps) {
  const cx = size / 2;
  const cy = size / 2;
  const radius = size / 2 - 44; // 라벨 공간 확보
  const n = labels.length;
  const rings = [0.25, 0.5, 0.75, 1];

  // 각 축의 좌표 (12시 방향에서 시작, 시계방향)
  const angleFor = (i: number) => (Math.PI * 2 * i) / n - Math.PI / 2;

  const point = (value: number, i: number) => {
    const r = (Math.max(0, Math.min(100, value)) / 100) * radius;
    const a = angleFor(i);
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)] as const;
  };

  const polygon = (values: number[]) =>
    values.map((v, i) => point(v, i).join(',')).join(' ');

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label="역량 갭 레이더 차트">
      {/* 그리드 링 */}
      {rings.map((ring, idx) => (
        <polygon
          key={idx}
          points={labels.map((_, i) => point(ring * 100, i).join(',')).join(' ')}
          fill="none"
          stroke="#e6e9f0"
          strokeWidth={1}
        />
      ))}

      {/* 축 선 */}
      {labels.map((_, i) => {
        const [x, y] = point(100, i);
        return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="#e6e9f0" strokeWidth={1} />;
      })}

      {/* 목표 수준 */}
      <polygon
        points={polygon(target)}
        fill="rgba(148, 163, 184, 0.12)"
        stroke="#94a3b8"
        strokeWidth={1.5}
        strokeDasharray="4 4"
      />

      {/* 현재 수준 */}
      <polygon
        points={polygon(current)}
        fill="rgba(79, 70, 229, 0.16)"
        stroke="#4f46e5"
        strokeWidth={2}
      />
      {current.map((v, i) => {
        const [x, y] = point(v, i);
        return <circle key={i} cx={x} cy={y} r={3.5} fill="#4f46e5" />;
      })}

      {/* 라벨 */}
      {labels.map((label, i) => {
        const a = angleFor(i);
        const lx = cx + (radius + 22) * Math.cos(a);
        const ly = cy + (radius + 22) * Math.sin(a);
        const anchor = Math.abs(Math.cos(a)) < 0.3 ? 'middle' : Math.cos(a) > 0 ? 'start' : 'end';
        return (
          <text
            key={label}
            x={lx}
            y={ly}
            textAnchor={anchor}
            dominantBaseline="middle"
            fontSize={11}
            fill="#64748b"
            fontWeight={500}
          >
            {label}
          </text>
        );
      })}
    </svg>
  );
}
