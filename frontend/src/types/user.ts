export interface User {
  id: number
  username: string
  email: string
  fullName?: string
  role: 'admin' | 'user' | 'operator'
  isActive: boolean
  isSuperuser: boolean
  createdAt: string
  updatedAt: string
  lastLogin?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  fullName?: string
  password: string
  confirmPassword: string
}

export interface UpdateUserRequest {
  email?: string
  fullName?: string
  currentPassword?: string
  newPassword?: string
}

export interface AuthTokens {
  accessToken: string
  refreshToken: string
  tokenType: string
  expiresIn: number
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: string
  timezone: string
  dateFormat: string
  notifications: NotificationPreferences
}

export interface NotificationPreferences {
  email: boolean
  push: boolean
  alertTypes: string[]
  digest: boolean
  quietHours: {
    enabled: boolean
    start: string
    end: string
  }
}
