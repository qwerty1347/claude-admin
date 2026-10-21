"use client";

import { usePathname } from "next/navigation";
import { Bell, Menu, Search } from "lucide-react";
import { allNavItems, isActive } from "./nav-items";

type Props = {
  onMenuClick: () => void;
};

export default function Header({ onMenuClick }: Props) {
  const pathname = usePathname();
  const title = allNavItems.find((item) => isActive(pathname, item.href))?.label ?? "관리자";

  return (
    <header className="sticky top-0 z-20 flex h-18 items-center gap-3 bg-canvas/90 px-4 backdrop-blur sm:px-8">
      <button
        type="button"
        className="-ml-1 rounded-lg p-1.5 text-sub hover:bg-surface lg:hidden"
        onClick={onMenuClick}
        aria-label="메뉴 열기"
      >
        <Menu className="size-6" />
      </button>

      <h1 className="text-[22px] font-bold tracking-tight text-ink">{title}</h1>

      <div className="ml-auto flex items-center gap-2">
        <label className="relative hidden md:block">
          <span className="sr-only">회원, 주문번호 검색</span>
          <Search className="pointer-events-none absolute top-1/2 left-3.5 size-4 -translate-y-1/2 text-muted" />
          <input
            type="search"
            placeholder="회원, 주문번호 검색"
            className="h-10 w-64 rounded-xl bg-surface pr-4 pl-10 text-[15px] text-ink placeholder:text-muted outline-none focus:ring-2 focus:ring-primary/30"
          />
        </label>
        <button
          type="button"
          className="relative rounded-xl p-2.5 text-sub hover:bg-surface"
          aria-label="알림 (새 알림 있음)"
        >
          <Bell className="size-5" />
          <span className="absolute top-2 right-2 size-2 rounded-full bg-rise ring-2 ring-canvas" />
        </button>
        <div
          className="flex size-10 items-center justify-center rounded-full bg-surface text-[15px] font-semibold text-sub"
          aria-label="내 계정"
        >
          관
        </div>
      </div>
    </header>
  );
}
