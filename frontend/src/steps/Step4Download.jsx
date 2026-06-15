export default function Step4Download({ form, downloadPdf, reset, error }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-dark mb-1">Download Documents</h2>
        <p className="text-subtle text-sm">
          Your tailored documents for <span className="font-semibold text-dark">{form.role}</span> at <span className="font-semibold text-dark">{form.company}</span> are ready.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        {/* Cover Letter */}
        <div className="bg-white border border-border rounded-2xl p-6 space-y-4">
          <div>
            <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center mb-3">
              <span className="text-xl">✉️</span>
            </div>
            <h3 className="text-dark font-bold">Cover Letter</h3>
            <p className="text-muted text-xs mt-1">
              Tailored to {form.company}'s language and values. ATS-friendly format.
            </p>
          </div>
          <button
            onClick={() => downloadPdf("cover_letter")}
            className="w-full bg-accent hover:bg-accent-hover text-white font-semibold py-3 rounded-xl transition-colors text-sm"
          >
            Download PDF
          </button>
        </div>

        {/* CV */}
        <div className="bg-white border border-border rounded-2xl p-6 space-y-4">
          <div>
            <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center mb-3">
              <span className="text-xl">📄</span>
            </div>
            <h3 className="text-dark font-bold">ATS-Optimised CV</h3>
            <p className="text-muted text-xs mt-1">
              Keywords from {form.company}'s JD injected. Google XYZ format. Single column.
            </p>
          </div>
          <button
            onClick={() => downloadPdf("cv")}
            className="w-full bg-accent hover:bg-accent-hover text-white font-semibold py-3 rounded-xl transition-colors text-sm"
          >
            Download PDF
          </button>
        </div>

      </div>

      {/* ATS tips */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5">
        <p className="text-xs font-semibold text-emerald-700 uppercase tracking-widest mb-3">ATS Tips</p>
        <ul className="space-y-1.5">
          {[
            "Submit the CV as a .pdf — not .docx",
            "Use the exact job title from the JD in your application",
            "Don't modify the CV formatting — it's optimised for ATS parsers",
            "Send the cover letter as a separate PDF attachment",
            "Follow up 7 days after applying",
          ].map((tip, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-emerald-800">
              <span className="text-emerald-500 mt-0.5">✓</span>
              {tip}
            </li>
          ))}
        </ul>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <button
        onClick={reset}
        className="w-full border border-border hover:border-accent text-subtle hover:text-accent font-semibold py-3 rounded-xl transition-colors text-sm"
      >
        Generate for Another Company →
      </button>
    </div>
  )
}
