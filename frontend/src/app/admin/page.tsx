import CategoryPieChart from "@/components/charts/CategoryPieChart";
import HourlyHeatmapChart from "@/components/charts/HourlyHeatmapChart";
import TrafficBarChart from "@/components/charts/TrafficBarChart";
import Card from "@/components/dashboard/Card";
import RecentOrders from "@/components/dashboard/RecentOrders";
import SalesOverview from "@/components/dashboard/SalesOverview";
import TodoPanel from "@/components/dashboard/TodoPanel";
import {
  getCategoryShares,
  getHourlyTraffic,
  getKpis,
  getRecentOrders,
  getRevenueTrend,
  getTodayRevenue,
  getTodos,
  getTrafficSources,
} from "@/lib/api";
import { formatNumber, withSubjectParticle } from "@/lib/format";

export default async function DashboardPage() {
  const [
    kpis,
    revenueTrend,
    categoryShares,
    trafficSources,
    hourlyTraffic,
    recentOrders,
    todoSummary,
    todayRevenue,
  ] = await Promise.all([
    getKpis(),
    getRevenueTrend(),
    getCategoryShares(),
    getTrafficSources(),
    getHourlyTraffic(),
    getRecentOrders(),
    getTodos(),
    getTodayRevenue(),
  ]);

  const topCategory = [...categoryShares].sort((a, b) => b.value - a.value)[0];
  const totalVisitors = trafficSources.reduce((sum, s) => sum + s.visitors, 0);
  const topSource = [...trafficSources].sort((a, b) => b.visitors - a.visitors)[0];
  const [peakHour, peakDay] = hourlyTraffic.values.reduce((max, v) => (v[2] > max[2] ? v : max));

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-12">
      {/* 1행: 오늘 주문 + 처리할 일 */}
      <div className="xl:col-span-8">
        <RecentOrders orders={recentOrders} />
      </div>
      <div className="xl:col-span-4">
        <TodoPanel summary={todoSummary} />
      </div>

      {/* 2행: 매출 추이 + 카테고리별 매출 */}
      <div className="xl:col-span-8">
        <SalesOverview kpis={kpis} trend={revenueTrend} today={todayRevenue} />
      </div>
      <Card
        title="카테고리별 매출"
        headline={`${withSubjectParticle(topCategory.name)} 가장 많이 팔렸어요`}
        className="xl:col-span-4"
      >
        <CategoryPieChart data={categoryShares} />
      </Card>

      {/* 3행: 최근 30일 방문 — 유입 경로 + 접속 시간 */}
      <Card
        title="최근 30일 유입 경로"
        headline={`${formatNumber(totalVisitors)}명 중 ${topSource.channel.split(" ")[0]} 유입이 가장 많아요`}
        className="xl:col-span-6"
      >
        <TrafficBarChart data={trafficSources} />
      </Card>
      <Card
        title="최근 30일 접속 시간"
        headline={`${hourlyTraffic.days[peakDay]}요일 ${hourlyTraffic.hours[peakHour]}에 가장 붐벼요`}
        className="xl:col-span-6"
      >
        <HourlyHeatmapChart data={hourlyTraffic} />
      </Card>
    </div>
  );
}
