import Link from "next/link";
import {
  ChevronRight,
  ClipboardList,
  MessageCircle,
  PackageX,
  RotateCcw,
  Truck,
  type LucideIcon,
} from "lucide-react";
import type { TodoSummary } from "@/types/dashboard";

const icons: Record<string, LucideIcon> = {
  "pending-orders": Truck,
  refunds: RotateCcw,
  "low-stock": PackageX,
  inquiries: MessageCircle,
};

export default function TodoPanel({ summary: { items, doneToday } }: { summary: TodoSummary }) {
  const urgentTotal = items.filter((t) => t.urgent).reduce((sum, t) => sum + t.count, 0);
  const remaining = items.reduce((sum, t) => sum + t.count, 0);
  const progress = Math.round((doneToday / (doneToday + remaining)) * 100);

  return (
    <section className="flex h-full flex-col rounded-card bg-surface p-7" aria-labelledby="todo-title">
      <h2 id="todo-title" className="text-[20px] font-bold tracking-tight text-ink">
        처리할 일
      </h2>

      {/* 오늘 처리 진행률 */}
      <div className="mt-5">
        <div className="rounded-2xl bg-canvas p-5">
          <div className="flex items-baseline justify-between">
            <p className="text-[15px] font-semibold text-sub">오늘 처리한 일</p>
            <p className="text-[15px] text-muted">
              <span className="text-[22px] font-bold text-ink">{doneToday}</span>
              <span className="font-semibold text-ink">건</span> / {doneToday + remaining}건
            </p>
          </div>
          <div
            className="mt-3 h-2.5 overflow-hidden rounded-full bg-line"
            role="progressbar"
            aria-label="오늘 처리 진행률"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div className="h-full rounded-full bg-primary" style={{ width: `${progress}%` }} />
          </div>
          <p className="mt-2.5 text-[13px] text-muted">
            {progress}% 끝냈어요. {remaining}건 남았어요.
          </p>
        </div>
      </div>

      {/* 대기 중인 일 — 진행률과 간격을 두어 구분 */}
      {urgentTotal > 0 && (
        <span className="mt-8 self-start text-[14px] font-semibold text-rise">
          대기 중 {urgentTotal}건
        </span>
      )}

      <ul className={`${urgentTotal > 0 ? "mt-3" : "mt-8"} space-y-2`}>
        {items.map((todo) => {
          const Icon = icons[todo.key] ?? ClipboardList;
          return (
            <li key={todo.key}>
              <Link
                href={todo.href}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors ${
                  todo.urgent ? "bg-[#fff5f5] hover:bg-[#ffeeee]" : "bg-canvas hover:bg-line/70"
                }`}
              >
                <span
                  className={`flex size-8 shrink-0 items-center justify-center rounded-lg bg-surface ${
                    todo.urgent ? "text-rise" : "text-sub"
                  }`}
                  aria-hidden
                >
                  <Icon className="size-4" strokeWidth={2.25} />
                </span>
                <span className="min-w-0 flex-1 truncate text-[15px] font-medium text-ink">
                  {todo.label}
                </span>
                <span
                  className={`shrink-0 text-[17px] font-bold ${todo.urgent ? "text-rise" : "text-ink"}`}
                >
                  {todo.count}
                  <span className="ml-0.5 text-[13px] font-semibold">{todo.unit}</span>
                </span>
                <ChevronRight className="size-4 shrink-0 text-muted" aria-hidden />
              </Link>
            </li>
          );
        })}
      </ul>

    </section>
  );
}
