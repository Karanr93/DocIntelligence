import React, { useState, useRef } from 'react'
import { uploadDocument } from '../api'

export default function UploadPanel() {
  const [uploads, setUploads] = useState([])
  const fileRef = useRef()

  async function handleFiles(files) {
    for (const file of files) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert(`${file.name} is not a PDF file`)
        continue
      }

      const entry = { name: file.name, status: 'uploading', id: null }
      setUploads(prev => [...prev, entry])

      try {
        const result = await uploadDocument(file)
        setUploads(prev => prev.map(u =>
          u.name === file.name ? { ...u, status: 'processing', id: result.id } : u
        ))
      } catch (err) {
        setUploads(prev => prev.map(u =>
          u.name === file.name ? { ...u, status: 'failed' } : u
        ))
      }
    }
  }

  function handleDrop(e) {
    e.preventDefault()
    handleFiles(e.dataTransfer.files)
  }

  const statusIcon = (status) => {
    switch (status) {
      case 'uploading': return '⏳'
      case 'processing': return '⚙️'
      case 'completed': return '✅'
      case 'failed': return '❌'
      default: return '📄'
    }
  }

  return (
    <div className="upload-panel">
      <h2 className="section-title">Upload Documents</h2>

      <div
        className="upload-zone"
        onDragOver={e => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
      >
        <div className="icon">📁</div>
        <p><strong>Click or drag PDF files here</strong></p>
        <p style={{ marginTop: 8, fontSize: 12 }}>Files will be OCR'd and processed automatically</p>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          multiple
          onChange={e => handleFiles(e.target.files)}
        />
      </div>

      {uploads.length > 0 && (
        <div className="upload-list">
          {uploads.map((u, i) => (
            <div key={i} className="upload-item">
              <span>{statusIcon(u.status)} {u.name}</span>
              <span className={`badge badge-${u.status === 'uploading' ? 'processing' : u.status}`}>
                {u.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
