import Link from "next/link";
import { Construction } from "lucide-react";

export default function ComingSoon({ title }: { title: string }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center rounded-card bg-surface px-6 text-center">
      <span className="flex size-14 items-center justify-center rounded-2xl bg-canvas">
        <Construction className="size-7 text-muted" />
      </span>
      <h2 className="mt-5 text-[20px] font-bold text-ink">{title} 화면을 만들고 있어요</h2>
      <p className="mt-2 text-[15px] text-sub">지금은 대시보드에서 전체 현황을 볼 수 있어요.</p>
      <Link
        href="/admin"
        className="mt-6 rounded-xl bg-primary px-5 py-3 text-[15px] font-semibold text-white hover:bg-primary-strong"
      >
        대시보드로 가기
      </Link>
    </div>
  );
}
