import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 배포 이미지(.docker/Dockerfile prod)에 필요한 파일만 .next/standalone 에 모은다
  output: "standalone",
  // 개발 모드 표시(N 버튼)가 사이드바 하단 메뉴를 가리지 않도록 오른쪽 아래로
  devIndicators: { position: "bottom-right" },
};

export default nextConfig;
