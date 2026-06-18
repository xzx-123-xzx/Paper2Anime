import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import ProjectPage from './pages/ProjectPage'
import EditorPage from './pages/EditorPage'
import SettingsPage from './pages/SettingsPage'
import UploadPage from './pages/UploadPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/project/:projectId" element={<ProjectPage />} />
      <Route path="/project/:projectId/editor" element={<EditorPage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  )
}

export default App
