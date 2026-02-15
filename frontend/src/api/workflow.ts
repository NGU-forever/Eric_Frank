import api from './index'
import type { Workflow, WorkflowCreate, WorkflowUpdate, Execution } from '@/types'

export const workflowApi = {
  async list() {
    const response = await api.get<Workflow[]>('/api/v1/workflows')
    return response.data
  },

  async get(id: string) {
    const response = await api.get<Workflow>(`/api/v1/workflows/${id}`)
    return response.data
  },

  async create(data: WorkflowCreate) {
    const response = await api.post<Workflow>('/api/v1/workflows', data)
    return response.data
  },

  async update(id: string, data: WorkflowUpdate) {
    const response = await api.put<Workflow>(`/api/v1/workflows/${id}`, data)
    return response.data
  },

  async delete(id: string) {
    await api.delete(`/api/v1/workflows/${id}`)
  },

  async execute(id: string, inputData: Record<string, any>) {
    const response = await api.post<{ execution_id: string }>(
      `/api/v1/workflows/${id}/execute`,
      { workflow_id: id, input_data: inputData }
    )
    return response.data
  },

  async getExecution(id: string) {
    const response = await api.get<Execution>(`/api/v1/workflows/executions/${id}`)
    return response.data
  },

  async pauseExecution(id: string) {
    await api.post(`/api/v1/workflows/executions/${id}/pause`)
  },

  async resumeExecution(id: string) {
    await api.post(`/api/v1/workflows/executions/${id}/resume`)
  },

  async cancelExecution(id: string) {
    await api.post(`/api/v1/workflows/executions/${id}/cancel`)
  },
}
