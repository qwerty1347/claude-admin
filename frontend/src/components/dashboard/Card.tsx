type Props = {
  /** 작은 제목 (무엇에 대한 카드인지) */
  title: string;
  /** 큰 문장 (한눈에 알아야 할 결론) */
  headline?: string;
  className?: string;
  children: React.ReactNode;
};

export default function Card({ title, headline, className = "", children }: Props) {
  return (
    <section className={`rounded-card bg-surface p-7 ${className}`}>
      <header className="mb-5">
        <h2 className="text-[16px] font-semibold text-sub">{title}</h2>
        {headline && (
          <p className="mt-1 text-[22px] font-bold tracking-tight text-ink">{headline}</p>
        )}
      </header>
      {children}
    </section>
  );
}
