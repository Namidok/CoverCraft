import { useState } from "react"
import toast from "react-hot-toast"
import axios from "axios"
import { supabase } from "../lib/supabase"

export default function useCoverCraft() {
  const [step, setStep] = useState(1)
  const [form, setForm] = useState({ company: "", role: "", jd_text: "" })
  const [skillGap, setSkillGap] = useState(null)
  const [coverLetter, setCoverLetter] = useState("")
  const [customCv, setCustomCv] = useState("")
  const [atsScore, setAtsScore] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const getAuthHeader = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    const token = session?.access_token
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  const analyseGap = async () => {
    if (!form.company || !form.role || !form.jd_text) {
      setError("Please fill in all fields.")
      return
    }
    setLoading(true)
    setError("")
    try {
      const headers = await getAuthHeader()
      const res = await axios.post("/api/add-jd", form, { headers })
      setSkillGap(res.data.skill_gap)
      setStep(2)
      toast.success("JD analysed successfully")
    } catch {
      setError("Failed to analyse JD. Is the backend running?")
      toast.error("Failed to analyse JD")
    } finally {
      setLoading(false)
    }
  }

  const generate = async () => {
    setLoading(true)
    setError("")
    try {
      const headers = await getAuthHeader()
      const res = await axios.post("/api/generate-all", form, { headers })
      setCoverLetter(res.data.cover_letter)
      setCustomCv(res.data.cv)
      setAtsScore(res.data.ats_score)
      setStep(3)
      toast.success("Documents generated!")
    } catch {
      setError("Generation failed. Please try again.")
      toast.error("Generation failed")
    } finally {
      setLoading(false)
    }
  }

  const downloadPdfDE = async (type) => {
    try {
      const headers = await getAuthHeader()
      const endpoint = type === "cover_letter"
        ? "/api/download-cover-letter-pdf-de"
        : "/api/download-cv-pdf-de"
      const res = await axios.post(endpoint, form, { headers, responseType: "blob" })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement("a")
      link.href = url
      link.setAttribute("download", type === "cover_letter"
        ? `cover_letter_${form.company}_DE.pdf`
        : `cv_${form.company}_DE.pdf`
      )
      document.body.appendChild(link)
      link.click()
      link.remove()
      toast.success("German PDF downloaded!")
    } catch {
      toast.error("German download failed")
    }
  }

  const downloadPdf = async (type) => {
    try {
      const endpoint = type === "cover_letter"
        ? "/api/download-cover-letter-pdf"
        : "/api/download-cv-pdf"
      const headers = await getAuthHeader()
      const res = await axios.post(endpoint, form, { headers, responseType: "blob" })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement("a")
      link.href = url
      link.setAttribute("download", type === "cover_letter"
        ? "cover_letter_" + form.company + ".pdf"
        : "cv_" + form.company + ".pdf"
      )
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch {
      setError("Download failed. Please try again.")
      toast.error("Download failed")
    }
  }

  const reset = () => {
    setStep(1)
    setForm({ company: "", role: "", jd_text: "" })
    setSkillGap(null)
    setCoverLetter("")
    setCustomCv("")
    setAtsScore(null)
    setError("")
  }

  return {
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
    downloadPdfDE,
    reset,
  }
}
