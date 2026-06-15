export default function SkillBadge({ skill, type }) {
  const styles = {
    matched: "bg-emerald-50 text-emerald-700 border border-emerald-200",
    missing: "bg-red-50 text-red-600 border border-red-200",
    neutral: "bg-gray-50 text-gray-600 border border-gray-200",
  }
  return (
    <span className={"inline-block px-2.5 py-1 rounded-lg text-xs font-mono font-medium " + styles[type]}>
      {skill}
    </span>
  )
}
