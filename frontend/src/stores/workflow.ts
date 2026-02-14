import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api'
import type { Workflow, WorkflowCreate, WorkflowUpdate } from '@/types'

export const useWorkflowStore = defineStore('workflow', () => {
  const workflows = ref<Workflow[]>([])
  const currentWorkflow = ref<Workflow | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchWorkflows() {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/api/v1/workflows')
      workflows.value = response.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function fetchWorkflow(id: string) {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/api/v1/workflows/${id}`)
      currentWorkflow.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createWorkflow(data: WorkflowCreate) {
    loading.value = true
    error.value = null

    try {
      const response = await api.post('/api/v1/workflows', data)
      workflows.value.push(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateWorkflow(id: string, data: WorkflowUpdate) {
    loading.value = true
    error.value = null

    try {
      const response = await api.put(`/api/v1/workflows/${id}`, data)

      const index = workflows.value.findIndex((w) => w.id === id)
      if (index !== -1) {
        workflows.value[index] = response.data
      }

      if (currentWorkflow.value?.id === id) {
        currentWorkflow.value = response.data
      }

      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteWorkflow(id: string) {
    loading.value = true
    error.value = null

    try {
      await api.delete(`/api/v1/workflows/${id}`)

      workflows.value = workflows.value.filter((w) => w.id !== id)

      if (currentWorkflow.value?.id === id) {
        currentWorkflow.value = null
      }
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function executeWorkflow(id: string, inputData: Record<string, any>) {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/api/v1/workflows/${id}/execute`, {
        workflow_id: id,
        input_data: inputData,
      })

      return response.data
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    workflows,
    currentWorkflow,
    loading,
    error,
    fetchWorkflows,
    fetchWorkflow,
    createWorkflow,
    updateWorkflow,
    deleteWorkflow,
    executeWorkflow,
  }
})
