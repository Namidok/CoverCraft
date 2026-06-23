import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { supabase } from "../lib/supabase"
import { CheckCircle, Upload, FileText } from "lucide-react"
import axios from "axios"

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [cvFile, setCvFile] = useState(null)
  const [uploadingCv, setUploadingCv] = useState(false)
  const [cvSuccess, setCvSuccess] = useState(false)
  const fileRef = useState(null)
  const navigate = useNavigate()

  useEffect(() => { fetchProfile() }, [])

  const fetchProfile = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    const user = session?.user
    if (!user) return

    const { data } = await supabase
      .from("user_profiles")
      .select("*")
      .eq("id", user.id)
      .single()

    const profileData = {
      id: user.id,
      full_name: user.user_metadata?.full_name || "",
      email: user.email,
      avatar_url: user.user_metadata?.avatar_url || "",
      target_role: data?.target_role || "",
      target_location: data?.target_location || "",
      available_date: data?.available_date || "",
      cv_uploaded: data?.cv_uploaded || false,
    }

    setProfile(profileData)
    setForm(profileData)
    setLoading(false)
  }

  const handleSave = async () => {
    setSaving(true)
    await supabase.from("user_profiles").upsert({
      id: profile.id,
      target_role: form.target_role,
      target_location: form.target_location,
      available_date: form.available_date,
      cv_uploaded: profile.cv_uploaded,
    })
    setProfile(form)
    setEditing(false)
    setSuccess(true)
    setTimeout(() => setSuccess(false), 3000)
    setSaving(false)
  }

  const handleCvUpload = async (e) => {
    const f = e.target.files[0]
    if (!f) return
    setCvFile(f)
    setUploadingCv(true)
    try {
      const formData = new FormData()
      formData.append("file", f)
      await axios.post("/api/upload-cv-pdf", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
      await supabase.from("user_profiles").upsert({
        id: profile.id,
        cv_uploaded: true,
      })
      setCvSuccess(true)
      setTimeout(() => setCvSuccess(false), 3000)
    } catch {
      alert("Upload failed. Please try again.")
    } finally {
      setUploadingCv(false)
    }
  }

  if (loading) return (
    <div className="min-h-screen bg-surface flex items-center justify-center">
      <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin" />
    </div>
  )

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <nav className="border-b border-border bg-white px-6 py-4 flex items-center justify-between">
        <span className="text-dark font-black text-lg">Cover<span className="text-accent">Craft</span></span>
        <div className="flex items-center gap-4">
          <button onClick={() => navigate("/app")} className="text-xs text-subtle hover:text-dark transition-colors">← Back to App</button>
          <button onClick={() => supabase.auth.signOut()} className="text-xs text-subtle hover:text-dark transition-colors">Sign out</button>
        </div>
      </nav>

      <div className="max-w-xl mx-auto w-full px-6 py-10 space-y-6">

        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-dark">Profile</h1>
          {!editing && (
            <button
              onClick={() => setEditing(true)}
              className="bg-accent hover:bg-accent-hover text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              Edit Profile
            </button>
          )}
        </div>

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
            <CheckCircle size={16} /> Profile updated successfully
          </div>
        )}

        {/* Avatar + basic info */}
        <div className="bg-white border border-border rounded-2xl p-6 flex items-center gap-5 shadow-sm">
          {profile?.avatar_url
            ? <img src={profile.avatar_url} alt="avatar" className="w-16 h-16 rounded-full" />
            : <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center text-accent text-2xl font-bold">
                {profile?.full_name?.[0]?.toUpperCase()}
              </div>
          }
          <div>
            <p className="text-dark font-bold text-lg">{profile?.full_name}</p>
            <p className="text-subtle text-sm">{profile?.email}</p>
          </div>
        </div>

        {/* Job search details */}
        <div className="bg-white border border-border rounded-2xl p-6 shadow-sm space-y-5">
          <p className="text-xs text-muted uppercase tracking-widest font-semibold">Job Search</p>

          <div className="space-y-1.5">
            <label className="text-xs text-muted uppercase tracking-widest">Target Role</label>
            {editing
              ? <input type="text" value={form.target_role || ""} onChange={e => setForm(p => ({ ...p, target_role: e.target.value }))}
                  placeholder="e.g. AI/ML Engineer" className="w-full border border-border rounded-lg px-3 py-2.5 text-sm text-dark focus:outline-none focus:border-accent" />
              : <p className="text-dark text-sm">{profile?.target_role || "—"}</p>
            }
          </div>

          <div className="space-y-1.5">
            <label className="text-xs text-muted uppercase tracking-widest">Target Location</label>
            {editing
              ? <input type="text" value={form.target_location || ""} onChange={e => setForm(p => ({ ...p, target_location: e.target.value }))}
                  placeholder="e.g. London, Remote" className="w-full border border-border rounded-lg px-3 py-2.5 text-sm text-dark focus:outline-none focus:border-accent" />
              : <p className="text-dark text-sm">{profile?.target_location || "—"}</p>
            }
          </div>

          <div className="space-y-1.5">
            <label className="text-xs text-muted uppercase tracking-widest">Available From</label>
            {editing
              ? <input type="date" value={form.available_date || ""} onChange={e => setForm(p => ({ ...p, available_date: e.target.value }))}
                  className="w-full border border-border rounded-lg px-3 py-2.5 text-sm text-dark focus:outline-none focus:border-accent" />
              : <p className="text-dark text-sm">{profile?.available_date || "—"}</p>
            }
          </div>
        </div>

        {/* CV section */}
        <div className="bg-white border border-border rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-muted uppercase tracking-widest font-semibold">Your CV</p>
            {profile?.cv_uploaded && (
              <span className="text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-0.5 rounded-full">Uploaded</span>
            )}
          </div>
          <p className="text-subtle text-sm">Upload a new CV to replace the existing one used for generation.</p>

          {cvSuccess && (
            <div className="bg-green-50 border border-green-200 text-green-700 rounded-xl px-4 py-3 text-sm flex items-center gap-2">
              <CheckCircle size={16} /> CV updated successfully
            </div>
          )}

          <label className="flex items-center justify-center gap-3 border-2 border-dashed border-border hover:border-accent rounded-xl p-5 cursor-pointer transition-colors group">
            <input type="file" accept=".pdf" onChange={handleCvUpload} className="hidden" />
            {uploadingCv
              ? <div className="w-5 h-5 border-2 border-accent border-t-transparent rounded-full animate-spin" />
              : <Upload size={20} className="text-muted group-hover:text-accent transition-colors" />
            }
            <span className="text-sm text-subtle group-hover:text-dark transition-colors">
              {cvFile ? cvFile.name : "Click to upload new CV (PDF)"}
            </span>
          </label>
        </div>

        {editing && (
          <div className="flex gap-3">
            <button onClick={() => { setEditing(false); setForm(profile) }}
              className="px-6 py-2.5 border border-border text-subtle hover:text-dark rounded-lg text-sm transition-colors">
              Cancel
            </button>
            <button onClick={handleSave} disabled={saving}
              className="flex-1 bg-accent hover:bg-accent-hover disabled:opacity-50 text-white font-medium py-2.5 rounded-lg text-sm transition-colors">
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        )}

      </div>
    </div>
  )
}
