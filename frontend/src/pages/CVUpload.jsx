import { useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import { Upload, FileText, CheckCircle } from "lucide-react"
import axios from "axios"

export default function CVUpload() {
  const [file, setFile] = useState(null)
  const [text, setText] = useState("")
  const [mode, setMode] = useState("paste")
  const [uploading, setUploading] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState("")
  const fileRef = useRef(null)
  const navigate = useNavigate()

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
      if (mode === "file") {
        if (!file) { setError("Please select a file."); setUploading(false); return }
        const formData = new FormData()
        formData.append("file", file)
        await axios.post("/api/upload-cv-pdf", formData, {
          headers: { "Content-Type": "multipart/form-data" }
        })
      } else {
        if (!text.trim()) { setError("Please paste your CV text."); setUploading(false); return }
        await axios.post("/api/upload-cv-text", { text })
      }
      setDone(true)
      setTimeout(() => navigate("/app"), 1500)
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed. Is the backend running?")
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <nav className="border-b border-border bg-white px-6 py-4">
        <span className="text-dark font-black text-lg">Cover<span className="text-accent">Craft</span></span>
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
                <p className="text-xs text-muted">Paste your CV as plain text — copy from your PDF or Word doc</p>
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
          <p className="text-center text-muted text-xs mt-4">
            Already uploaded before?{" "}
            <button onClick={() => navigate("/app")} className="text-accent hover:underline">
              Skip to app →
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
