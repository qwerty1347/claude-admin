"use client"; // 에러 화면은 클라이언트 컴포넌트여야 한다

import { useEffect } from "react";
import { CloudOff } from "lucide-react";

// /admin 아래 페이지(대시보드 등)에서 데이터를 못 불러왔을 때. 사이드바·헤더는 그대로 남는다.
// 사이드바 배지(admin/layout.tsx)에서 난 에러는 여기서 잡히지 않고 app/error.tsx 로 간다.
export default function AdminError({
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
    <div className="flex min-h-[60vh] flex-col items-center justify-center rounded-card bg-surface px-6 text-center">
      <span className="flex size-14 items-center justify-center rounded-2xl bg-canvas">
        <CloudOff className="size-7 text-muted" />
      </span>
      <h2 className="mt-5 text-[20px] font-bold text-ink">데이터를 불러오지 못했어요</h2>
      <p className="mt-2 text-[15px] text-sub">잠시 후 다시 시도해 주세요. 계속 안 되면 서버 상태를 확인해 주세요.</p>
      <button
        type="button"
        onClick={() => retry()}
        className="mt-6 rounded-xl bg-primary px-5 py-3 text-[15px] font-semibold text-white hover:bg-primary-strong"
      >
        다시 시도
      </button>
      {error.digest && <p className="mt-4 text-[13px] text-muted">오류 번호 {error.digest}</p>}
    </div>
  );
}
