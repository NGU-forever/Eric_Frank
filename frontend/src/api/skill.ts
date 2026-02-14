import api from './index'
import type { Skill } from '@/types'

export const skillApi = {
  async list() {
    const response = await api.get<{ skills: any[]; categories: string[] }>('/api/v1/skills')
    return response.data
  },

  async get(name: string) {
    const response = await api.get<Skill>(`/api/v1/skills/${name}`)
    return response.data
  },

  async execute(name: string, data: Record<string, any>) {
    const response = await api.post(`/api/v1/skills/${name}/execute`, { data })
    return response.data
  },

  async listSkills() {
    const response = await api.get<{ skills: any[]; categories: string[] }>('/api/v1/skills')
    return response.data
  },
}
