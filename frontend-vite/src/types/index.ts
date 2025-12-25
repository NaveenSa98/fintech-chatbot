export interface User {
  id: string
  email: string
  fullName: string
  role: "Finance" | "Marketing" | "HR" | "Engineering" | "Employee" | "C-Level"
  department: string
  status: "active" | "inactive"
}

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  sources?: string[]
}

export interface Conversation {
  id: string
  title: string
  createdAt: Date
  messages: Message[]
}

export interface Document {
  id: string
  filename: string
  type: string
  size: number
  uploadDate: Date
  status: "processed" | "processing"
  chunks: number
}
