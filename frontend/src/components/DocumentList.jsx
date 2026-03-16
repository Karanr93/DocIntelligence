import React, { useState, useEffect } from 'react'
import { fetchDocumentsByClause } from '../api'

const COLORS = {
  Medical: '#3B82F6',
  Finance: '#10B981',
  Sports: '#F59E0B',
}

export default function DocumentList({ category, role, onDocClick }) {
  const [docs, setDocs] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDocs()
  }, [category, search])

  async function loadDocs() {
    setLoading(true)
    try {
      const data = await fetchDocumentsByClause(category, search)
      setDocs(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const cls = `badge badge-${status}`
    return <span className={cls}>{status}</span>
  }

  const getConfidenceColor = (score) => {
    if (score >= 0.85) return '#10B981'
    if (score >= 0.5) return '#F59E0B'
    return '#EF4444'
  }

  return (
    <div>
      <div className="doc-list-header">
        <h2>
          <span style={{ color: COLORS[category] || '#374151' }}>{category}</span> Documents
        </h2>
        <input
          className="search-input"
          type="text"
          placeholder="Search within documents..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="loading">Loading documents...</div>
      ) : docs.length === 0 ? (
        <div className="empty-state">No documents found for {category}</div>
      ) : (
        <div className="doc-table">
          <table>
            <thead>
              <tr>
                <th>Document</th>
                <th>Pages</th>
                <th>Relevant Pages</th>
                <th>Avg Confidence</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {docs.map(doc => (
                <tr key={doc.id} onClick={() => onDocClick(doc.id)}>
                  <td><strong>{doc.filename}</strong></td>
                  <td>{doc.total_pages}</td>
                  <td>
                    {doc.relevance_pages?.map(p => (
                      <span key={p} className="badge" style={{
                        background: `${COLORS[category]}20`,
                        color: COLORS[category],
                        marginRight: 4
                      }}>
                        p.{p}
                      </span>
                    ))}
                  </td>
                  <td>
                    <div className="confidence-bar">
                      <div
                        className="confidence-fill"
                        style={{
                          width: `${(doc.confidence_avg || 0) * 100}%`,
                          background: getConfidenceColor(doc.confidence_avg)
                        }}
                      />
                    </div>
                    {((doc.confidence_avg || 0) * 100).toFixed(0)}%
                  </td>
                  <td>{getStatusBadge(doc.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
