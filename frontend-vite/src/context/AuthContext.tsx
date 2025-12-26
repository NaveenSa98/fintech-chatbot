"use client"

import { createContext, useState, type ReactNode, useEffect } from "react"
import type { User } from "../types"
import { StorageManager } from "../services/storage"

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
    // Check if user is already logged in from storage
    const storedUser = StorageManager.getUser()
    const storedToken = StorageManager.getToken()

    if (storedUser && storedToken) {
      setUser(storedUser)
      setIsAuthenticated(true)
    }
  }, [])

  const login = (user: User, token: string, rememberMe: boolean = true) => {
    setUser(user)
    setIsAuthenticated(true)
    StorageManager.setAuth(token, user, rememberMe)
  }

  const logout = () => {
    setUser(null)
    setIsAuthenticated(false)
    StorageManager.clearAuth()
  }

  return <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>{children}</AuthContext.Provider>
}
