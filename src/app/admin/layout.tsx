import AdminShell from "@/components/layout/AdminShell";
import { getNavBadges } from "@/lib/api";

export default async function AdminLayout({ children }: LayoutProps<"/admin">) {
  const badges = await getNavBadges();
  return <AdminShell badges={badges}>{children}</AdminShell>;
}
