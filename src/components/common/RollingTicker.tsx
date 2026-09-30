"use client";

import { useEffect, useState } from "react";

type Props = {
  items: React.ReactNode[];
  /** 한 항목이 머무는 시간 (ms) */
  interval?: number;
  /** 한 줄 높이 (px). 모든 항목이 이 높이 안에 들어와야 한다. */
  lineHeight?: number;
  /** 스크린 리더용 설명 (굴러가는 줄은 읽지 않고 이 목록 전체를 읽는다) */
  srLabel: string;
  srItems: string[];
};

/**
 * 한 줄 안에서 항목이 위로 굴러 올라가며 바뀌는 띠 (실시간 검색어·시세 띠 방식).
 * 마지막 다음에 첫 항목 복사본을 두고, 복사본에 도착하면 애니메이션 없이 처음으로 되돌려 끊김 없이 반복한다.
 */
export default function RollingTicker({
  items,
  interval = 3000,
  lineHeight = 32,
  srLabel,
  srItems,
}: Props) {
  const count = items.length;
  const [state, setState] = useState({ index: 0, animate: true });
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (paused || count < 2) return;
    const id = window.setInterval(() => {
      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      setState((s) => {
        if (reduceMotion) return { index: (s.index + 1) % count, animate: false };
        // 탭이 백그라운드라 transitionend를 놓친 경우 복사본에서 처음으로 되돌린다
        if (s.index >= count) return { index: 0, animate: false };
        return { index: s.index + 1, animate: true };
      });
    }, interval);
    return () => window.clearInterval(id);
  }, [paused, count, interval]);

  const handleTransitionEnd = (e: React.TransitionEvent<HTMLUListElement>) => {
    if (e.target !== e.currentTarget) return;
    if (state.index === count) setState({ index: 0, animate: false });
  };

  return (
    <div
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
    >
      <div className="overflow-hidden" style={{ height: lineHeight }} aria-hidden>
        <ul
          onTransitionEnd={handleTransitionEnd}
          className={state.animate ? "transition-transform duration-500 ease-out" : ""}
          style={{ transform: `translateY(-${state.index * lineHeight}px)` }}
        >
          {[...items, items[0]].map((item, i) => (
            <li key={i} className="flex items-center" style={{ height: lineHeight }}>
              {item}
            </li>
          ))}
        </ul>
      </div>
      <ul className="sr-only" aria-label={srLabel}>
        {srItems.map((text) => (
          <li key={text}>{text}</li>
        ))}
      </ul>
    </div>
  );
}
