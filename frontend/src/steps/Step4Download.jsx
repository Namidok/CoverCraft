import { CheckCircle } from "lucide-react"
import { useLang } from "../hooks/useLang.jsx"
import { t } from "../data/translations.js"

export default function Step4Download({ form, downloadPdf, downloadPdfDE, reset, error }) {
  const { lang } = useLang()

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-dark mb-1">{t("downloadTitle", lang)}</h2>
        <p className="text-subtle text-sm">
          {t("downloadDesc", lang)} <span className="font-semibold text-dark">{form.role}</span> {t("at", lang)} <span className="font-semibold text-dark">{form.company}</span>.
        </p>
      </div>

      {/* Download cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Cover Letter */}
        <div className="bg-white border border-border rounded-2xl p-5 space-y-3">
          <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center">
            <span className="text-xl">✉️</span>
          </div>
          <h3 className="text-dark font-bold text-sm">Cover Letter</h3>
          <div className="space-y-2">
            <button
              onClick={() => downloadPdf("cover_letter")}
              className="w-full bg-accent hover:bg-accent-hover text-white font-semibold py-2.5 rounded-xl transition-colors text-sm"
            >
              {t("downloadCoverLetter", lang)}
            </button>
            <button
              onClick={() => downloadPdfDE("cover_letter")}
              className="w-full border border-accent text-accent hover:bg-accent/5 font-semibold py-2.5 rounded-xl transition-colors text-sm"
            >
              {t("downloadCoverLetterDE", lang)}
            </button>
          </div>
        </div>

        {/* CV */}
        <div className="bg-white border border-border rounded-2xl p-5 space-y-3">
          <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center">
            <span className="text-xl">📄</span>
          </div>
          <h3 className="text-dark font-bold text-sm">ATS CV</h3>
          <div className="space-y-2">
            <button
              onClick={() => downloadPdf("cv")}
              className="w-full bg-accent hover:bg-accent-hover text-white font-semibold py-2.5 rounded-xl transition-colors text-sm"
            >
              {t("downloadCv", lang)}
            </button>
            <button
              onClick={() => downloadPdfDE("cv")}
              className="w-full border border-accent text-accent hover:bg-accent/5 font-semibold py-2.5 rounded-xl transition-colors text-sm"
            >
              {t("downloadCvDE", lang)}
            </button>
          </div>
        </div>
      </div>

      {/* ATS Tips */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5">
        <p className="text-xs font-semibold text-emerald-700 uppercase tracking-widest mb-3">{t("atsTips", lang)}</p>
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
        {t("generateAnother", lang)}
      </button>
    </div>
  )
}
