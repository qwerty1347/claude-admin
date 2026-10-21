"use client";

type Option<T extends string> = { value: T; label: string };

type Props<T extends string> = {
  label: string;
  options: Option<T>[];
  value: T;
  onChange: (value: T) => void;
};

/** 2~4개 보기 중 하나를 고르는 토글 (기간 전환, 보기 전환 등) */
export default function Segmented<T extends string>({ label, options, value, onChange }: Props<T>) {
  return (
    <div role="group" aria-label={label} className="inline-flex shrink-0 rounded-xl bg-canvas p-1">
      {options.map((option) => {
        const selected = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            aria-pressed={selected}
            onClick={() => onChange(option.value)}
            className={`rounded-lg px-3.5 py-1.5 text-[14px] font-semibold transition-colors ${
              selected ? "bg-surface text-ink shadow-sm" : "text-muted hover:text-sub"
            }`}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
