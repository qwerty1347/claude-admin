"use client";

import { useState } from "react";
import Link from "next/link";
import { formatTime, formatWon } from "@/lib/format";
import type { Order, OrderStatus } from "@/types/dashboard";

const statusStyle: Record<OrderStatus, { label: string; className: string }> = {
  paid: { label: "결제 완료", className: "bg-primary-weak text-primary" },
  shipping: { label: "배송 중", className: "bg-[#fff3e0] text-[#e67700]" },
  delivered: { label: "배송 완료", className: "bg-[#e5f8ef] text-[#028a52]" },
  cancelled: { label: "취소", className: "bg-canvas text-muted" },
};

const filters: ("all" | OrderStatus)[] = ["all", "paid", "shipping", "delivered", "cancelled"];

export default function RecentOrders({ orders }: { orders: Order[] }) {
  const [filter, setFilter] = useState<"all" | OrderStatus>("all");
  const visible = filter === "all" ? orders : orders.filter((o) => o.status === filter);

  const countOf = (f: "all" | OrderStatus) =>
    f === "all" ? orders.length : orders.filter((o) => o.status === f).length;

  return (
    <section className="h-full rounded-card bg-surface p-7" aria-labelledby="orders-title">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="orders-title" className="text-[20px] font-bold tracking-tight text-ink">
          오늘 들어온 주문
        </h2>
        <Link href="/admin/orders" className="text-[14px] font-semibold text-primary hover:underline">
          전체 주문 보기
        </Link>
      </div>

      <div className="mt-4 flex flex-wrap gap-2" role="group" aria-label="주문 상태로 거르기">
        {filters.map((f) => {
          const selected = f === filter;
          return (
            <button
              key={f}
              type="button"
              aria-pressed={selected}
              onClick={() => setFilter(f)}
              className={`rounded-full px-3.5 py-1.5 text-[14px] font-semibold transition-colors ${
                selected ? "bg-ink text-white" : "bg-canvas text-sub hover:bg-line"
              }`}
            >
              {f === "all" ? "전체" : statusStyle[f].label}
              <span className={`ml-1.5 ${selected ? "text-white/60" : "text-muted"}`}>{countOf(f)}</span>
            </button>
          );
        })}
      </div>

      <div className="-mx-7 mt-4 overflow-x-auto">
        <table className="w-full min-w-[680px] text-[15px]">
          <thead>
            <tr className="text-left text-[13px] text-muted">
              <th className="px-7 py-3 font-medium">고객</th>
              <th className="px-7 py-3 font-medium">주문번호</th>
              <th className="px-7 py-3 font-medium">상태</th>
              <th className="px-7 py-3 text-right font-medium">금액</th>
              <th className="px-7 py-3 text-right font-medium">주문 시각</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((order) => {
              const status = statusStyle[order.status];
              return (
                <tr key={order.id} className="border-t border-line/70 hover:bg-canvas/60">
                  <td className="px-7 py-3.5">
                    <span className="flex items-center gap-3">
                      <span
                        className="flex size-9 shrink-0 items-center justify-center rounded-full bg-canvas text-[14px] font-semibold text-sub"
                        aria-hidden
                      >
                        {order.customer.slice(0, 1)}
                      </span>
                      <span className="font-semibold text-ink">{order.customer}</span>
                    </span>
                  </td>
                  <td className="px-7 py-3.5 text-[14px] text-muted">{order.id}</td>
                  <td className="px-7 py-3.5">
                    <span
                      className={`inline-flex rounded-lg px-2.5 py-1 text-[13px] font-semibold ${status.className}`}
                    >
                      {status.label}
                    </span>
                  </td>
                  <td
                    className={`px-7 py-3.5 text-right font-bold ${
                      order.status === "cancelled" ? "text-muted line-through" : "text-ink"
                    }`}
                  >
                    {formatWon(order.amount)}
                  </td>
                  <td className="px-7 py-3.5 text-right text-sub">
                    <time dateTime={order.orderedAt}>{formatTime(order.orderedAt)}</time>
                  </td>
                </tr>
              );
            })}
            {visible.length === 0 && (
              <tr>
                <td colSpan={5} className="px-7 py-10 text-center text-[15px] text-muted">
                  이 상태의 주문은 아직 없어요
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
