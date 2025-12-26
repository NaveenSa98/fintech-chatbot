import type { User } from "../types"

/**
 * Storage Manager - Centralized auth token and user data management
 * Handles both localStorage (persistent) and sessionStorage (session-only) storage
 * Eliminates duplicate cleanup logic across the application
 */
export const StorageManager = {
  /**
   * Clear all authentication data from both storage types
   */
  clearAuth(): void {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    sessionStorage.removeItem("token")
    sessionStorage.removeItem("user")
  },

  /**
   * Clear only localStorage auth data
   */
  clearLocalAuth(): void {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
  },

  /**
   * Clear only sessionStorage auth data
   */
  clearSessionAuth(): void {
    sessionStorage.removeItem("token")
    sessionStorage.removeItem("user")
  },

  /**
   * Store authentication credentials
   * @param token - JWT token
   * @param user - User object
   * @param rememberMe - If true, use localStorage (persistent); if false, use sessionStorage
   */
  setAuth(token: string, user: User, rememberMe: boolean = true): void {
    if (rememberMe) {
      // Persistent storage (Remember Me checked)
      localStorage.setItem("token", token)
      localStorage.setItem("user", JSON.stringify(user))
      // Clear session storage if any
      this.clearSessionAuth()
    } else {
      // Session storage only (Remember Me unchecked)
      sessionStorage.setItem("token", token)
      sessionStorage.setItem("user", JSON.stringify(user))
      // Clear localStorage if any
      this.clearLocalAuth()
    }
  },

  /**
   * Get stored token from either storage type
   * @returns JWT token or null
   */
  getToken(): string | null {
    return localStorage.getItem("token") || sessionStorage.getItem("token")
  },

  /**
   * Get stored user from either storage type
   * @returns User object or null
   */
  getUser(): User | null {
    const userStr = localStorage.getItem("user") || sessionStorage.getItem("user")
    return userStr ? JSON.parse(userStr) : null
  },

  /**
   * Check if user is authenticated
   * @returns true if both token and user exist
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null && this.getUser() !== null
  }
}
