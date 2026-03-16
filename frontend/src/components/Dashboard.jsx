import React, { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { fetchDashboardStats } from '../api'

const COLORS = {
  Medical: '#3B82F6',
  Finance: '#10B981',
  Sports: '#F59E0B',
}

export default function Dashboard({ role, onCategoryClick }) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
    const interval = setInterval(loadStats, 5000)
    return () => clearInterval(interval)
  }, [])

  async function loadStats() {
    try {
      const data = await fetchDashboardStats()
      setStats(data)
    } catch (err) {
      console.error('Failed to load stats:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading dashboard...</div>
  if (!stats) return <div className="empty-state">Failed to load dashboard</div>

  const chartData = Object.entries(stats.clause_document_counts || {}).map(([name, count]) => ({
    name,
    documents: count,
    extractions: stats.clause_counts?.[name] || 0,
  }))

  // Filter by role if set
  const filteredChart = role ? chartData.filter(d => d.name === role) : chartData

  return (
    <div>
      <h2 className="section-title">Dashboard Overview</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="label">Total Documents</div>
          <div className="value">{stats.total_documents}</div>
        </div>
        <div className="stat-card">
          <div className="label">Processed</div>
          <div className="value" style={{ color: '#10B981' }}>{stats.processed_documents}</div>
        </div>
        <div className="stat-card">
          <div className="label">Pending</div>
          <div className="value" style={{ color: '#F59E0B' }}>{stats.pending_documents}</div>
        </div>
        <div className="stat-card">
          <div className="label">Failed</div>
          <div className="value" style={{ color: '#EF4444' }}>{stats.failed_documents}</div>
        </div>
      </div>

      <div className="clause-section">
        <div>
          <h3 className="section-title">Clause Categories</h3>
          <div className="clause-cards">
            {(role ? chartData.filter(d => d.name === role) : chartData).map(item => (
              <div
                key={item.name}
                className="clause-card"
                style={{ borderLeftColor: COLORS[item.name] || '#6B7280' }}
                onClick={() => onCategoryClick(item.name)}
              >
                <div className="color-dot" style={{ background: COLORS[item.name] || '#6B7280' }}>
                  {item.documents}
                </div>
                <div className="info">
                  <div className="name">{item.name}</div>
                  <div className="count">
                    {item.documents} documents · {item.extractions} extractions
                  </div>
                </div>
              </div>
            ))}
            {chartData.length === 0 && (
              <div className="empty-state">No documents processed yet. Upload some PDFs to get started.</div>
            )}
          </div>
        </div>

        <div className="chart-container">
          <h3>Documents by Clause Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={filteredChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="documents" name="Documents" radius={[6, 6, 0, 0]}>
                {filteredChart.map((entry, i) => (
                  <Cell key={i} fill={COLORS[entry.name] || '#6B7280'} />
                ))}
              </Bar>
              <Bar dataKey="extractions" name="Extractions" radius={[6, 6, 0, 0]} opacity={0.5}>
                {filteredChart.map((entry, i) => (
                  <Cell key={i} fill={COLORS[entry.name] || '#6B7280'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
