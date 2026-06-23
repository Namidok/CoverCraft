import { useNavigate } from "react-router-dom"

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <nav className="border-b border-border bg-white px-6 py-4 flex items-center justify-between">
        <span className="text-dark font-black text-lg">Cover<span className="text-accent">Craft</span></span>
        <button
          onClick={() => navigate("/login")}
          className="bg-accent hover:bg-accent-hover text-white text-sm font-semibold px-5 py-2 rounded-lg transition-colors"
        >
          Get Started
        </button>
      </nav>
      <div className="flex-1 flex flex-col items-center justify-center px-6 text-center py-20">
        <h1 className="text-5xl md:text-7xl font-black text-dark leading-tight mb-6">
          Land the job with<br /><span className="text-accent">AI-tailored</span> documents
        </h1>
        <p className="text-subtle text-lg max-w-xl mb-10 leading-relaxed">
          Paste any job description. Get a tailored cover letter, ATS-optimised CV, and skill gap analysis in seconds.
        </p>
        <div className="flex gap-4">
          <button
            onClick={() => navigate("/login")}
            className="bg-accent hover:bg-accent-hover text-white font-bold px-8 py-4 rounded-xl transition-all hover:scale-105 text-sm"
          >
            Start for free →
          </button>
          <a href="#how" className="border border-border text-subtle hover:text-dark font-medium px-8 py-4 rounded-xl transition-colors text-sm">
            How it works
          </a>
        </div>
      </div>
      <div id="how" className="max-w-4xl mx-auto px-6 pb-20 w-full">
        <p className="text-xs text-accent uppercase tracking-widest text-center mb-10 font-semibold">How it works</p>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { step: "01", title: "Upload your CV", desc: "Upload once. We use it as context for every application." },
            { step: "02", title: "Paste the JD", desc: "Copy any job description and paste it in. We analyse it instantly." },
            { step: "03", title: "See your gaps", desc: "Know exactly which skills match and which you need to develop." },
            { step: "04", title: "Download PDFs", desc: "Get a tailored cover letter and ATS-optimised CV ready to send." },
          ].map(({ step, title, desc }) => (
            <div key={step} className="bg-white border border-border rounded-2xl p-5">
              <p className="text-accent font-black text-2xl mb-3">{step}</p>
              <p className="text-dark font-bold text-sm mb-2">{title}</p>
              <p className="text-muted text-xs leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>
      <footer className="text-center py-6 text-muted text-xs border-t border-border">
        CoverCraft · 2026
      </footer>
    </div>
  )
}
