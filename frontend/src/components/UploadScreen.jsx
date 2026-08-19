import { useState } from 'react'
import { analyzeText, analyzeFile } from '../api'

export default function UploadScreen({ onAnalysisComplete }) {
  const [mode, setMode] = useState('text') // 'text' | 'file'
  const [productName, setProductName] = useState('')
  const [bulkText, setBulkText] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!productName.trim()) {
      setError('Product name is required.')
      return
    }
    if (mode === 'text' && !bulkText.trim()) {
      setError('Paste at least one review.')
      return
    }
    if (mode === 'file' && !file) {
      setError('Choose a CSV file to upload.')
      return
    }

    setLoading(true)
    try {
      const data = mode === 'text'
        ? await analyzeText(productName, bulkText)
        : await analyzeFile(productName, file)
      onAnalysisComplete(data)
    } catch (err) {
      setError(err.message || 'Something went wrong. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-state">
        Analyzing reviews with Gemini — this can take a moment for larger batches...
      </div>
    )
  }

  return (
    <div className="card">
      <h3>New Analysis</h3>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>Product name</label>
          <input
            type="text"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            placeholder="e.g. Wireless Headphones X200"
          />
        </div>

        <div className="mode-toggle">
          <button type="button" className={mode === 'text' ? 'active' : ''} onClick={() => setMode('text')}>
            Paste reviews
          </button>
          <button type="button" className={mode === 'file' ? 'active' : ''} onClick={() => setMode('file')}>
            Upload CSV
          </button>
        </div>

        {mode === 'text' ? (
          <div className="field">
            <label>Reviews (one per line)</label>
            <textarea
              rows={8}
              value={bulkText}
              onChange={(e) => setBulkText(e.target.value)}
              placeholder={"Great sound quality but battery drains fast.\nComfortable fit, would buy again.\n..."}
            />
          </div>
        ) : (
          <div className="field">
            <label>CSV file (column named "review" preferred)</label>
            <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
          </div>
        )}

        {error && <div className="error-text">{error}</div>}

        <button type="submit" className="btn-primary" style={{ marginTop: 8 }}>
          Analyze Reviews
        </button>
      </form>
    </div>
  )
}
