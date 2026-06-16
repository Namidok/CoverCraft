import { useState } from "react"

function ATSScore({ ats }) {
  if (!ats) return null

  const { overall, grade, base_score, improvement, breakdown, improvements } = ats

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

  const req = breakdown.required_skills
  const pref = breakdown.preferred_skills

  return (
    <div className="bg-white border border-border rounded-2xl overflow-hidden">
      <div className="px-5 py-4 border-b border-border bg-gray-50 flex items-center justify-between">
        <span className="text-xs font-semibold text-subtle uppercase tracking-widest">ATS Score</span>
        <div className={"text-sm font-black px-3 py-1 rounded-full border " + gradeColor}>Grade {grade}</div>
      </div>

      <div className="p-5 space-y-5">

        {/* Before / After */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center">
            <p className="text-xs text-muted mb-1">Base CV Score</p>
            <p className="text-2xl font-black text-gray-400">{base_score}/100</p>
            <p className="text-xs text-muted mt-1">Before optimisation</p>
          </div>
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
            <p className="text-xs text-muted mb-1">Optimised Score</p>
            <p className="text-2xl font-black text-emerald-600">{overall}/100</p>
            <p className="text-xs text-emerald-600 font-semibold mt-1">
              {improvement > 0 ? "+" + improvement + " improvement" : "No change"}
            </p>
          </div>
        </div>

        {/* Overall bar */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-dark">Overall ATS Score</span>
            <span className="text-xl font-black text-dark">{overall}/100</span>
          </div>
          <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
            <div className={"h-full rounded-full transition-all duration-700 " + barColor}
              style={{ width: overall + "%" }} />
          </div>
        </div>

        {/* Required skills */}
        <div className="bg-white border border-border rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-semibold text-subtle uppercase tracking-widest">Required Skills</p>
            <span className="text-sm font-bold text-dark">{req.matched_count}/{req.total}</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden mb-3">
            <div className={"h-full rounded-full " + (req.score >= 70 ? "bg-emerald-500" : req.score >= 50 ? "bg-yellow-500" : "bg-red-500")}
              style={{ width: req.score + "%" }} />
          </div>
          {req.matched.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-2">
              {req.matched.map(s => (
                <span key={s} className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-lg font-mono">✓ {s}</span>
              ))}
            </div>
          )}
          {req.missing.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {req.missing.map(s => (
                <span key={s} className="text-xs bg-red-50 text-red-600 border border-red-200 px-2 py-0.5 rounded-lg font-mono">✗ {s}</span>
              ))}
            </div>
          )}
        </div>

        {/* Preferred skills */}
        {pref.total > 0 && (
          <div className="bg-white border border-border rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <p className="text-xs font-semibold text-subtle uppercase tracking-widest">Preferred Skills</p>
              <span className="text-sm font-bold text-dark">{pref.matched_count}/{pref.total}</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden mb-3">
              <div className={"h-full rounded-full " + (pref.score >= 70 ? "bg-emerald-500" : pref.score >= 50 ? "bg-yellow-500" : "bg-red-500")}
                style={{ width: pref.score + "%" }} />
            </div>
            <div className="flex flex-wrap gap-1.5">
              {pref.matched.map(s => (
                <span key={s} className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-lg font-mono">✓ {s}</span>
              ))}
              {pref.missing.map(s => (
                <span key={s} className="text-xs bg-gray-50 text-gray-500 border border-gray-200 px-2 py-0.5 rounded-lg font-mono">○ {s}</span>
              ))}
            </div>
          </div>
        )}

        {/* Improvements */}
        {improvements.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <p className="text-xs font-semibold text-amber-700 uppercase tracking-widest mb-2">Suggestions</p>
            <ul className="space-y-1.5">
              {improvements.map((imp, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-amber-800">
                  <span className="mt-0.5 flex-shrink-0">→</span>{imp}
                </li>
              ))}
            </ul>
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
        <button onClick={() => setActiveTab("cover_letter")}
          className={"flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all " +
            (activeTab === "cover_letter" ? "bg-white text-dark shadow-sm" : "text-subtle hover:text-dark")}>
          Cover Letter
        </button>
        <button onClick={() => setActiveTab("cv")}
          className={"flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all " +
            (activeTab === "cv" ? "bg-white text-dark shadow-sm" : "text-subtle hover:text-dark")}>
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
