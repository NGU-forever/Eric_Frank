// Skill interface
export interface Skill {
  id: string
  name: string
  displayName: string
  description: string
  category: string
  inputSchema: Record<string, any>
  outputSchema: Record<string, any>
  configTemplate?: Record<string, any>
  icon?: string
  version: string
  enabled: boolean
}

export interface Workflow {
  id: string
  name: string
  description?: string
  status: 'draft' | 'active' | 'archived'
  version: string
  configJson: {
    steps: any[]
    transitions: any[]
    variables?: Record<string, any>
  }
  variables?: Record<string, any>
  tags?: string[]
  timeout?: number
  retryStrategy?: 'linear' | 'exponential'
  maxRetries?: number
  userId: number
  createdAt: string
  updatedAt: string
}

export interface WorkflowCreate {
  name: string
  description?: string
  version?: string
  steps: any[]
  transitions: any[]
  variables?: Record<string, any>
  tags?: string[]
}

export interface WorkflowUpdate {
  name?: string
  description?: string
  status?: string
  steps?: any[]
  transitions?: any[]
  variables?: Record<string, any>
  tags?: string[]
  timeout?: number
  retryStrategy?: string
  maxRetries?: number
}

export interface Execution {
  id: string
  workflowId: string
  workflowName: string
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'
  currentStep?: string
  contextJson?: Record<string, any>
  errorMsg?: string
  startedAt: string
  finishedAt?: string
}

// For backward compatibility with existing code
export interface WorkflowStep {
  id: string
  name: string
  skillName: string
  skillDisplayName?: string
  x: number
  y: number
  config: Record<string, any>
  retryOnFailure: boolean
  maxRetries: number
  timeout: number
  condition: string
  conditionExpression?: string
  onFailureAction?: string
}

export interface WorkflowConnection {
  id: string
  from: string
  to: string
  condition?: string
  x1: number
  y1: number
  x2: number
  y2: number
}

export interface WorkflowTemplate {
  id: string
  name: string
  description: string
  category: string
  thumbnail?: string
  steps: WorkflowStep[]
  connections: WorkflowConnection[]
}

export interface WorkflowValidation {
  valid: boolean
  errors: string[]
  warnings: string[]
}

export interface WorkflowExecution {
  id: string
  workflowName: string
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'cancelled'
  currentStep: string
  progress: number
  duration: string
  startedAt: string
  finishedAt: string | null
  completedSteps: string[]
  steps?: ExecutionStep[]
  errorMsg?: string
}

export interface ExecutionStep {
  name: string
  skillName: string
  status: 'pending' | 'running' | 'success' | 'failed' | 'skipped'
  completedAt: string
  duration?: string
  error?: string
}

export interface WorkflowStats {
  totalExecutions: number
  successRate: number
  avgDuration: string
  mostUsedWorkflows: string[]
}
