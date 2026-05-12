const PRESETS = [
  {
    id: "natural",
    label: "Natural",
    icon: "🌿",
    tagline: "Subtle · Transparent · Realistic",
    description: "Minimal touch — removes AI sheen without changing character.",
    color: "from-emerald-600/30 to-teal-600/20",
    border: "border-emerald-500/40",
    activeBorder: "border-emerald-400",
    activeGlow: "shadow-emerald-500/20",
  },
  {
    id: "warm",
    label: "Warm",
    icon: "☀️",
    tagline: "Body · Soft top · Romantic",
    description: "More body and warmth. Great for sad, melodic, Hindi & Telugu vocals.",
    color: "from-orange-600/30 to-amber-600/20",
    border: "border-orange-500/40",
    activeBorder: "border-orange-400",
    activeGlow: "shadow-orange-500/20",
  },
  {
    id: "rap_punchy",
    label: "Rap / Punchy",
    icon: "⚡",
    tagline: "Tight · Aggressive · Upfront",
    description: "Controlled, upfront and punchy. Keeps rap vocals clean and cutting.",
    color: "from-red-600/30 to-pink-600/20",
    border: "border-red-500/40",
    activeBorder: "border-red-400",
    activeGlow: "shadow-red-500/20",
  },
];

export default function PresetSelector({ value, onChange, disabled }) {
  return (
    <div>
      <label className="block text-sm font-medium text-white/70 mb-3">Preset</label>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {PRESETS.map((p) => {
          const active = value === p.id;
          return (
            <button
              key={p.id}
              onClick={() => !disabled && onChange(p.id)}
              disabled={disabled}
              className={`
                relative text-left rounded-xl border p-4 transition-all duration-200 cursor-pointer
                bg-gradient-to-br ${p.color}
                ${active
                  ? `${p.activeBorder} shadow-lg ${p.activeGlow}`
                  : `${p.border} hover:border-white/40`}
                ${disabled ? "opacity-50 cursor-not-allowed" : ""}
              `}
            >
              {active && (
                <span className="absolute top-3 right-3 w-2 h-2 rounded-full bg-white animate-pulse" />
              )}
              <span className="text-2xl block mb-2">{p.icon}</span>
              <span className="block text-white font-semibold text-sm">{p.label}</span>
              <span className="block text-white/50 text-xs mt-0.5 mb-2">{p.tagline}</span>
              <span className="block text-white/40 text-xs leading-relaxed">{p.description}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
