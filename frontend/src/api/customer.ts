import api from './index'
import type { Customer, CustomerCreate } from '@/types'

export const customerApi = {
  async list(params?: {
    page?: number
    page_size?: number
    platform?: string
    country?: string
    category?: string
    status?: string
    intent_level?: string
    search?: string
  }) {
    const response = await api.get<{
      items: Customer[]
      total: number
      page: number
      page_size: number
    }>('/api/v1/customers', { params })
    return response.data
  },

  async get(id: number) {
    const response = await api.get<Customer>(`/api/v1/customers/${id}`)
    return response.data
  },

  async create(data: CustomerCreate) {
    const response = await api.post<Customer>('/api/v1/customers', data)
    return response.data
  },

  async update(id: number, data: Partial<CustomerCreate>) {
    const response = await api.put<Customer>(`/api/v1/customers/${id}`, data)
    return response.data
  },

  async delete(id: number) {
    await api.delete(`/api/v1/customers/${id}`)
  },

  async bulkCreate(data: CustomerCreate[]) {
    const response = await api.post<{ created: number; duplicates: number; customers: number[] }>(
      '/api/v1/customers/bulk',
      data
    )
    return response.data
  },

  async addTags(id: number, tags: string[]) {
    const response = await api.post<{ tags: string[] }>(`/api/v1/customers/${id}/tags`, tags)
    return response.data
  },

  async removeTags(id: number, tags: string[]) {
    const response = await api.delete<{ tags: string[] }>(`/api/v1/customers/${id}/tags`, {
      data: tags,
    })
    return response.data
  },
}
