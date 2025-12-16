export default function WorkflowsLoading() {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-10 w-48 bg-white/10 rounded animate-pulse" />
            <div className="h-5 w-64 bg-white/10 rounded animate-pulse" />
          </div>
          <div className="h-10 w-32 bg-white/10 rounded animate-pulse" />
        </div>

        {/* Stats Cards Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="glass p-4 rounded-lg">
              <div className="h-4 w-20 bg-white/10 rounded animate-pulse mb-2" />
              <div className="h-8 w-16 bg-white/10 rounded animate-pulse" />
            </div>
          ))}
        </div>

        {/* Filters Skeleton */}
        <div className="glass p-4 rounded-lg">
          <div className="flex items-center gap-4">
            <div className="flex-1 h-10 bg-white/10 rounded animate-pulse" />
            <div className="h-10 w-32 bg-white/10 rounded animate-pulse" />
            <div className="h-10 w-10 bg-white/10 rounded animate-pulse" />
          </div>
        </div>

        {/* Table Skeleton */}
        <div className="glass rounded-lg overflow-hidden">
          <div className="space-y-4 p-6">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center gap-4">
                <div className="h-12 flex-1 bg-white/10 rounded animate-pulse" />
                <div className="h-12 w-24 bg-white/10 rounded animate-pulse" />
                <div className="h-12 w-32 bg-white/10 rounded animate-pulse" />
                <div className="h-12 w-24 bg-white/10 rounded animate-pulse" />
                <div className="h-12 w-32 bg-white/10 rounded animate-pulse" />
                <div className="h-12 w-20 bg-white/10 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

