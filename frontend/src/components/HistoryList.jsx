import { useEffect, useState } from 'react'
import { getProducts, getDashboard } from '../api'

export default function HistoryList({ onSelect }) {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const handleClick = async (id) => {
    try {
      const data = await getDashboard(id)
      onSelect(data)
    } catch (e) {
      setError(e.message)
    }
  }

  if (loading) return <div className="loading-state">Loading past analyses...</div>
  if (error) return <div className="error-text">{error}</div>

  return (
    <div className="card">
      <h3>Past Analyses</h3>
      {products.length === 0 ? (
        <div className="empty-state">No analyses yet. Run one from the "New Analysis" tab.</div>
      ) : (
        products.map((p) => (
          <div key={p.id} className="product-list-item" onClick={() => handleClick(p.id)}>
            <span>{p.name}</span>
            <span className="date">{new Date(p.created_at).toLocaleDateString()}</span>
          </div>
        ))
      )}
    </div>
  )
}
