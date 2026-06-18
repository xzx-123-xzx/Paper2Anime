import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Play, Edit, RefreshCw, Download, Share2, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'

interface ProjectInfo {
  project_id: string
  name: string
  description: string
  status: string
  progress: number
  current_stage: string
  script?: string
  storyboard?: any[]
  characters?: any[]
  final_video_url?: string
  thumbnail_url?: string
}

export default function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<ProjectInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/projects/${projectId}`)
        if (!response.ok) {
          throw new Error('获取项目失败')
        }
        const data = await response.json()
        setProject(data)
      } catch (err) {
        setError('无法获取项目信息')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    if (projectId) {
      fetchProject()
    }
  }, [projectId])

  const stageName: Record<string, string> = {
    created: '已创建',
    document_parser: '文档解析',
    script_generator: '剧本生成',
    storyboard_generator: '分镜生成',
    character_designer: '角色设计',
    image_generator: '图片生成',
    video_generator: '视频生成',
    video_editor: '视频剪辑',
    quality_check: '质量检查',
    completed: '完成',
    failed: '失败',
    cancelled: '已取消',
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error || '项目不存在'}</p>
          <Button onClick={() => navigate('/')}>返回首页</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            返回
          </Button>
          <div>
            <h1 className="text-xl font-bold text-gray-900">{project.name}</h1>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
              <span>{stageName[project.current_stage] || project.current_stage}</span>
              <span className="text-gray-300">|</span>
              <span>{project.status}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold">视频预览</h2>
              </CardHeader>
              <CardContent>
                <div className="aspect-video bg-gradient-to-br from-gray-900 to-gray-800 rounded-lg flex items-center justify-center">
                  {project.final_video_url ? (
                    <video
                      src={`http://localhost:8000/api/v1/projects/${project.project_id}/video`}
                      controls
                      className="w-full h-full rounded-lg"
                    />
                  ) : (
                    <div className="text-center text-white px-8">
                      <span className="text-6xl mb-4 block">🎬</span>
                      <p className="text-lg">视频生成中...</p>
                      <p className="text-sm text-gray-400 mt-2">
                        当前阶段: {stageName[project.current_stage] || project.current_stage}
                      </p>
                    </div>
                  )}
                </div>
                {project.final_video_url && (
                  <div className="flex gap-2 mt-4">
                    <a
                      href={`http://localhost:8000/api/v1/projects/${project.project_id}/video`}
                      download
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex"
                    >
                      <Button className="gap-2">
                        <Download className="w-4 h-4" />
                        下载
                      </Button>
                    </a>
                    <Button variant="outline" className="gap-2">
                      <Share2 className="w-4 h-4" />
                      分享
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {project.script && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                <h2 className="text-lg font-semibold">剧本</h2>
                <Button variant="outline" size="sm" className="gap-1">
                  <Edit className="w-4 h-4" />
                  编辑
                </Button>
                </CardHeader>
                <CardContent>
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 max-h-96 overflow-y-auto border rounded-lg p-4 bg-white">
                    {project.script}
                  </pre>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold">生成进度</h2>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">整体进度</span>
                    <span className="font-medium">{Math.round(project.progress)}%</span>
                  </div>
                  <Progress value={project.progress} className="h-2" />
                  <div className="text-sm text-gray-500">
                    当前阶段: {stageName[project.current_stage] || project.current_stage}
                  </div>
                  <div className="text-xs text-gray-400 mt-2">
                    每 3 秒刷新一次
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold">分镜 ({project.storyboard?.length || 0}个)</h2>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-2">
                  {project.storyboard?.map((scene: any, index: number) => (
                    <div
                      key={scene.scene_id || index}
                      className="aspect-square bg-gradient-to-br from-blue-50 to-blue-100 rounded flex flex-col items-center justify-center text-blue-700 hover:shadow-sm"
                    >
                      <span className="text-lg font-bold">{index + 1}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {project.characters && project.characters.length > 0 && (
              <Card>
                <CardHeader>
                  <h2 className="text-lg font-semibold">角色 ({project.characters.length}个)</h2>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {project.characters.map((char: any, index: number) => (
                      <div
                        key={index}
                        className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg"
                      >
                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold">
                          {char.name?.charAt(0) || '?'}
                        </div>
                        <div>
                          <p className="font-medium text-sm">{char.name}</p>
                          <p className="text-xs text-gray-500">{char.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
