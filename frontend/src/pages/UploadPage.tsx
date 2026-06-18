import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FileText, X, CheckCircle2, AlertCircle, ArrowLeft, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { documentApi } from '@/api/document'
import { projectApi, ProjectSettings } from '@/api/project'

export default function UploadPage() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [error, setError] = useState('')
  const [projectCreated, setProjectCreated] = useState(false)
  const [documentId, setDocumentId] = useState('')
  const [projectId, setProjectId] = useState('')

  const [settings, setSettings] = useState<ProjectSettings>({
    quality_preset: 'standard',
    voiceover: false,
    subtitle: true,
    aspect_ratio: '16:9',
    resolution: '1920x1080'
  })

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      validateAndSetFile(droppedFile)
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      validateAndSetFile(selectedFile)
    }
  }

  const validateAndSetFile = (file: File) => {
    const validExtensions = ['txt', 'docx', 'pdf']
    const ext = file.name.split('.').pop()?.toLowerCase()
    
    if (!ext || !validExtensions.includes(ext)) {
      setError('不支持的文件格式，请上传 TXT、DOCX 或 PDF 文件')
      setUploadStatus('error')
      return
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('文件大小超过 50MB 限制')
      setUploadStatus('error')
      return
    }

    setFile(file)
    setUploadStatus('idle')
    setError('')
  }

  const removeFile = () => {
    setFile(null)
    setUploadStatus('idle')
    setError('')
    setUploadProgress(0)
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setUploadStatus('uploading')
    setUploadProgress(0)

    try {
      // 模拟上传进度
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + 10
        })
      }, 200)

      const uploadResponse = await documentApi.upload(file, (event) => {
        if (event.total) {
          const progress = Math.round((event.loaded / event.total) * 100)
          setUploadProgress(progress)
        }
      })

      clearInterval(progressInterval)
      setUploadProgress(100)
      setDocumentId(uploadResponse.document_id)
      setUploadStatus('success')

      // 创建项目
      const project = await projectApi.create({
        name: file.name.replace(/\.[^/.]+$/, ''),
        description: '',
        document_id: uploadResponse.document_id,
        settings: settings
      })

      setProjectId(project.project_id)
      setProjectCreated(true)

      // 启动工作流
      await projectApi.startWorkflow(project.project_id, settings)

      // 跳转到项目页面
      setTimeout(() => {
        navigate(`/project/${project.project_id}`)
      }, 1500)

    } catch (err: any) {
      setError(err.message || '上传失败，请重试')
      setUploadStatus('error')
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <header className="bg-white/80 backdrop-blur-sm shadow-sm sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-bold text-gray-900 flex-1">上传文档</h1>
          <Button variant="ghost" size="icon" onClick={() => navigate('/settings')}>
            <Settings className="w-5 h-5" />
          </Button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>选择文档</CardTitle>
              </CardHeader>
              <CardContent>
                {!file ? (
                  <div
                    className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-blue-400 hover:bg-blue-50/50 transition-all cursor-pointer"
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('file-input')?.click()}
                  >
                    <input
                      id="file-input"
                      type="file"
                      accept=".txt,.docx,.pdf"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <p className="text-lg font-medium text-gray-700 mb-2">
                      拖拽文件到此处或点击上传
                    </p>
                    <p className="text-sm text-gray-500">
                      支持格式：TXT、DOCX、PDF
                    </p>
                  </div>
                ) : (
                  <div className="border rounded-xl p-4">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-6 h-6 text-blue-600" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{file.name}</p>
                        <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                      {uploadStatus === 'idle' && (
                        <Button variant="ghost" size="icon" onClick={removeFile}>
                          <X className="w-5 h-5" />
                        </Button>
                      )}
                    </div>

                    {(uploadStatus === 'uploading' || uploadStatus === 'success') && (
                      <div className="mt-4">
                        <div className="flex items-center justify-between text-sm mb-2">
                          <span className="text-gray-600">
                            {uploadStatus === 'success' ? '上传完成' : '上传中...'}
                          </span>
                          <span className="text-gray-500">{uploadProgress}%</span>
                        </div>
                        <Progress value={uploadProgress} />
                      </div>
                    )}
                  </div>
                )}

                {error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                )}

                {uploadStatus === 'success' && !projectCreated && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5" />
                    <p className="text-sm text-green-700">文档上传成功，正在创建项目...</p>
                  </div>
                )}

                {projectCreated && (
                  <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5" />
                    <div>
                      <p className="text-sm text-green-700 font-medium">项目创建成功！</p>
                      <p className="text-sm text-green-600">正在跳转到项目页面...</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>项目设置</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">视频比例</label>
                  <select
                    value={settings.aspect_ratio}
                    onChange={(e) => setSettings({ ...settings, aspect_ratio: e.target.value })}
                    className="w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="16:9">16:9 (横屏)</option>
                    <option value="9:16">9:16 (竖屏)</option>
                    <option value="1:1">1:1 (方形)</option>
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">画质预设</label>
                  <select
                    value={settings.quality_preset}
                    onChange={(e) => setSettings({ ...settings, quality_preset: e.target.value })}
                    className="w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="economy">经济 (快速生成)</option>
                    <option value="standard">标准 (推荐)</option>
                    <option value="high">高质量 (较慢)</option>
                  </select>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">分辨率</label>
                  <select
                    value={settings.resolution}
                    onChange={(e) => setSettings({ ...settings, resolution: e.target.value })}
                    className="w-full p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="1280x720">720p</option>
                    <option value="1920x1080">1080p (推荐)</option>
                    <option value="2560x1440">1440p</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={settings.subtitle}
                      onChange={(e) => setSettings({ ...settings, subtitle: e.target.checked })}
                      className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">添加字幕</span>
                  </label>

                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={settings.voiceover}
                      onChange={(e) => setSettings({ ...settings, voiceover: e.target.checked })}
                      className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">添加配音</span>
                  </label>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <Button
                  className="w-full"
                  size="lg"
                  disabled={!file || uploading || uploadStatus === 'success'}
                  onClick={handleUpload}
                >
                  {uploading ? '上传中...' : '开始创建项目'}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
