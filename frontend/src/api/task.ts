import { apiClient } from './client'

export interface TaskStatus {
  task_id: string
  status: string
  progress: number
  current_node: string
  error_message?: string
}

export const taskApi = {
  get: async (taskId: string) => {
    const response = await apiClient.get<TaskStatus>(`/tasks/${taskId}`)
    return response.data
  },

  getLogs: async (taskId: string) => {
    const response = await apiClient.get(`/tasks/${taskId}/logs`)
    return response.data
  },
}
