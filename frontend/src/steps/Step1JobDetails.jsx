export default function Step1JobDetails({ form, setForm, analyseGap, loading, error }) {
  const set = (field, value) => setForm(prev => ({ ...prev, [field]: value }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-dark mb-1">Job Details</h2>
        <p className="text-subtle text-sm">Paste the job description and we'll analyse your fit instantly.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-subtle uppercase tracking-widest">Company *</label>
          <input
            type="text"
            value={form.company}
            onChange={e => set("company", e.target.value)}
            placeholder="e.g. Celonis"
            className="w-full border border-border rounded-xl px-4 py-3 text-sm text-dark placeholder-muted focus:outline-none focus:border-accent transition-colors bg-white"
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-subtle uppercase tracking-widest">Role *</label>
          <input
            type="text"
            value={form.role}
            onChange={e => set("role", e.target.value)}
            placeholder="e.g. AI/ML Engineer"
            className="w-full border border-border rounded-xl px-4 py-3 text-sm text-dark placeholder-muted focus:outline-none focus:border-accent transition-colors bg-white"
          />
        </div>
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-subtle uppercase tracking-widest">Job Description *</label>
        <textarea
          value={form.jd_text}
          onChange={e => set("jd_text", e.target.value)}
          placeholder="Paste the full job description here — we'll extract required skills, analyse your gaps, and generate tailored documents..."
          rows={10}
          className="w-full border border-border rounded-xl px-4 py-3 text-sm text-dark placeholder-muted focus:outline-none focus:border-accent transition-colors bg-white resize-none"
        />
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={analyseGap}
        disabled={loading || !form.company || !form.role || !form.jd_text}
        className="w-full bg-accent hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3.5 rounded-xl transition-colors text-sm"
      >
        {loading ? "Analysing..." : "Analyse Skill Fit →"}
      </button>
    </div>
  )
}
