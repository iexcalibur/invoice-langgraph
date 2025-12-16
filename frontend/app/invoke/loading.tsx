export default function InvokeLoading() {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-center gap-4">
          <div className="h-10 w-20 bg-white/10 rounded animate-pulse" />
          <div className="h-10 w-48 bg-white/10 rounded animate-pulse" />
        </div>

        {/* Form Skeleton */}
        <div className="glass p-6 rounded-lg space-y-6">
          <div className="h-8 w-32 bg-white/10 rounded animate-pulse" />
          <div className="grid grid-cols-2 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 w-24 bg-white/10 rounded animate-pulse" />
                <div className="h-10 w-full bg-white/10 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>

        {/* Line Items Skeleton */}
        <div className="glass p-6 rounded-lg space-y-4">
          <div className="flex items-center justify-between">
            <div className="h-6 w-32 bg-white/10 rounded animate-pulse" />
            <div className="h-10 w-32 bg-white/10 rounded animate-pulse" />
          </div>
          {[...Array(2)].map((_, i) => (
            <div key={i} className="h-20 w-full bg-white/10 rounded animate-pulse" />
          ))}
        </div>
      </div>
    </div>
  );
}

