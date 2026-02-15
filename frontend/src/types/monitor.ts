export interface Alert {
  id: string
  type: AlertType
  severity: AlertSeverity
  message: string
  details?: string
  createdAt: string
  read: boolean
  actionable?: boolean
  actionType?: string
  actionData?: any
  expiresAt?: string
  relatedId?: string
  relatedType?: 'workflow' | 'conversation' | 'customer'
}

export type AlertType =
  | 'workflow_failed'
  | 'workflow_stuck'
  | 'takeover_needed'
  | 'rate_limit_exceeded'
  | 'api_error'
  | 'low_open_rate'
  | 'high_intent_leads'
  | 'account_warning'
  | 'system_warning'
  | 'security_alert'

export type AlertSeverity = 'critical' | 'high' | 'medium' | 'low'

export interface AlertSettings {
  enabledAlerts: AlertType[]
  severityThresholds: {
    critical: AlertType[]
    high: AlertType[]
    medium: AlertType[]
    low: AlertType[]
  }
  notificationMethods: {
    inApp: boolean
    email: boolean
    webhook: boolean
  }
  quietHours: {
    enabled: boolean
    start: string
    end: string
  }
}

export interface ExecutionMonitor {
  id: string
  workflowName: string
  status: ExecutionStatus
  currentStep: string
  progress: number
  duration: string
  startedAt: string
  finishedAt: string | null
  completedSteps: string[]
  failedSteps: string[]
  errorMsg?: string
  logs?: ExecutionLog[]
}

export type ExecutionStatus =
  | 'pending'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'cancelled'

export interface ExecutionLog {
  timestamp: string
  level: 'info' | 'warning' | 'error'
  message: string
  step?: string
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy'
  components: HealthComponent[]
  lastCheck: string
}

export interface HealthComponent {
  name: string
  status: 'healthy' | 'degraded' | 'unhealthy'
  responseTime?: number
  uptime?: number
  errorRate?: number
}

export interface PerformanceMetrics {
  avgResponseTime: number
  p95ResponseTime: number
  p99ResponseTime: number
  throughput: number
  errorRate: number
  activeConnections: number
}
