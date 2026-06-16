import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { useState, useEffect } from "react"
import { supabase } from "./lib/supabase"
import Landing from "./pages/Landing"
import Auth from "./components/Auth"
import CVUpload from "./pages/CVUpload"
import StepIndicator from "./components/StepIndicator"
import Step1JobDetails from "./steps/Step1JobDetails"
import Step2SkillGap from "./steps/Step2SkillGap"
import Step3Generate from "./steps/Step3Generate"
import Step4Download from "./steps/Step4Download"
import useCoverCraft from "./hooks/useCoverCraft"

function AppFlow() {
  const {
    step, setStep,
    form, setForm,
    skillGap,
    coverLetter,
    customCv,
    atsScore,
    loading,
    error,
    analyseGap,
    generate,
    downloadPdf,
    reset,
  } = useCoverCraft()

  return (
    <div className="min-h-screen bg-surface">
      <header className="border-b border-border bg-white sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <span className="text-dark font-black text-lg tracking-tight">Cover<span className="text-accent">Craft</span></span>
            <p className="text-muted text-xs">AI-powered cover letters and CV optimisation</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted border border-border px-3 py-1 rounded-full">Powered by RAG + Llama 3.3</span>
            <button
              onClick={() => supabase.auth.signOut()}
              className="text-xs text-subtle hover:text-dark transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>
      <main className="max-w-2xl mx-auto px-6 py-10">
        <StepIndicator current={step} />
        <div className="bg-white border border-border rounded-2xl p-8 shadow-sm">
          {step === 1 && <Step1JobDetails form={form} setForm={setForm} analyseGap={analyseGap} loading={loading} error={error} />}
          {step === 2 && <Step2SkillGap skillGap={skillGap} form={form} generate={generate} loading={loading} error={error} setStep={setStep} />}
          {step === 3 && <Step3Generate coverLetter={coverLetter} customCv={customCv} atsScore={atsScore} form={form} setStep={setStep} downloadPdf={downloadPdf} error={error} />}
          {step === 4 && <Step4Download form={form} downloadPdf={downloadPdf} reset={reset} error={error} />}
        </div>
      </main>
      <footer className="text-center py-8 text-muted text-xs">CoverCraft · Built by Srikar Kodi · 2026</footer>
    </div>
  )
}

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
    })
    return () => subscription.unsubscribe()
  }, [])

  if (loading) return (
    <div className="min-h-screen bg-surface flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
    </div>
  )

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={user ? <Navigate to="/upload-cv" /> : <Auth />} />
        <Route path="/upload-cv" element={user ? <CVUpload /> : <Navigate to="/login" />} />
        <Route path="/app" element={user ? <AppFlow /> : <Navigate to="/login" />} />
        <Route path="/*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}
