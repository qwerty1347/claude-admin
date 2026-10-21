"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { PanelLeftClose, PanelLeftOpen, X } from "lucide-react";
import { bottomNavItems, isActive, navItems, type NavItem } from "./nav-items";

type Props = {
  /** 데스크톱에서 아이콘만 보이게 접힌 상태 */
  collapsed: boolean;
  onToggleCollapsed: () => void;
  /** 모바일에서 서랍처럼 열린 상태 */
  mobileOpen: boolean;
  onCloseMobile: () => void;
  badges: Record<string, number>;
};

export default function Sidebar({
  collapsed,
  onToggleCollapsed,
  mobileOpen,
  onCloseMobile,
  badges,
}: Props) {
  const pathname = usePathname();

  const renderItem = (item: NavItem) => (
    <SidebarLink
      key={item.href}
      item={item}
      active={isActive(pathname, item.href)}
      badge={badges[item.href]}
      collapsed={collapsed}
      onNavigate={onCloseMobile}
    />
  );

  return (
    <>
      {/* 모바일: 사이드바 뒤 반투명 배경 */}
      <div
        className={`fixed inset-0 z-30 bg-ink/50 transition-opacity motion-reduce:transition-none lg:hidden ${
          mobileOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onCloseMobile}
        aria-hidden
      />

      <aside
        data-collapsed={collapsed}
        className={`group/sidebar fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-ink text-[#b0b8c1] transition-[transform,width] duration-200 motion-reduce:transition-none lg:sticky lg:top-0 lg:h-screen lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        } ${collapsed ? "lg:w-[76px]" : "lg:w-64"}`}
        aria-label="관리자 메뉴"
      >
        <div className="flex h-18 shrink-0 items-center gap-3 px-5">
          <Link
            href="/admin"
            onClick={onCloseMobile}
            className="flex min-w-0 items-center gap-3 rounded-lg"
          >
            <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-primary text-[15px] font-bold text-white">
              A
            </span>
            <span className="truncate text-[17px] font-bold text-white group-data-[collapsed=true]/sidebar:lg:hidden">
              관리자
            </span>
          </Link>
          <button
            type="button"
            className="ml-auto rounded-lg p-1.5 hover:bg-white/10 hover:text-white lg:hidden"
            onClick={onCloseMobile}
            aria-label="메뉴 닫기"
          >
            <X className="size-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-3">{navItems.map(renderItem)}</nav>

        <div className="space-y-1 border-t border-white/10 px-3 py-3">
          {bottomNavItems.map(renderItem)}
          <button
            type="button"
            onClick={onToggleCollapsed}
            className="group/item relative hidden w-full items-center gap-3 rounded-xl group-data-[collapsed=true]/sidebar:lg:justify-center px-3 py-2.5 text-[15px] font-medium hover:bg-white/10 hover:text-white lg:flex"
            aria-label={collapsed ? "메뉴 펼치기" : "메뉴 접기"}
            aria-expanded={!collapsed}
          >
            {collapsed ? (
              <PanelLeftOpen className="size-5 shrink-0" strokeWidth={1.75} />
            ) : (
              <PanelLeftClose className="size-5 shrink-0" strokeWidth={1.75} />
            )}
            <span className="truncate group-data-[collapsed=true]/sidebar:lg:hidden">메뉴 접기</span>
            <Tooltip label="메뉴 펼치기" />
          </button>
        </div>
      </aside>
    </>
  );
}

function SidebarLink({
  item: { label, href, icon: Icon },
  active,
  badge,
  collapsed,
  onNavigate,
}: {
  item: NavItem;
  active: boolean;
  badge?: number;
  collapsed: boolean;
  onNavigate: () => void;
}) {
  return (
    <Link
      href={href}
      onClick={onNavigate}
      aria-current={active ? "page" : undefined}
      aria-label={collapsed ? (badge ? `${label} (${badge}건 대기)` : label) : undefined}
      className={`group/item relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-[15px] transition-colors group-data-[collapsed=true]/sidebar:lg:justify-center ${
        active ? "bg-white/12 font-semibold text-white" : "font-medium hover:bg-white/8 hover:text-white"
      }`}
    >
      <span className="relative shrink-0">
        <Icon className="size-5" strokeWidth={active ? 2.25 : 1.75} />
        {badge ? (
          <span className="absolute -top-1 -right-1 hidden size-2 rounded-full bg-rise ring-2 ring-ink group-data-[collapsed=true]/sidebar:lg:block" />
        ) : null}
      </span>
      <span className="truncate group-data-[collapsed=true]/sidebar:lg:hidden">{label}</span>
      {badge ? (
        <span className="ml-auto rounded-full bg-rise px-2 py-0.5 text-[12px] font-bold text-white group-data-[collapsed=true]/sidebar:lg:hidden">
          {badge}
        </span>
      ) : null}
      <Tooltip label={badge ? `${label} (${badge}건 대기)` : label} />
    </Link>
  );
}

/** 접힌 상태에서만, 마우스를 올리거나 키보드로 포커스하면 메뉴 이름을 보여준다 */
function Tooltip({ label }: { label: string }) {
  return (
    <span
      role="tooltip"
      className="pointer-events-none absolute top-1/2 left-full z-50 ml-3 hidden -translate-y-1/2 rounded-lg bg-ink px-2.5 py-1.5 text-[13px] font-medium whitespace-nowrap text-white opacity-0 shadow-lg ring-1 ring-white/10 transition-opacity group-hover/item:opacity-100 group-focus-visible/item:opacity-100 group-data-[collapsed=true]/sidebar:lg:block"
    >
      {label}
    </span>
  );
}
