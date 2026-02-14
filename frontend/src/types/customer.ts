export interface Customer {
  id: number
  username: string
  platform: 'tiktok' | 'instagram' | 'youtube' | 'facebook'
  email?: string
  whatsapp?: string
  phone?: string
  country?: string
  category?: string
  followerCount?: number
  status: 'new' | 'contacted' | 'engaged' | 'converted' | 'lost'
  intentLevel?: 'low' | 'medium' | 'high' | 'very_high'
  tags?: string[]
  sourceDataJson?: Record<string, any>
  createdAt: string
  updatedAt: string
  lastContactedAt?: string
}

export interface CustomerCreate {
  username: string
  platform: string
  email?: string
  whatsapp?: string
  phone?: string
  country?: string
  category?: string
  followerCount?: number
  sourceDataJson?: Record<string, any>
}

export interface CustomerUpdate {
  email?: string
  whatsapp?: string
  phone?: string
  country?: string
  category?: string
  status?: string
  intentLevel?: string
  tags?: string[]
}

export interface CustomerSearchFilters {
  page?: number
  page_size?: number
  platform?: string
  country?: string
  category?: string
  status?: string
  intent_level?: string
  search?: string
}

export interface CustomerStats {
  total: number
  byStatus: Record<string, number>
  byPlatform: Record<string, number>
  byCountry: Record<string, number>
  highIntentCount: number
}

export interface HighIntentLead {
  id: number
  name: string
  username: string
  intent: 'low' | 'medium' | 'high' | 'very_high'
  lastActivity: string
}
