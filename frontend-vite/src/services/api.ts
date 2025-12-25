import axios, { AxiosInstance, AxiosError } from "axios"

// Use relative URLs - Vite proxy handles the rewriting
const apiClient: AxiosInstance = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
})

// Add token to requests
apiClient.interceptors.request.use((config) => {
  // Check localStorage first (Remember me), then sessionStorage
  const token = localStorage.getItem("token") || sessionStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle responses
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear both storage types
      localStorage.removeItem("token")
      localStorage.removeItem("user")
      sessionStorage.removeItem("token")
      sessionStorage.removeItem("user")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  },
)

// ===== Auth APIs =====
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await apiClient.post("/auth/login/", { email, password })
    return response.data
  },

  register: async (email: string, password: string, full_name: string, role: string, department: string) => {
    const response = await apiClient.post("/auth/register/", {
      email,
      password,
      full_name,
      role,
      department,
    })
    return response.data
  },

  getAllRoles: async () => {
    const response = await apiClient.get("/auth/roles/")
    return response.data
  },
}

// ===== Chat APIs =====
export const chatAPI = {
  sendMessage: async (message: string, conversationId?: number, includeSources: boolean = true) => {
    const response = await apiClient.post("/chat/", {
      message,
      conversation_id: conversationId,
      include_sources: includeSources,
    })
    return response.data
  },

  listConversations: async (limit: number = 10) => {
    const response = await apiClient.get("/chat/conversations", {
      params: { limit },
    })
    return response.data
  },

  getConversation: async (conversationId: number) => {
    const response = await apiClient.get(`/chat/conversations/${conversationId}`)
    return response.data
  },

  deleteConversation: async (conversationId: number) => {
    const response = await apiClient.delete(`/chat/conversations/${conversationId}`)
    return response.data
  },
}

// ===== Document APIs =====
export const documentAPI = {
  uploadDocument: async (
    fileBytes: ArrayBuffer | Blob,
    filename: string,
    department: string,
    description?: string,
  ) => {
    const formData = new FormData()
    formData.append("file", new Blob([fileBytes]), filename)
    formData.append("department", department)
    if (description) {
      formData.append("description", description)
    }

    const response = await apiClient.post("/documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    return response.data
  },

  listDocuments: async (limit: number = 100) => {
    const response = await apiClient.get("/documents/", {
      params: { limit },
    })
    return response.data
  },

  deleteDocument: async (documentId: number) => {
    const response = await apiClient.delete(`/documents/${documentId}`)
    return response.data
  },
}

export default apiClient
