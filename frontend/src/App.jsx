import React, { useState } from 'react'
import Dashboard from './components/Dashboard'
import DocumentList from './components/DocumentList'
import DocumentDetail from './components/DocumentDetail'
import ReviewQueue from './components/ReviewQueue'
import UploadPanel from './components/UploadPanel'
import './App.css'

const ROLES = [
  { id: '', label: 'All Roles', color: '#6B7280' },
  { id: 'Medical', label: 'Medical Clinician', color: '#3B82F6' },
  { id: 'Finance', label: 'Finance Analyst', color: '#10B981' },
  { id: 'Sports', label: 'Sports Analyst', color: '#F59E0B' },
]

export default function App() {
  const [view, setView] = useState('dashboard')
  const [selectedRole, setSelectedRole] = useState('')
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [selectedDocId, setSelectedDocId] = useState(null)

  const handleCategoryClick = (category) => {
    setSelectedCategory(category)
    setView('documents')
  }

  const handleDocClick = (docId) => {
    setSelectedDocId(docId)
    setView('detail')
  }

  const handleBack = () => {
    if (view === 'detail') {
      setView('documents')
      setSelectedDocId(null)
    } else if (view === 'documents') {
      setView('dashboard')
      setSelectedCategory(null)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1 onClick={() => { setView('dashboard'); setSelectedCategory(null); setSelectedDocId(null) }}>
            DocClause
          </h1>
          <span className="subtitle">Document Clause Extraction System</span>
        </div>
        <nav className="nav">
          <button className={view === 'dashboard' ? 'active' : ''} onClick={() => setView('dashboard')}>Dashboard</button>
          <button className={view === 'upload' ? 'active' : ''} onClick={() => setView('upload')}>Upload</button>
          <button className={view === 'review' ? 'active' : ''} onClick={() => setView('review')}>Review Queue</button>
        </nav>
        <div className="role-selector">
          <label>Role:</label>
          <select value={selectedRole} onChange={e => setSelectedRole(e.target.value)}>
            {ROLES.map(r => (
              <option key={r.id} value={r.id}>{r.label}</option>
            ))}
          </select>
        </div>
      </header>

      <main className="main">
        {view !== 'dashboard' && view !== 'upload' && view !== 'review' && (
          <button className="back-btn" onClick={handleBack}>← Back</button>
        )}

        {view === 'dashboard' && (
          <Dashboard
            role={selectedRole}
            onCategoryClick={handleCategoryClick}
          />
        )}

        {view === 'documents' && (
          <DocumentList
            category={selectedCategory}
            role={selectedRole}
            onDocClick={handleDocClick}
          />
        )}

        {view === 'detail' && selectedDocId && (
          <DocumentDetail
            docId={selectedDocId}
            role={selectedRole}
          />
        )}

        {view === 'upload' && <UploadPanel />}

        {view === 'review' && <ReviewQueue role={selectedRole} />}
      </main>
    </div>
  )
}
