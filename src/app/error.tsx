"use client"; // 에러 화면은 클라이언트 컴포넌트여야 한다

import { useEffect } from "react";
import { CloudOff } from "lucide-react";

// 루트 아래 세그먼트의 레이아웃에서 난 에러 (예: admin/layout.tsx 의 사이드바 배지 조회 실패).
// 사이드바까지 못 그리므로 화면 전체를 대신한다. 루트 레이아웃 자체의 에러는 global-error.tsx 담당.
export default function RootError({
  error,
  retry,
}: {
  error: Error & { digest?: string };
  retry: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-canvas px-6 text-center">
      <span className="flex size-14 items-center justify-center rounded-2xl bg-surface">
        <CloudOff className="size-7 text-muted" />
      </span>
      <h1 className="mt-5 text-[20px] font-bold text-ink">관리자 화면을 불러오지 못했어요</h1>
      <p className="mt-2 text-[15px] text-sub">잠시 후 다시 시도해 주세요. 계속 안 되면 서버 상태를 확인해 주세요.</p>
      <button
        type="button"
        onClick={() => retry()}
        className="mt-6 rounded-xl bg-primary px-5 py-3 text-[15px] font-semibold text-white hover:bg-primary-strong"
      >
        다시 시도
      </button>
      {error.digest && <p className="mt-4 text-[13px] text-muted">오류 번호 {error.digest}</p>}
    </main>
  );
}
