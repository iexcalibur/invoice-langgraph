export default function WorkflowDetailLoading() {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-10 w-20 bg-white/10 rounded animate-pulse" />
            <div className="space-y-2">
              <div className="h-10 w-48 bg-white/10 rounded animate-pulse" />
              <div className="h-5 w-64 bg-white/10 rounded animate-pulse" />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-8 w-24 bg-white/10 rounded animate-pulse" />
            <div className="h-10 w-10 bg-white/10 rounded animate-pulse" />
          </div>
        </div>

        {/* Status Card Skeleton */}
        <div className="glass p-6 rounded-lg">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 w-20 bg-white/10 rounded animate-pulse" />
                <div className="h-8 w-24 bg-white/10 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>

        {/* Stage Progress Skeleton */}
        <div className="glass p-6 rounded-lg">
          <div className="h-6 w-32 bg-white/10 rounded animate-pulse mb-4" />
          <div className="space-y-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="flex items-center gap-4">
                <div className="h-5 w-32 bg-white/10 rounded animate-pulse" />
                <div className="flex-1 h-2 bg-white/10 rounded animate-pulse" />
                <div className="h-6 w-20 bg-white/10 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>

        {/* Logs Skeleton */}
        <div className="glass p-6 rounded-lg">
          <div className="h-6 w-32 bg-white/10 rounded animate-pulse mb-4" />
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 w-full bg-white/10 rounded animate-pulse" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

