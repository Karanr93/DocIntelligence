import React, { useState, useEffect } from 'react'
import { fetchDocument, downloadAnnotatedPdf } from '../api'

const COLORS = {
  Medical: '#3B82F6',
  Finance: '#10B981',
  Sports: '#F59E0B',
}

export default function DocumentDetail({ docId, role }) {
  const [doc, setDoc] = useState(null)
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)
  const [pdfUrl, setPdfUrl] = useState(null)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [viewMode, setViewMode] = useState('pdf') // 'pdf' or 'extractions'

  useEffect(() => {
    loadDoc()
    loadPdfPreview()
    return () => {
      // Cleanup blob URL on unmount
      if (pdfUrl) window.URL.revokeObjectURL(pdfUrl)
    }
  }, [docId, role])

  async function loadDoc() {
    setLoading(true)
    try {
      const data = await fetchDocument(docId, role)
      setDoc(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function loadPdfPreview() {
    setPdfLoading(true)
    try {
      // Revoke old URL
      if (pdfUrl) window.URL.revokeObjectURL(pdfUrl)
      const blob = await downloadAnnotatedPdf(docId, role)
      const url = window.URL.createObjectURL(blob)
      setPdfUrl(url)
    } catch (err) {
      console.error('Failed to load PDF preview:', err)
    } finally {
      setPdfLoading(false)
    }
  }

  async function handleDownload() {
    setDownloading(true)
    try {
      const blob = await downloadAnnotatedPdf(docId, role)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `annotated_${doc?.filename || 'document.pdf'}`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Download failed:', err)
      alert('Failed to download annotated PDF')
    } finally {
      setDownloading(false)
    }
  }

  if (loading) return <div className="loading">Loading document...</div>
  if (!doc) return <div className="empty-state">Document not found</div>

  return (
    <div className="doc-detail">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h2>{doc.filename}</h2>
          <div style={{ color: '#6b7280', fontSize: 13, marginTop: 4 }}>
            {doc.total_pages} pages · Status: {doc.status}
            {role && <span> · Filtered by: <strong style={{ color: COLORS[role] }}>{role}</strong></span>}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {/* View mode toggle */}
          <div style={{
            display: 'flex', borderRadius: 8, overflow: 'hidden',
            border: '1px solid #d1d5db'
          }}>
            <button
              onClick={() => setViewMode('pdf')}
              style={{
                padding: '8px 16px', border: 'none', cursor: 'pointer', fontSize: 13,
                background: viewMode === 'pdf' ? '#3b82f6' : 'white',
                color: viewMode === 'pdf' ? 'white' : '#374151',
              }}
            >
              Highlighted PDF
            </button>
            <button
              onClick={() => setViewMode('extractions')}
              style={{
                padding: '8px 16px', border: 'none', cursor: 'pointer', fontSize: 13,
                borderLeft: '1px solid #d1d5db',
                background: viewMode === 'extractions' ? '#3b82f6' : 'white',
                color: viewMode === 'extractions' ? 'white' : '#374151',
              }}
            >
              Extractions
            </button>
          </div>
          <button className="download-btn" onClick={handleDownload} disabled={downloading}>
            {downloading ? 'Generating...' : 'Download PDF'}
          </button>
        </div>
      </div>

      {/* Clause summary badges */}
      {doc.clause_summary && Object.keys(doc.clause_summary).length > 0 && (
        <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
          {Object.entries(doc.clause_summary).map(([name, count]) => (
            <div key={name} className="badge" style={{
              background: `${COLORS[name] || '#6b7280'}15`,
              color: COLORS[name] || '#6b7280',
              padding: '6px 14px', fontSize: 13,
            }}>
              {name}: {count} extractions
            </div>
          ))}
        </div>
      )}

      {/* Color legend */}
      <div style={{
        display: 'flex', gap: 16, marginBottom: 16, padding: '8px 16px',
        background: 'white', borderRadius: 8, fontSize: 13, alignItems: 'center',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <span style={{ color: '#6b7280', fontWeight: 500 }}>Highlight Colors:</span>
        {Object.entries(COLORS).map(([name, color]) => (
          <span key={name} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{
              width: 16, height: 16, borderRadius: 3,
              background: color, opacity: 0.4, display: 'inline-block'
            }} />
            {name}
          </span>
        ))}
      </div>

      {/* PDF View */}
      {viewMode === 'pdf' && (
        <div style={{
          background: 'white', borderRadius: 12, overflow: 'hidden',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: 24
        }}>
          {pdfLoading ? (
            <div style={{ padding: 48, textAlign: 'center', color: '#6b7280' }}>
              Loading highlighted PDF...
            </div>
          ) : pdfUrl ? (
            <iframe
              src={pdfUrl}
              style={{
                width: '100%',
                height: 'calc(100vh - 280px)',
                minHeight: 600,
                border: 'none',
              }}
              title="Highlighted PDF Preview"
            />
          ) : (
            <div style={{ padding: 48, textAlign: 'center', color: '#9ca3af' }}>
              Failed to load PDF preview
            </div>
          )}
        </div>
      )}

      {/* Extractions View */}
      {viewMode === 'extractions' && doc.pages?.map(page => (
        <div key={page.id} className="page-section">
          <h3>Page {page.page_number}</h3>

          {page.extractions?.length > 0 ? (
            <div className="extraction-cards">
              {page.extractions.map(ext => (
                <div
                  key={ext.id}
                  className="extraction-card"
                  style={{ borderLeftColor: COLORS[ext.category_name] || '#e5e7eb' }}
                >
                  <div className="meta">
                    <span className="badge" style={{
                      background: `${COLORS[ext.category_name] || '#6b7280'}15`,
                      color: COLORS[ext.category_name] || '#6b7280',
                    }}>
                      {ext.category_name}
                    </span>
                    <span>Source: {ext.source}</span>
                    <span>
                      Confidence:
                      <span style={{
                        color: ext.confidence_score >= 0.85 ? '#10B981' :
                               ext.confidence_score >= 0.5 ? '#F59E0B' : '#EF4444',
                        fontWeight: 600, marginLeft: 4
                      }}>
                        {(ext.confidence_score * 100).toFixed(0)}%
                      </span>
                    </span>
                    {ext.needs_review && (
                      <span className="badge" style={{ background: '#FEF3C7', color: '#92400E' }}>
                        Needs Review
                      </span>
                    )}
                  </div>

                  {ext.extracted_text && (
                    <div className="text">{ext.extracted_text}</div>
                  )}

                  {ext.structured_data && Object.keys(ext.structured_data).length > 0 && (
                    <details style={{ marginTop: 8, fontSize: 13 }}>
                      <summary style={{ cursor: 'pointer', color: '#6b7280' }}>
                        Structured Data
                      </summary>
                      <pre style={{
                        background: '#f9fafb', padding: 12, borderRadius: 6,
                        fontSize: 12, overflow: 'auto', marginTop: 8
                      }}>
                        {JSON.stringify(ext.structured_data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: '#9ca3af', fontSize: 13, padding: '8px 0' }}>
              No extractions for this page{role ? ` (filtered by ${role})` : ''}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
