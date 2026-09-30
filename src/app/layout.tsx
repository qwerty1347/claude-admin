import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

// Pretendard: 한글/영문/숫자 모두 균형 잡힌 오픈소스 서체 (가변 폰트 1개 파일)
const pretendard = localFont({
  src: "../../node_modules/pretendard/dist/web/variable/woff2/PretendardVariable.woff2",
  variable: "--font-pretendard",
  weight: "45 920",
  display: "swap",
});

export const metadata: Metadata = {
  title: "admin",
  description: "admin",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ko" className={`${pretendard.variable} h-full antialiased`}>
      <body className="min-h-full">{children}</body>
    </html>
  );
}
