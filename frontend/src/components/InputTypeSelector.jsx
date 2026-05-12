const OPTIONS = [
  {
    id: "auto",
    label: "Auto Detect",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
    desc: "Let the app decide",
  },
  {
    id: "vocal_stem",
    label: "Vocal Stem",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
          d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
      </svg>
    ),
    desc: "Vocals only — fastest",
  },
  {
    id: "full_song",
    label: "Full Song",
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
          d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
      </svg>
    ),
    desc: "Requires Demucs",
  },
];

export default function InputTypeSelector({ value, onChange, disabled }) {
  return (
    <div>
      <label className="block text-sm font-medium text-white/70 mb-3">Input Type</label>
      <div className="flex gap-2 flex-wrap">
        {OPTIONS.map((opt) => {
          const active = value === opt.id;
          return (
            <button
              key={opt.id}
              onClick={() => !disabled && onChange(opt.id)}
              disabled={disabled}
              className={`
                flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm transition-all duration-150
                ${active
                  ? "border-purple-400 bg-purple-500/20 text-purple-300"
                  : "border-white/15 bg-white/5 text-white/60 hover:border-white/30 hover:text-white/80"}
                ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
              `}
            >
              {opt.icon}
              <span className="font-medium">{opt.label}</span>
              <span className={`text-xs ${active ? "text-purple-400" : "text-white/30"}`}>
                {opt.desc}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
