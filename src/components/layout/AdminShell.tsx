"use client";

import { useState } from "react";
import Header from "./Header";
import Sidebar from "./Sidebar";
import { useSidebarCollapsed } from "./use-sidebar-collapsed";

type Props = {
  badges: Record<string, number>;
  children: React.ReactNode;
};

// 사이드바 상태(데스크톱 접힘 / 모바일 열림)를 Header와 Sidebar가 공유하도록 묶는 틀.
// children(각 페이지)은 서버 컴포넌트 그대로 전달된다.
export default function AdminShell({ badges, children }: Props) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useSidebarCollapsed();

  return (
    <div className="flex min-h-screen bg-canvas">
      <Sidebar
        collapsed={collapsed}
        onToggleCollapsed={() => setCollapsed(!collapsed)}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
        badges={badges}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header onMenuClick={() => setMobileOpen(true)} />
        <main className="mx-auto w-full max-w-[1440px] flex-1 px-4 pt-2 pb-12 sm:px-8">
          {children}
        </main>
      </div>
    </div>
  );
}
