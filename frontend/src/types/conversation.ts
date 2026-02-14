export interface Conversation {
  id: string
  customerId: number
  platform: 'email' | 'whatsapp' | 'instagram_dm' | 'tiktok_dm'
  platformConversationId?: string
  status: 'active' | 'paused' | 'closed' | 'archived'
  currentIntent?: string
  intentConfidence: number
  intentLevel?: 'low' | 'medium' | 'high' | 'very_high'
  aiHandled: boolean
  manualTakeover: boolean
  takeoverReason?: string
  tags: string[]
  customFields: Record<string, any>
  createdAt: string
  updatedAt: string
  lastMessageAt: string
}

export interface Message {
  id: string
  conversationId: string
  role: 'user' | 'system' | 'assistant'
  content: string
  platformMessageId?: string
  aiGenerated: boolean
  intentDetected?: string
  suggestedActions: string[]
  attachments: Attachment[]
  sentAt: string
  readAt: string | null
  failedAt: string | null
  errorMessage?: string
}

export interface Attachment {
  id: string
  type: 'image' | 'video' | 'document' | 'audio'
  url: string
  name: string
  size: number
  mimeType: string
}

export interface ConversationListItem {
  id: string
  customerId: number
  customerName: string
  customerAvatar?: string
  platform: string
  status: string
  lastMessage: string
  lastMessageAt: string
  intentLevel?: string
  unreadCount: number
  awaitingReply: boolean
  manualTakeover: boolean
}

export interface ConversationStats {
  total: number
  active: number
  highIntent: number
  awaitingReply: number
  aiHandled: number
  manualTakeovers: number
  avgResponseTime: number
}

export interface SendMessageRequest {
  conversationId: string
  content: string
  attachments?: Attachment[]
}

export interface ConversationSearchFilters {
  platform?: string
  status?: string
  intentLevel?: string
  hasUnread?: boolean
  dateFrom?: string
  dateTo?: string
  search?: string
}
