import { useRef, useState, useEffect } from "react";

function PlayIcon() { return <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>; }
function PauseIcon() { return <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" /></svg>; }

function formatTime(s) {
  if (!isFinite(s)) return "0:00";
  return `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
}

function SinglePlayer({ label, src, accentColor = "purple" }) {
  const audioRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    const a = audioRef.current;
    if (!a) return;
    const onEnd = () => setPlaying(false);
    const onTime = () => { setCurrentTime(a.currentTime); setProgress(a.duration ? a.currentTime / a.duration : 0); };
    const onMeta = () => setDuration(a.duration);
    a.addEventListener("ended", onEnd);
    a.addEventListener("timeupdate", onTime);
    a.addEventListener("loadedmetadata", onMeta);
    return () => { a.removeEventListener("ended", onEnd); a.removeEventListener("timeupdate", onTime); a.removeEventListener("loadedmetadata", onMeta); };
  }, [src]);

  const toggle = () => { const a = audioRef.current; if (!a) return; if (playing) { a.pause(); setPlaying(false); } else { a.play(); setPlaying(true); } };
  const seek = (e) => { const a = audioRef.current; if (!a || !a.duration) return; const rect = e.currentTarget.getBoundingClientRect(); a.currentTime = ((e.clientX - rect.left) / rect.width) * a.duration; };

  const colors = { purple: { btn: "bg-purple-600 hover:bg-purple-500", bar: "bg-purple-500" }, emerald: { btn: "bg-emerald-600 hover:bg-emerald-500", bar: "bg-emerald-500" } };
  const c = colors[accentColor] || colors.purple;

  return (
    <div className="bg-white/5 rounded-xl p-4 border border-white/10">
      <audio ref={audioRef} src={src} preload="metadata" />
      <div className="flex items-center gap-3">
        <button onClick={toggle} className={`w-10 h-10 rounded-full ${c.btn} flex items-center justify-center text-white shrink-0 transition-colors`}>
          {playing ? <PauseIcon /> : <PlayIcon />}
        </button>
        <div className="flex-1 min-w-0">
          <p className="text-xs text-white/50 mb-1.5 font-medium uppercase tracking-wide">{label}</p>
          <div className="h-1.5 rounded-full bg-white/10 cursor-pointer" onClick={seek}>
            <div className={`h-full rounded-full ${c.bar} transition-all`} style={{ width: `${progress * 100}%` }} />
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-xs text-white/30 font-mono">{formatTime(currentTime)}</span>
            <span className="text-xs text-white/30 font-mono">{formatTime(duration)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AudioPlayer({ originalFile, processedUrl }) {
  const originalSrc = originalFile ? URL.createObjectURL(originalFile) : null;
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-white/70 uppercase tracking-wide">Preview Before / After</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {originalSrc && <SinglePlayer label="Original" src={originalSrc} accentColor="purple" />}
        {processedUrl && <SinglePlayer label="Humanized" src={processedUrl} accentColor="emerald" />}
      </div>
    </div>
  );
}
