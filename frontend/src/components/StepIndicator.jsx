const STEPS = [
  { number: 1, label: "Job Details" },
  { number: 2, label: "Skill Gap" },
  { number: 3, label: "Preview" },
  { number: 4, label: "Download" },
]

export default function StepIndicator({ current }) {
  return (
    <div className="flex items-center justify-center mb-10">
      {STEPS.map(({ number, label }, i) => (
        <div key={number} className="flex items-center">
          <div className="flex flex-col items-center">
            <div className={"w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold transition-all " +
              (current === number
                ? "bg-accent text-white shadow-lg shadow-accent/30"
                : current > number
                ? "bg-accent/20 text-accent"
                : "bg-gray-100 text-gray-400")
            }>
              {current > number ? "✓" : number}
            </div>
            <span className={"text-xs mt-1.5 font-medium " +
              (current >= number ? "text-accent" : "text-gray-400")
            }>
              {label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={"h-0.5 w-16 mx-2 mb-4 transition-all " +
              (current > number ? "bg-accent/40" : "bg-gray-200")
            } />
          )}
        </div>
      ))}
    </div>
  )
}
