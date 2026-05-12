const LABELS = { queued: "Queued — waiting to start…", processing: "Processing your vocal…", done: "Done!", error: "Processing failed" };

export default function ProgressBar({ status, progress, error, warning }) {
  if (!status) return null;
  const isError = status === "error";
  const isDone = status === "done";
  return (
    <div className={`rounded-xl border p-4 ${isError ? "border-red-500/40 bg-red-500/10" : "border-white/10 bg-white/5"}`}>
      <div className="flex items-center justify-between mb-2">
        <span className={`text-sm font-medium ${isError ? "text-red-400" : isDone ? "text-emerald-400" : "text-white/70"}`}>
          {isError ? error || "Something went wrong" : LABELS[status] || status}
        </span>
        {!isError && <span className="text-sm font-mono text-white/40">{progress}%</span>}
      </div>
      {!isError && (
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <div className={`h-full rounded-full transition-all duration-500 ${isDone ? "bg-emerald-500" : "bg-purple-500"}`} style={{ width: `${progress}%` }}>
            {!isDone && <div className="h-full w-12 bg-white/20 animate-pulse rounded-full" />}
          </div>
        </div>
      )}
      {warning && (
        <p className="mt-2 text-xs text-amber-400/80 flex items-start gap-1.5">
          <svg className="w-3.5 h-3.5 mt-0.5 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" /></svg>
          {warning}
        </p>
      )}
    </div>
  );
}
