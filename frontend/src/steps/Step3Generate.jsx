import { useState } from "react"

export default function Step3Generate({ coverLetter, customCv, form, setStep, downloadPdf, error }) {
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

      {/* Tabs */}
      <div className="flex gap-2 bg-gray-100 p-1 rounded-xl">
        <button
          onClick={() => setActiveTab("cover_letter")}
          className={"flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all " +
            (activeTab === "cover_letter"
              ? "bg-white text-dark shadow-sm"
              : "text-subtle hover:text-dark")
          }
        >
          Cover Letter
        </button>
        <button
          onClick={() => setActiveTab("cv")}
          className={"flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all " +
            (activeTab === "cv"
              ? "bg-white text-dark shadow-sm"
              : "text-subtle hover:text-dark")
          }
        >
          ATS CV
        </button>
      </div>

      {/* Preview */}
      <div className="bg-white border border-border rounded-2xl overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-gray-50">
          <span className="text-xs font-semibold text-subtle uppercase tracking-widest">
            {activeTab === "cover_letter" ? "Cover Letter Preview" : "ATS-Optimised CV Preview"}
          </span>
          <button
            onClick={copyToClipboard}
            className="text-xs text-accent hover:text-accent-hover font-semibold transition-colors"
          >
            {copied ? "Copied!" : "Copy to clipboard"}
          </button>
        </div>
        <div className="p-6 max-h-96 overflow-y-auto">
          <pre className="text-sm text-dark leading-relaxed whitespace-pre-wrap font-sans">
            {activeContent}
          </pre>
        </div>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <div className="flex gap-3">
        <button
          onClick={() => setStep(2)}
          className="px-6 py-3 border border-border rounded-xl text-sm font-medium text-subtle hover:text-dark transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={() => setStep(4)}
          className="flex-1 bg-accent hover:bg-accent-hover text-white font-semibold py-3 rounded-xl transition-colors text-sm"
        >
          Download PDFs →
        </button>
      </div>
    </div>
  )
}
