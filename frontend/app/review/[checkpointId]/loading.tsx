export default function ReviewDetailLoading() {
  return (
    <div className="min-h-screen p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-center gap-4">
          <div className="h-10 w-20 bg-white/10 rounded animate-pulse" />
          <div className="space-y-2">
            <div className="h-10 w-48 bg-white/10 rounded animate-pulse" />
            <div className="h-5 w-64 bg-white/10 rounded animate-pulse" />
          </div>
        </div>

        {/* Invoice Details Skeleton */}
        <div className="glass p-6 rounded-lg">
          <div className="h-6 w-32 bg-white/10 rounded animate-pulse mb-4" />
          <div className="grid grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 w-20 bg-white/10 rounded animate-pulse" />
                <div className="h-6 w-32 bg-white/10 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>

        {/* Reason Card Skeleton */}
        <div className="glass p-6 rounded-lg">
          <div className="h-6 w-32 bg-white/10 rounded animate-pulse mb-2" />
          <div className="h-20 w-full bg-white/10 rounded animate-pulse" />
        </div>

        {/* Decision Skeleton */}
        <div className="glass p-6 rounded-lg">
          <div className="h-6 w-32 bg-white/10 rounded animate-pulse mb-4" />
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="h-32 w-full bg-white/10 rounded animate-pulse" />
            <div className="h-32 w-full bg-white/10 rounded animate-pulse" />
          </div>
          <div className="h-24 w-full bg-white/10 rounded animate-pulse" />
        </div>

        {/* Submit Button Skeleton */}
        <div className="flex justify-end gap-4">
          <div className="h-10 w-24 bg-white/10 rounded animate-pulse" />
          <div className="h-10 w-32 bg-white/10 rounded animate-pulse" />
        </div>
      </div>
    </div>
  );
}

