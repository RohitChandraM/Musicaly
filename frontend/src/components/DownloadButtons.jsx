const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function DownloadButtons({ fileId, disabled }) {
  if (!fileId || disabled) return null;

  const download = (fmt) => {
    const a = document.createElement("a");
    a.href = `${API}/download/${fileId}?fmt=${fmt}`;
    a.download = `humanized_vocal.${fmt}`;
    a.click();
  };

  return (
    <div>
      <h3 className="text-sm font-semibold text-white/70 uppercase tracking-wide mb-3">
        Download
      </h3>
      <div className="flex gap-3 flex-wrap">
        <button
          onClick={() => download("wav")}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download WAV
        </button>
        <button
          onClick={() => download("mp3")}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-sm transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download MP3
        </button>
      </div>
    </div>
  );
}
