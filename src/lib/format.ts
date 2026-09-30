const numberFormat = new Intl.NumberFormat("ko-KR");

export function formatNumber(value: number): string {
  return numberFormat.format(value);
}

export function formatWon(value: number): string {
  return `${numberFormat.format(value)}원`;
}

/** 큰 금액을 "1.3억", "8,200만" 처럼 축약 (차트 축 라벨용) */
export function formatWonShort(value: number): string {
  if (value >= 100_000_000) return `${(value / 100_000_000).toFixed(1)}억`;
  if (value >= 10_000) return `${numberFormat.format(Math.round(value / 10_000))}만`;
  return numberFormat.format(value);
}

/** 읽기 쉬운 한국식 금액: 128,450,000 → "1억 2,845만원" */
export function formatWonKorean(value: number): string {
  const eok = Math.floor(value / 100_000_000);
  const man = Math.floor((value % 100_000_000) / 10_000);
  const parts: string[] = [];
  if (eok > 0) parts.push(`${numberFormat.format(eok)}억`);
  if (man > 0) parts.push(`${numberFormat.format(man)}만`);
  if (parts.length === 0) return formatWon(value);
  return `${parts.join(" ")}원`;
}

/** 받침 유무에 따라 주격 조사 붙이기: "의류" → "의류가", "식품" → "식품이" */
export function withSubjectParticle(word: string): string {
  const code = word.charCodeAt(word.length - 1) - 0xac00;
  const hasBatchim = code >= 0 && code <= 11171 && code % 28 !== 0;
  return `${word}${hasBatchim ? "이" : "가"}`;
}

export function formatPercent(value: number, digits = 1): string {
  return `${value.toFixed(digits)}%`;
}
