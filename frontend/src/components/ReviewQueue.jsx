import React, { useState, useEffect } from 'react'
import { fetchReviewQueue, fetchReviewStats, updateReview } from '../api'

const COLORS = {
  Medical: '#3B82F6',
  Finance: '#10B981',
  Sports: '#F59E0B',
}

export default function ReviewQueue({ role }) {
  const [items, setItems] = useState([])
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState('pending')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [filter, role])

  async function loadData() {
    setLoading(true)
    try {
      const [queueData, statsData] = await Promise.all([
        fetchReviewQueue(filter, role),
        fetchReviewStats()
      ])
      setItems(queueData)
      setStats(statsData)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleAction(reviewId, status) {
    try {
      await updateReview(reviewId, {
        status,
        reviewer_role: role || 'admin'
      })
      loadData()
    } catch (err) {
      console.error(err)
      alert('Failed to update review')
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 className="section-title">Human Review Queue</h2>
        {stats && (
          <div style={{ display: 'flex', gap: 16, fontSize: 13 }}>
            <span>Pending: <strong style={{ color: '#F59E0B' }}>{stats.pending}</strong></span>
            <span>Approved: <strong style={{ color: '#10B981' }}>{stats.approved}</strong></span>
            <span>Rejected: <strong style={{ color: '#EF4444' }}>{stats.rejected}</strong></span>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {['pending', 'approved', 'rejected'].map(s => (
          <button
            key={s}
            className={`badge ${filter === s ? `badge-${s === 'pending' ? 'processing' : s}` : ''}`}
            style={{
              cursor: 'pointer', padding: '6px 16px', border: '1px solid #e5e7eb',
              borderRadius: 6, background: filter === s ? undefined : 'white'
            }}
            onClick={() => setFilter(s)}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading">Loading review queue...</div>
      ) : items.length === 0 ? (
        <div className="empty-state">
          No {filter} review items{role ? ` for ${role}` : ''}
        </div>
      ) : (
        <div className="review-list">
          {items.map(item => (
            <div key={item.id} className="review-card">
              <div className="header-row">
                <div>
                  <strong>{item.document_name}</strong>
                  <span style={{ color: '#6b7280', marginLeft: 8, fontSize: 13 }}>
                    Page {item.page_number}
                  </span>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <span className="badge" style={{
                    background: `${COLORS[item.extraction?.category_name] || '#6b7280'}15`,
                    color: COLORS[item.extraction?.category_name] || '#6b7280',
                  }}>
                    {item.extraction?.category_name}
                  </span>
                  <span style={{ fontSize: 13, color: '#6b7280' }}>
                    Confidence: {((item.extraction?.confidence_score || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="extracted">
                {item.extraction?.extracted_text || 'No extracted text'}
              </div>

              {item.extraction?.structured_data && (
                <details style={{ fontSize: 13, marginBottom: 8 }}>
                  <summary style={{ cursor: 'pointer', color: '#6b7280' }}>View Structured Data</summary>
                  <pre style={{ background: '#f9fafb', padding: 8, borderRadius: 4, fontSize: 11, marginTop: 4 }}>
                    {JSON.stringify(item.extraction.structured_data, null, 2)}
                  </pre>
                </details>
              )}

              {filter === 'pending' && (
                <div className="review-actions">
                  <button className="btn-approve" onClick={() => handleAction(item.id, 'approved')}>
                    Approve
                  </button>
                  <button className="btn-reject" onClick={() => handleAction(item.id, 'rejected')}>
                    Reject
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
