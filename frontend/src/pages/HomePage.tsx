import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, FolderOpen, Plus, Search, Filter, ChevronRight, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { projectApi } from '@/api/project'

export default function HomePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<{ id: string; name: string } | null>(null)

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectApi.list,
  })

  const deleteMutation = useMutation({
    mutationFn: (projectId: string) => projectApi.delete(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setDeleteTarget(null)
    },
    onError: (err) => {
      console.error('删除失败:', err)
      alert('删除失败，请重试')
    },
  })

  const filteredProjects = projects.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleCardClick = (projectId: string) => {
    if (deleteMutation.isPending) return
    navigate(`/project/${projectId}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">P2A</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">Paper2Anime</h1>
          </div>
          <Button variant="ghost" onClick={() => navigate('/settings')}>
            设置
          </Button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8">
          <Button size="lg" className="gap-2" onClick={() => navigate('/upload')}>
            <Upload className="w-5 h-5" />
            上传文档
          </Button>
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="搜索项目..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">我的项目</h2>
          <Button variant="outline" size="sm" className="gap-1">
            <Filter className="w-4 h-4" />
            筛选
          </Button>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-gray-500">加载中...</div>
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-12">
            <FolderOpen className="w-16 h-16 mx-auto text-gray-300 mb-4" />
            <p className="text-gray-500 mb-4">还没有项目</p>
            <Button onClick={() => navigate('/upload')}>创建第一个项目</Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProjects.map((project) => (
              <Card
                key={project.project_id}
                className="cursor-pointer hover:shadow-lg transition-shadow relative group"
              >
                <div
                  onClick={() => handleCardClick(project.project_id)}
                  className="cursor-pointer"
                >
                  <CardHeader className="pb-2">
                    <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg mb-2 flex items-center justify-center">
                      {project.status === 'completed' ? (
                        <span className="text-4xl">🎬</span>
                      ) : project.status === 'failed' ? (
                        <span className="text-4xl">❌</span>
                      ) : (
                        <span className="text-4xl">📄</span>
                      )}
                    </div>
                    <h3 className="font-semibold text-gray-900 truncate">{project.name}</h3>
                  </CardHeader>
                  <CardContent className="pb-2">
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span className="capitalize">{project.status.replace('_', ' ')}</span>
                      <span>{Math.round(project.progress)}%</span>
                    </div>
                    {project.status !== 'completed' && project.status !== 'failed' && (
                      <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 transition-all"
                          style={{ width: `${project.progress}%` }}
                        />
                      </div>
                    )}
                  </CardContent>
                  <CardFooter className="text-xs text-gray-400">
                    {new Date(project.created_at).toLocaleDateString('zh-CN')}
                    <ChevronRight className="w-4 h-4 ml-auto" />
                  </CardFooter>
                </div>
                <button
                  className="absolute top-2 right-2 p-1.5 rounded-md bg-white/80 hover:bg-red-50 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity shadow-sm"
                  title="删除项目"
                  onClick={(e) => {
                    e.stopPropagation()
                    setDeleteTarget({ id: project.project_id, name: project.name })
                  }}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </Card>
            ))}
          </div>
        )}
      </main>

      {deleteTarget && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
          onClick={() => !deleteMutation.isPending && setDeleteTarget(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl w-full max-w-sm mx-4 p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-2">确认删除项目？</h3>
            <p className="text-sm text-gray-500 mb-4">
              将删除项目 <span className="font-medium text-gray-900">"{deleteTarget.name}"</span>{' '}
              以及其工作流、生成的图片、视频和分镜文件。此操作不可恢复。
            </p>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setDeleteTarget(null)}
                disabled={deleteMutation.isPending}
              >
                取消
              </Button>
              <Button
                variant="destructive"
                onClick={() => deleteMutation.mutate(deleteTarget.id)}
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? '删除中...' : '确认删除'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
