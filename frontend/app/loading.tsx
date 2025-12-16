export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="space-y-4 text-center">
        <div className="w-12 h-12 border-4 border-purple-500/20 border-t-purple-500 rounded-full animate-spin mx-auto" />
        <p className="text-white/60">Loading...</p>
      </div>
    </div>
  );
}

