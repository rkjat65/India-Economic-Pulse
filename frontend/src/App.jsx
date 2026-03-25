import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import GDP from './pages/GDP'
import Inflation from './pages/Inflation'
import Trade from './pages/Trade'
import Forex from './pages/Forex'
import AIStudio from './pages/AIStudio'
import ContentStudio from './pages/ContentStudio'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-bg text-white overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/gdp" element={<GDP />} />
            <Route path="/inflation" element={<Inflation />} />
            <Route path="/trade" element={<Trade />} />
            <Route path="/forex" element={<Forex />} />
            <Route path="/ai-studio" element={<AIStudio />} />
            <Route path="/content-studio" element={<ContentStudio />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
