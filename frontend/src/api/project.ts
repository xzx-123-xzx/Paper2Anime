import { request } from './client'

export interface ProjectSettings {
  quality_preset: string
  voiceover: boolean
  subtitle: boolean
  aspect_ratio: string
  resolution: string
}

export interface ProjectInfo {
  project_id: string
  user_id: string
  name: string
  description: string
  document_id: string
  status: string
  progress: number
  current_stage: string
  settings: ProjectSettings
  script?: string
  storyboard?: any[]
  characters?: any[]
  final_video_url?: string
  thumbnail_url?: string
  error_message?: string
  created_at: string
  updated_at: string
}

export interface WorkflowInfo {
  workflow_id: string
  project_id: string
  status: string
  current_node?: string
  progress: number
  error_message?: string
}

export const projectApi = {
  create(data: {
    name: string
    description?: string
    document_id: string
    settings: ProjectSettings
  }) {
    return request<ProjectInfo>('/projects/', {
      method: 'POST',
      body: JSON.stringify({
        name: data.name,
        description: data.description || '',
        document_id: data.document_id,
        settings: data.settings,
        status: 'pending',
      }),
    })
  },

  list() {
    return request<ProjectInfo[]>('/projects/')
  },

  get(projectId: string) {
    return request<ProjectInfo>(`/projects/${projectId}`)
  },

  update(projectId: string, data: Partial<ProjectInfo>) {
    return request<ProjectInfo>(`/projects/${projectId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  },

  delete(projectId: string) {
    return request<{ success: boolean; project_id: string }>(`/projects/${projectId}`, {
      method: 'DELETE',
    })
  },

  startWorkflow(projectId: string, options?: Record<string, any>) {
    return request<{
      workflow_id: string
      project_id: string
      task_id: string
      status: string
    }>('/tasks/workflows/start', {
      method: 'POST',
      body: JSON.stringify({
        project_id: projectId,
        options: options || {},
      }),
    })
  },

  getWorkflowStatus(workflowId: string) {
    return request<WorkflowInfo>(`/tasks/workflows/${workflowId}/status`)
  },

  cancelWorkflow(workflowId: string) {
    return request<{ status: string; workflow_id: string }>(
      `/tasks/workflows/${workflowId}/cancel`,
      { method: 'POST' }
    )
  },

  getWorkflowResult(workflowId: string) {
    return request<{
      workflow_id: string
      status: string
      project: {
        project_id: string
        final_video_url?: string
        thumbnail_url?: string
        script?: string
        storyboard?: any
        characters?: any
      }
    }>(`/tasks/workflows/${workflowId}/result`)
  },

  getTask(taskId: string) {
    return request<{
      task_id: string
      status: string
      progress?: number
      result?: any
      error?: string
    }>(`/tasks/${taskId}`)
  },
}
