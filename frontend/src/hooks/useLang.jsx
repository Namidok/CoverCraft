import { useState, useEffect, createContext, useContext } from "react"

export const LangContext = createContext()

export function useLang() {
  return useContext(LangContext)
}

export function LangProvider({ children }) {
  const [lang, setLang] = useState(() => localStorage.getItem("lang") || "en")

  useEffect(() => {
    localStorage.setItem("lang", lang)
  }, [lang])

  const toggle = () => setLang(l => l === "en" ? "de" : "en")

  return (
    <LangContext.Provider value={{ lang, toggle }}>
      {children}
    </LangContext.Provider>
  )
}
