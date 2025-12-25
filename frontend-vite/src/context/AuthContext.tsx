"use client"

import { createContext, useState, type ReactNode, useEffect } from "react"
import type { User } from "../types"

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (user: User, token: string, rememberMe?: boolean) => void
  logout: () => void
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check if user is already logged in (from localStorage or sessionStorage)
    const savedUserLocal = localStorage.getItem("user")
    const savedTokenLocal = localStorage.getItem("token")
    const savedUserSession = sessionStorage.getItem("user")
    const savedTokenSession = sessionStorage.getItem("token")

    // Check localStorage first (Remember me = true)
    if (savedUserLocal && savedTokenLocal) {
      setUser(JSON.parse(savedUserLocal))
      setIsAuthenticated(true)
      return
    }

    // Then check sessionStorage (Remember me = false)
    if (savedUserSession && savedTokenSession) {
      setUser(JSON.parse(savedUserSession))
      setIsAuthenticated(true)
      return
    }
  }, [])

  const login = (user: User, token: string, rememberMe: boolean = true) => {
    setUser(user)
    setIsAuthenticated(true)

    if (rememberMe) {
      // Store in localStorage for persistent login (Remember me checked)
      localStorage.setItem("user", JSON.stringify(user))
      localStorage.setItem("token", token)
      // Clear sessionStorage if any
      sessionStorage.removeItem("user")
      sessionStorage.removeItem("token")
    } else {
      // Store in sessionStorage for session-only login (Remember me unchecked)
      sessionStorage.setItem("user", JSON.stringify(user))
      sessionStorage.setItem("token", token)
      // Clear localStorage if any
      localStorage.removeItem("user")
      localStorage.removeItem("token")
    }
  }

  const logout = () => {
    setUser(null)
    setIsAuthenticated(false)
    // Clear both localStorage and sessionStorage
    localStorage.removeItem("user")
    localStorage.removeItem("token")
    sessionStorage.removeItem("user")
    sessionStorage.removeItem("token")
  }

  return <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>{children}</AuthContext.Provider>
}
