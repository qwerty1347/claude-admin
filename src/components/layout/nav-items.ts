import {
  LayoutDashboard,
  Package,
  Settings,
  ShoppingCart,
  Users,
  type LucideIcon,
} from "lucide-react";

export type NavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
};

// 관리자 메뉴 추가: app/admin/<이름>/page.tsx 를 만들고 여기에 한 줄 추가
export const navItems: NavItem[] = [
  { label: "대시보드", href: "/admin", icon: LayoutDashboard },
  { label: "주문 관리", href: "/admin/orders", icon: ShoppingCart },
  { label: "상품 관리", href: "/admin/products", icon: Package },
  { label: "회원 관리", href: "/admin/users", icon: Users },
];

// 사이드바 맨 아래에 따로 두는 메뉴
export const bottomNavItems: NavItem[] = [
  { label: "설정", href: "/admin/settings", icon: Settings },
];

export const allNavItems = [...navItems, ...bottomNavItems];

export function isActive(pathname: string, href: string): boolean {
  if (href === "/admin") return pathname === "/admin";
  return pathname === href || pathname.startsWith(`${href}/`);
}
