import { request } from './client'

export interface DocumentInfo {
  document_id: string
  file_name: string
  file_type: string
  file_size: number
  parsed_content?: any
  metadata?: any
  created_at: string
}

export const documentApi = {
  upload(file: File, onProgress?: (event: { loaded: number; total: number }) => void) {
    const formData = new FormData()
    formData.append('file', file)

    return request<{ document_id: string; file_path: string; status: string }>(
      '/documents/upload',
      {
        method: 'POST',
        body: formData,
      },
      onProgress
    )
  },

  get(documentId: string) {
    return request<DocumentInfo>(`/documents/${documentId}`)
  },

  parse(documentId: string) {
    return request<{ status: string; document_id: string; metadata: any }>(
      `/documents/${documentId}/parse`,
      { method: 'POST' }
    )
  },

  download(documentId: string) {
    return request<string>(`/documents/${documentId}/download`)
  },
}
