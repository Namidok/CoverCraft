import SkillBadge from "../components/SkillBadge"

export default function Step2SkillGap({ skillGap, form, generate, loading, error, setStep }) {
  if (!skillGap) return null

  const { matched, missing, coverage_pct, total_required, total_matched, total_missing } = skillGap

  const coverageColor = coverage_pct >= 70
    ? "bg-emerald-500"
    : coverage_pct >= 40
    ? "bg-yellow-500"
    : "bg-red-500"

  const coverageText = coverage_pct >= 70
    ? "Strong match"
    : coverage_pct >= 40
    ? "Moderate match"
    : "Weak match"

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-dark mb-1">Skill Gap Analysis</h2>
        <p className="text-subtle text-sm">
          Here's how your profile matches <span className="font-semibold text-dark">{form.role}</span> at <span className="font-semibold text-dark">{form.company}</span>
        </p>
      </div>

      {/* Coverage bar */}
      <div className="bg-white border border-border rounded-2xl p-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-dark">Overall Coverage</span>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-black text-dark">{coverage_pct}%</span>
            <span className={"text-xs font-semibold px-2 py-0.5 rounded-full " +
              (coverage_pct >= 70 ? "bg-emerald-100 text-emerald-700" :
               coverage_pct >= 40 ? "bg-yellow-100 text-yellow-700" :
               "bg-red-100 text-red-600")
            }>{coverageText}</span>
          </div>
        </div>
        <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={"h-full rounded-full transition-all duration-700 " + coverageColor}
            style={{ width: coverage_pct + "%" }}
          />
        </div>
        <div className="flex justify-between mt-3 text-xs text-muted">
          <span>{total_required} skills required</span>
          <span>{total_matched} matched · {total_missing} missing</span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white border border-border rounded-xl p-4 text-center">
          <p className="text-2xl font-black text-dark">{total_required}</p>
          <p className="text-xs text-muted mt-1">Required</p>
        </div>
        <div className="bg-white border border-emerald-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-black text-emerald-600">{total_matched}</p>
          <p className="text-xs text-muted mt-1">Matched</p>
        </div>
        <div className="bg-white border border-red-200 rounded-xl p-4 text-center">
          <p className="text-2xl font-black text-red-500">{total_missing}</p>
          <p className="text-xs text-muted mt-1">Missing</p>
        </div>
      </div>

      {/* Matched skills */}
      {matched.length > 0 && (
        <div className="bg-white border border-border rounded-2xl p-5">
          <p className="text-xs font-semibold text-subtle uppercase tracking-widest mb-3">Your Matched Skills</p>
          <div className="flex flex-wrap gap-2">
            {matched.map(s => <SkillBadge key={s} skill={s} type="matched" />)}
          </div>
        </div>
      )}

      {/* Missing skills */}
      {missing.length > 0 && (
        <div className="bg-white border border-border rounded-2xl p-5">
          <p className="text-xs font-semibold text-subtle uppercase tracking-widest mb-3">Skills to Develop</p>
          <div className="flex flex-wrap gap-2">
            {missing.map(s => <SkillBadge key={s} skill={s} type="missing" />)}
          </div>
        </div>
      )}

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <div className="flex gap-3">
        <button
          onClick={() => setStep(1)}
          className="px-6 py-3 border border-border rounded-xl text-sm font-medium text-subtle hover:text-dark transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={generate}
          disabled={loading}
          className="flex-1 bg-accent hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors text-sm"
        >
          {loading ? "Generating documents..." : "Generate Cover Letter + CV →"}
        </button>
      </div>
    </div>
  )
}
