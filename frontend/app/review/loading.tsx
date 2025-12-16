export default function ReviewLoading() {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-10 w-48 bg-white/10 rounded animate-pulse" />
            <div className="h-5 w-64 bg-white/10 rounded animate-pulse" />
          </div>
          <div className="h-10 w-24 bg-white/10 rounded animate-pulse" />
        </div>

        {/* Review Cards Grid Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="glass p-6 rounded-lg space-y-4">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="h-6 w-32 bg-white/10 rounded animate-pulse" />
                  <div className="h-4 w-48 bg-white/10 rounded animate-pulse" />
                </div>
                <div className="h-6 w-20 bg-white/10 rounded animate-pulse" />
              </div>
              <div className="space-y-2">
                <div className="h-4 w-full bg-white/10 rounded animate-pulse" />
                <div className="h-4 w-3/4 bg-white/10 rounded animate-pulse" />
              </div>
              <div className="h-16 w-full bg-white/10 rounded animate-pulse" />
              <div className="h-10 w-full bg-white/10 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

