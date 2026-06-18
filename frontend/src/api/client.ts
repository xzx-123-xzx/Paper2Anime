const API_BASE = 'http://localhost:8000/api/v1'

export interface ApiResponse<T> {
  data: T
}

class ApiError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(
  url: string,
  options: RequestInit = {},
  onUploadProgress?: (event: { loaded: number; total: number }) => void
): Promise<T> {
  if (onUploadProgress) {
    return uploadWithProgress<T>(API_BASE + url, options, onUploadProgress)
  }

  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  const res = await fetch(API_BASE + url, { ...options, headers })

  if (!res.ok) {
    const text = await res.text()
    throw new ApiError(`请求失败 (${res.status}): ${text || res.statusText}`)
  }

  const contentType = res.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return (await res.json()) as T
  }
  return res as unknown as T
}

function uploadWithProgress<T>(
  url: string,
  options: RequestInit,
  onUploadProgress: (event: { loaded: number; total: number }) => void
): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        onUploadProgress({ loaded: e.loaded, total: e.total })
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText) as T)
        } catch {
          resolve(xhr.responseText as unknown as T)
        }
      } else {
        reject(new ApiError(`上传失败 (${xhr.status}): ${xhr.statusText}`))
      }
    }

    xhr.onerror = () => reject(new ApiError('网络错误，请检查后端服务是否启动'))
    xhr.onabort = () => reject(new ApiError('上传已取消'))

    xhr.open(options.method || 'POST', url)

    if (options.body instanceof FormData) {
      xhr.send(options.body)
    } else if (options.body) {
      xhr.setRequestHeader('Content-Type', 'application/json')
      xhr.send(options.body)
    } else {
      xhr.send()
    }
  })
}

export { API_BASE, ApiError, request }
