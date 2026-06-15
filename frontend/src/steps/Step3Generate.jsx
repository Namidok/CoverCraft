import { useState } from "react"

function ATSScore({ ats }) {
  if (!ats) return null

  const { overall, grade, breakdown, improvements } = ats

  const gradeColor = grade === "A"
    ? "text-emerald-600 bg-emerald-50 border-emerald-200"
    : grade === "B"
    ? "text-blue-600 bg-blue-50 border-blue-200"
    : grade === "C"
    ? "text-yellow-600 bg-yellow-50 border-yellow-200"
    : "text-red-600 bg-red-50 border-red-200"

  const barColor = overall >= 85 ? "bg-emerald-500"
    : overall >= 70 ? "bg-blue-500"
    : overall >= 55 ? "bg-yellow-500"
    : "bg-red-500"

  const categories = [
    { label: "Keywords", score: breakdown.keywords.score, weight: "40%" },
    { label: "Sections", score: breakdown.sections.score, weight: "20%" },
    { label: "Action Verbs", score: breakdown.action_verbs.score, weight: "20%" },
    { label: "Format", score: breakdown.format.score, weight: "10%" },
    { label: "Length", score: breakdown.length.score, weight: "10%" },
  ]

  return (
    <div className="bg-white border border-border rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-border bg-gray-50 flex items-center justify-between">
        <span className="text-xs font-semibold text-subtle uppercase tracking-widest">ATS Score</span>
        <div className={"text-sm font-black px-3 py-1 rounded-full border " + gradeColor}>
          Grade {grade}
        </div>
      </div>

      <div className="p-5 space-y-4">
        {/* Overall score */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-dark">Overall Score</span>
            <span className="text-2xl font-black text-dark">{overall}/100</span>
          </div>
          <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
            <div className={"h-full rounded-full transition-all duration-700 " + barColor}
              style={{ width: overall + "%" }} />
          </div>
        </div>

        {/* Category breakdown */}
        <div className="space-y-2">
          {categories.map(({ label, score, weight }) => (
            <div key={label} className="flex items-center gap-3">
              <span className="text-xs text-subtle w-24">{label}</span>
              <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className={"h-full rounded-full " + (score >= 70 ? "bg-emerald-400" : score >= 50 ? "bg-yellow-400" : "bg-red-400")}
                  style={{ width: score + "%" }}
                />
              </div>
              <span className="text-xs font-semibold text-dark w-8">{score}</span>
              <span className="text-xs text-muted w-8">{weight}</span>
            </div>
          ))}
        </div>

        {/* Improvements */}
        {improvements.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <p className="text-xs font-semibold text-amber-700 uppercase tracking-widest mb-2">Suggestions</p>
            <ul className="space-y-1.5">
              {improvements.map((imp, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-amber-800">
                  <span className="mt-0.5">→</span>{imp}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Missing keywords */}
        {breakdown.keywords.top_missing?.length > 0 && (
          <div>
            <p className="text-xs text-subtle mb-2">Missing JD keywords:</p>
            <div className="flex flex-wrap gap-1.5">
              {breakdown.keywords.top_missing.map(k => (
                <span key={k} className="text-xs bg-red-50 text-red-600 border border-red-200 px-2 py-0.5 rounded-lg font-mono">{k}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function Step3Generate({ coverLetter, customCv, atsScore, form, setStep, downloadPdf, error }) {
  const [activeTab, setActiveTab] = useState("cover_letter")
  const [copied, setCopied] = useState(false)

  const activeContent = activeTab === "cover_letter" ? coverLetter : customCv

  const copyToClipboard = () => {
    navigator.clipboard.writeText(activeContent)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-dark mb-1">Preview Documents</h2>
        <p className="text-subtle text-sm">
          Tailored for <span className="font-semibold text-dark">{form.role}</span> at <span className="font-semibold text-dark">{form.company}</span>
        </p>
      </div>

      <div className="flex gap-2 bg-gray-100 p-1 rounded-xl">
        <button
          onClick={() => setActiveTab("cover_letter")}
          className={"flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all " +
            (activeTab === "cover_letter" ? "bg-white text-dark shadow-sm" : "text-subtle hover:text-dark")}
        >
          Cover Letter
        </button>
        <button
          onClick={() => setActiveTab("cv")}
          className={"flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all " +
            (activeTab === "cv" ? "bg-white text-dark shadow-sm" : "text-subtle hover:text-dark")}
        >
          ATS CV
        </button>
      </div>

      <div className="bg-white border border-border rounded-2xl overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-gray-50">
          <span className="text-xs font-semibold text-subtle uppercase tracking-widest">
            {activeTab === "cover_letter" ? "Cover Letter Preview" : "ATS-Optimised CV Preview"}
          </span>
          <button onClick={copyToClipboard} className="text-xs text-accent hover:text-accent-hover font-semibold transition-colors">
            {copied ? "Copied!" : "Copy to clipboard"}
          </button>
        </div>
        <div className="p-6 max-h-80 overflow-y-auto">
          <pre className="text-sm text-dark leading-relaxed whitespace-pre-wrap font-sans">{activeContent}</pre>
        </div>
      </div>

      {activeTab === "cv" && <ATSScore ats={atsScore} />}

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <div className="flex gap-3">
        <button onClick={() => setStep(2)} className="px-6 py-3 border border-border rounded-xl text-sm font-medium text-subtle hover:text-dark transition-colors">
          ← Back
        </button>
        <button onClick={() => setStep(4)} className="flex-1 bg-accent hover:bg-accent-hover text-white font-semibold py-3 rounded-xl transition-colors text-sm">
          Download PDFs →
        </button>
      </div>
    </div>
  )
}
