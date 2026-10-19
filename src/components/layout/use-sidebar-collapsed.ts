"use client";

import { useCallback, useSyncExternalStore } from "react";

// 데스크톱 사이드바 접힘 상태. localStorage에 저장해 새로고침해도 유지한다.
// 저장소를 쓸 수 없는 환경(시크릿 창 등)에서는 메모리 값으로만 동작한다.
const STORAGE_KEY = "admin.sidebar.collapsed";
const listeners = new Set<() => void>();
let memoryValue = false;

function subscribe(listener: () => void) {
  listeners.add(listener);
  window.addEventListener("storage", listener);
  return () => {
    listeners.delete(listener);
    window.removeEventListener("storage", listener);
  };
}

function getSnapshot(): boolean {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === null ? memoryValue : stored === "1";
  } catch {
    return memoryValue;
  }
}

function getServerSnapshot(): boolean {
  return false;
}

export function useSidebarCollapsed() {
  const collapsed = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const setCollapsed = useCallback((value: boolean) => {
    memoryValue = value;
    try {
      localStorage.setItem(STORAGE_KEY, value ? "1" : "0");
    } catch {
      // 저장 실패 시 메모리 값만 사용
    }
    listeners.forEach((listener) => listener());
  }, []);

  return [collapsed, setCollapsed] as const;
}
