import { create } from 'zustand'
import type { Project } from '@/api/project'

interface ProjectState {
  currentProject: Project | null
  projects: Project[]
  setCurrentProject: (project: Project | null) => void
  setProjects: (projects: Project[]) => void
  updateProject: (projectId: string, updates: Partial<Project>) => void
}

export const useProjectStore = create<ProjectState>((set) => ({
  currentProject: null,
  projects: [],
  setCurrentProject: (project) => set({ currentProject: project }),
  setProjects: (projects) => set({ projects }),
  updateProject: (projectId, updates) =>
    set((state) => ({
      projects: state.projects.map((p) =>
        p.project_id === projectId ? { ...p, ...updates } : p
      ),
      currentProject:
        state.currentProject?.project_id === projectId
          ? { ...state.currentProject, ...updates }
          : state.currentProject,
    })),
}))
