const STEPS = [
  { value: 0.25, label: "25%", desc: "Subtle" },
  { value: 0.5, label: "50%", desc: "Balanced" },
  { value: 0.75, label: "75%", desc: "Obvious" },
  { value: 1.0, label: "100%", desc: "Maximum" },
];

export default function StrengthSlider({ value, onChange, disabled }) {
  return (
    <div>
      <label className="block text-sm font-medium text-white/70 mb-3">Processing Strength</label>
      <div className="grid grid-cols-4 gap-2">
        {STEPS.map((step) => {
          const active = value === step.value;
          return (
            <button key={step.value} onClick={() => !disabled && onChange(step.value)} disabled={disabled}
              className={`py-3 rounded-xl border text-center transition-all duration-150 ${active ? "border-purple-400 bg-purple-500/25 shadow-lg shadow-purple-500/20" : "border-white/15 bg-white/5 hover:bg-white/10 hover:border-white/30"} ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
            >
              <span className={`block text-sm font-bold ${active ? "text-purple-300" : "text-white/80"}`}>{step.label}</span>
              <span className="block text-xs text-white/40 mt-0.5">{step.desc}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
