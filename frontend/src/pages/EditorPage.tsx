import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Save, Play, ChevronUp, ChevronDown, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { useQuery } from '@tanstack/react-query'
import { projectApi } from '@/api/project'

export default function EditorPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()

  const { data: project } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectApi.get(projectId!),
    enabled: !!projectId,
  })

  const storyboard = project?.storyboard || []

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(`/project/${projectId}`)}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-bold text-gray-900 flex-1">分镜编辑器</h1>
          <Button className="gap-2">
            <Save className="w-4 h-4" />
            保存修改
          </Button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-4">
          {storyboard.map((scene: any, index: number) => (
            <Card key={scene.scene_id || index}>
              <CardHeader className="flex flex-row items-center justify-between py-3">
                <span className="font-semibold">镜头 {index + 1}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">时长: {scene.duration || 5}s</span>
                  <Button variant="ghost" size="icon" disabled={index === 0}>
                    <ChevronUp className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="icon" disabled={index === storyboard.length - 1}>
                    <ChevronDown className="w-4 h-4" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-700">画面描述</label>
                  <textarea
                    className="mt-1 w-full p-2 border rounded-md text-sm"
                    rows={2}
                    defaultValue={scene.description}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">角色</label>
                  <input
                    type="text"
                    className="mt-1 w-full p-2 border rounded-md text-sm"
                    defaultValue={scene.characters?.join(', ')}
                  />
                </div>
                {scene.dialogue && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">对话</label>
                    <textarea
                      className="mt-1 w-full p-2 border rounded-md text-sm"
                      rows={2}
                      defaultValue={scene.dialogue}
                    />
                  </div>
                )}
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="gap-1">
                    <Play className="w-4 h-4" />
                    重新生成
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-6 flex justify-end">
          <Button className="gap-2">
            <Save className="w-4 h-4" />
            保存并更新视频
          </Button>
        </div>
      </main>
    </div>
  )
}
