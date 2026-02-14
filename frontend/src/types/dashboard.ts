export interface DashboardStats {
  today: DailyStats
  week: DailyStats
  month: DailyStats
  conversionRate: number
  avgResponseTime: number
  activeConversations: number
  highIntentLeads: number
  trends?: Trends
}

export interface Trends {
  customers: number
  messages: number
  replies: number
  conversions: number
}

export interface DailyStats {
  date: string
  newCustomers: number
  new_customers?: number  // Alternative naming for compatibility
  activeCustomers: number
  convertedCustomers: number
  converted_customers?: number  // Alternative naming for compatibility
  emailsSent: number
  emails_sent?: number  // Alternative naming for compatibility
  whatsappSent: number
  emailsOpened: number
  emailsReplied: number
  emails_replied?: number  // Alternative naming for compatibility
  newConversations: number
  activeConversations: number
  aiHandled: number
  manualTakeovers: number
  workflowsExecuted: number
  workflowsCompleted: number
  workflowsFailed: number
}

export interface ActivityItem {
  id: string
  type: ActivityType
  description: string
  timestamp: string
  metadata?: Record<string, any>
  userId?: number
}

export type ActivityType =
  | 'message_sent'
  | 'message_delivered'
  | 'message_opened'
  | 'reply_received'
  | 'workflow_started'
  | 'workflow_completed'
  | 'workflow_failed'
  | 'customer_created'
  | 'customer_updated'
  | 'takeover_requested'
  | 'system_alert'

export interface FunnelStage {
  name: string
  value: number
  rate: number
  color: string
}

export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string
  borderColor?: string
}

export interface MetricCard {
  label: string
  value: number
  suffix?: string
  trend?: number
  period?: string
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  icon?: string
}

export interface TopLead {
  customerId: number
  customerName: string
  intentLevel: string
  engagementScore: number
  lastActivity: string
}
