export default function Loading() {
  return (
    <div className="animate-pulse space-y-4 motion-reduce:animate-none" aria-label="불러오는 중">
      <div className="h-5 w-48 rounded-md bg-line" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, i) => (
          <div key={i} className="h-40 rounded-card bg-surface" />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="h-96 rounded-card bg-surface xl:col-span-2" />
        <div className="h-96 rounded-card bg-surface" />
      </div>
    </div>
  );
}
