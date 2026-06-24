import { useState, useRef, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Upload, FileText, CheckCircle } from "lucide-react"
import axios from "axios"
import { supabase } from "../lib/supabase"
import toast from "react-hot-toast"

export default function CVUpload() {
  const [file, setFile] = useState(null)
  const [mode, setMode] = useState("file")
  const [text, setText] = useState("")
  const [uploading, setUploading] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState("")
  const [checking, setChecking] = useState(true)
  const fileRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    checkCVUploaded()
  }, [])

  const checkCVUploaded = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    const { data } = await supabase
      .from("user_profiles")
      .select("cv_uploaded")
      .eq("id", session.user.id)
      .single()

    if (data?.cv_uploaded) {
      navigate("/app")
      return
    }
    setChecking(false)
  }

  const markCVUploaded = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (!session) return

    const { data } = await supabase
      .from("user_profiles")
      .select("id")
      .eq("id", session.user.id)
      .single()

    if (data) {
      await supabase
        .from("user_profiles")
        .update({ cv_uploaded: true })
        .eq("id", session.user.id)
    } else {
      await supabase
        .from("user_profiles")
        .insert({ id: session.user.id, cv_uploaded: true })
    }
  }

  const handleFileChange = (e) => {
    const f = e.target.files[0]
    if (!f) return
    setFile(f)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (!f) return
    setFile(f)
  }

  const handleUpload = async () => {
    setUploading(true)
    setError("")
    try {
      const { data: { session } } = await supabase.auth.getSession()
      const authHeader = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {}

      if (mode === "file") {
        if (!file) { setError("Please select a file."); setUploading(false); return }
        const formData = new FormData()
        formData.append("file", file)
        await axios.post("/api/upload-cv-pdf", formData, {
          headers: { ...authHeader, "Content-Type": "multipart/form-data" }
        })
      } else {
        if (!text.trim()) { setError("Please paste your CV text."); setUploading(false); return }
        await axios.post("/api/upload-cv-text", { text }, { headers: authHeader })
      }
      await markCVUploaded()
      setDone(true)
      toast.success("CV uploaded successfully!")
      setTimeout(() => navigate("/app"), 1500)
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed. Please try again.")
      toast.error("Upload failed")
    } finally {
      setUploading(false)
    }
  }

  if (checking) return (
    <div className="min-h-screen bg-surface flex items-center justify-center">
      <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin" />
    </div>
  )

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <nav className="border-b border-border bg-white px-6 py-4 flex items-center justify-between">
        <span className="text-dark font-black text-lg">Cover<span className="text-accent">Craft</span></span>
        <button
          onClick={() => supabase.auth.signOut()}
          className="text-xs text-subtle hover:text-dark transition-colors"
        >
          Sign out
        </button>
      </nav>
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-lg">
          <div className="text-center mb-8">
            <div className="w-12 h-12 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FileText size={24} className="text-accent" />
            </div>
            <h1 className="text-2xl font-bold text-dark mb-2">Upload your CV</h1>
            <p className="text-subtle text-sm">Upload once — we use it as context for every cover letter and CV we generate for you.</p>
          </div>
          <div className="bg-white border border-border rounded-2xl p-6 shadow-sm space-y-5">
            <div className="flex gap-2 bg-gray-100 p-1 rounded-xl">
              <button
                onClick={() => setMode("file")}
                className={"flex-1 py-2 rounded-lg text-sm font-semibold transition-all " +
                  (mode === "file" ? "bg-white text-dark shadow-sm" : "text-subtle hover:text-dark")}
              >
                Upload PDF
              </button>
              <button
                onClick={() => setMode("paste")}
                className={"flex-1 py-2 rounded-lg text-sm font-semibold transition-all " +
                  (mode === "paste" ? "bg-white text-dark shadow-sm" : "text-subtle hover:text-dark")}
              >
                Paste Text
              </button>
            </div>

            {mode === "file" ? (
              <div
                onDrop={handleDrop}
                onDragOver={e => e.preventDefault()}
                onClick={() => fileRef.current.click()}
                className="border-2 border-dashed border-border hover:border-accent rounded-xl p-8 text-center cursor-pointer transition-colors group"
              >
                <input ref={fileRef} type="file" accept=".pdf" onChange={handleFileChange} className="hidden" />
                <Upload size={32} className="text-muted group-hover:text-accent mx-auto mb-3 transition-colors" />
                {file ? (
                  <div>
                    <p className="text-dark font-semibold text-sm">{file.name}</p>
                    <p className="text-muted text-xs mt-1">Click to change</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-dark font-medium text-sm">Drop your CV PDF here or click to browse</p>
                    <p className="text-muted text-xs mt-1">PDF files only</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-xs text-muted">Paste your CV as plain text</p>
                <textarea
                  value={text}
                  onChange={e => setText(e.target.value)}
                  placeholder="Paste your CV text here..."
                  rows={10}
                  className="w-full border border-border rounded-xl px-4 py-3 text-sm text-dark placeholder-muted focus:outline-none focus:border-accent resize-none"
                />
              </div>
            )}

            {error && <p className="text-red-500 text-sm">{error}</p>}

            {done ? (
              <div className="flex items-center justify-center gap-2 text-accent font-semibold py-3">
                <CheckCircle size={18} />
                CV uploaded! Redirecting...
              </div>
            ) : (
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="w-full bg-accent hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors text-sm"
              >
                {uploading ? "Uploading..." : "Upload CV & Continue →"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
