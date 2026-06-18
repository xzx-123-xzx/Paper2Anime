import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Key, Database, HardDrive, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Settings {
  deepseek_api_key: string
  deepseek_base_url: string
  minmax_api_key: string
  mysql_host: string
  mysql_port: number
  mysql_user: string
  mysql_password: string
  mysql_database: string
  storage_type: string
  local_storage_path: string
}

const DEFAULTS: Settings = {
  deepseek_api_key: '',
  deepseek_base_url: 'https://api.deepseek.com',
  minmax_api_key: '',
  mysql_host: 'localhost',
  mysql_port: 3306,
  mysql_user: 'root',
  mysql_password: '',
  mysql_database: 'paper2anime',
  storage_type: 'local',
  local_storage_path: './storage',
}

const API_BASE = 'http://localhost:8000/api/v1'

export default function SettingsPage() {
  const navigate = useNavigate()
  const [settings, setSettings] = useState<Settings>(DEFAULTS)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    const loadSettings = async () => {
      setLoading(true)
      try {
        const res = await fetch(`${API_BASE}/settings/`)
        if (res.ok) {
          const data = await res.json()
          setSettings({ ...DEFAULTS, ...data })
        }
      } catch (e) {
        console.error('加载设置失败:', e)
      } finally {
        setLoading(false)
      }
    }
    loadSettings()
  }, [])

  const handleChange = (key: keyof Settings, value: string | number) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)
    try {
      const res = await fetch(`${API_BASE}/settings/`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      })
      if (res.ok) {
        const data = await res.json()
        setSettings({ ...DEFAULTS, ...data })
        setMessage({ type: 'success', text: '设置已保存' })
        setTimeout(() => setMessage(null), 3000)
      } else {
        setMessage({ type: 'error', text: '保存失败，请检查后端服务是否启动' })
      }
    } catch (e) {
      console.error('保存设置失败:', e)
      setMessage({ type: 'error', text: '保存失败，请检查后端服务是否启动' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-xl font-bold text-gray-900">设置</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {message && (
          <div
            className={`mb-4 px-4 py-3 rounded-md ${
              message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="w-5 h-5" />
                API 配置
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">DeepSeek API Key</label>
                <input
                  type="password"
                  className="mt-1 w-full p-2 border rounded-md"
                  placeholder="sk-..."
                  value={settings.deepseek_api_key}
                  onChange={(e) => handleChange('deepseek_api_key', e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium">DeepSeek Base URL</label>
                <input
                  type="text"
                  className="mt-1 w-full p-2 border rounded-md"
                  placeholder="https://api.deepseek.com"
                  value={settings.deepseek_base_url}
                  onChange={(e) => handleChange('deepseek_base_url', e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium">MinMax API Key</label>
                <input
                  type="password"
                  className="mt-1 w-full p-2 border rounded-md"
                  placeholder="..."
                  value={settings.minmax_api_key}
                  onChange={(e) => handleChange('minmax_api_key', e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                数据库配置
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">MySQL Host</label>
                <input
                  type="text"
                  className="mt-1 w-full p-2 border rounded-md"
                  value={settings.mysql_host}
                  onChange={(e) => handleChange('mysql_host', e.target.value)}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">MySQL User</label>
                  <input
                    type="text"
                    className="mt-1 w-full p-2 border rounded-md"
                    value={settings.mysql_user}
                    onChange={(e) => handleChange('mysql_user', e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">MySQL Password</label>
                  <input
                    type="password"
                    className="mt-1 w-full p-2 border rounded-md"
                    value={settings.mysql_password}
                    onChange={(e) => handleChange('mysql_password', e.target.value)}
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">MySQL Database</label>
                <input
                  type="text"
                  className="mt-1 w-full p-2 border rounded-md"
                  value={settings.mysql_database}
                  onChange={(e) => handleChange('mysql_database', e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HardDrive className="w-5 h-5" />
                存储配置
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">存储类型</label>
                <select
                  className="mt-1 w-full p-2 border rounded-md"
                  value={settings.storage_type}
                  onChange={(e) => handleChange('storage_type', e.target.value)}
                >
                  <option value="local">本地存储</option>
                  <option value="s3">S3/MinIO</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">本地存储路径</label>
                <input
                  type="text"
                  className="mt-1 w-full p-2 border rounded-md"
                  value={settings.local_storage_path}
                  onChange={(e) => handleChange('local_storage_path', e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => navigate(-1)} disabled={saving}>
              取消
            </Button>
            <Button onClick={handleSave} disabled={saving || loading} className="gap-2">
              <Save className="w-4 h-4" />
              {saving ? '保存中...' : '保存设置'}
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
