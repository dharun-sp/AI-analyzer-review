import { useState } from 'react'
import UploadScreen from './components/UploadScreen'
import Dashboard from './components/Dashboard'
import HistoryList from './components/HistoryList'

export default function App() {
  const [tab, setTab] = useState('new') // 'new' | 'history' | 'dashboard'
  const [dashboardData, setDashboardData] = useState(null)

  const handleAnalysisComplete = (data) => {
    setDashboardData(data)
    setTab('dashboard')
  }

  const handleHistorySelect = (data) => {
    setDashboardData(data)
    setTab('dashboard')
  }

  return (
    <div className="app">
      <div className="app-header">
        <div>
          <span className="eyebrow">Internship Project</span>
          <h1>AI Product Review Analyzer</h1>
        </div>
        <div className="nav-tabs">
          <button className={tab === 'new' ? 'active' : ''} onClick={() => setTab('new')}>
            New Analysis
          </button>
          <button className={tab === 'history' ? 'active' : ''} onClick={() => setTab('history')}>
            Past Analyses
          </button>
          {dashboardData && (
            <button className={tab === 'dashboard' ? 'active' : ''} onClick={() => setTab('dashboard')}>
              Dashboard
            </button>
          )}
        </div>
      </div>

      {tab === 'new' && <UploadScreen onAnalysisComplete={handleAnalysisComplete} />}
      {tab === 'history' && <HistoryList onSelect={handleHistorySelect} />}
      {tab === 'dashboard' && <Dashboard data={dashboardData} />}
    </div>
  )
}
