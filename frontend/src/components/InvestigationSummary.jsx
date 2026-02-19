import React, { useState, useEffect } from 'react'
import { getInvestigationSummary } from '../services/api'
import '../styles/InvestigationSummary.css'

function InvestigationSummary({ analysisId }) {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchSummary = async () => {
      if (!analysisId) return
      
      setLoading(true)
      setError(null)
      try {
        const data = await getInvestigationSummary(analysisId)
        setSummary(data)
      } catch (err) {
        console.error('Error fetching investigation summary:', err)
        setError('Failed to load AI summary')
      } finally {
        setLoading(false)
      }
    }

    fetchSummary()
  }, [analysisId])

  if (loading) {
    return (
      <div className="investigation-summary loading">
        <div className="skeleton-loader"></div>
      </div>
    )
  }

  if (error) {
    return <div className="investigation-summary error">{error}</div>
  }

  if (!summary) return null

  return (
    <div className="investigation-summary">
      <h3>📋 AI Investigation Summary</h3>
      <div className="summary-content">
        <p>{summary.overview}</p>
        {summary.top_suspects && summary.top_suspects.length > 0 && (
          <div className="suspects-section">
            <h4>🚨 Top Suspects</h4>
            <ul>
              {summary.top_suspects.slice(0, 5).map((suspect, idx) => (
                <li key={idx}>{suspect}</li>
              ))}
            </ul>
          </div>
        )}
        {summary.key_findings && summary.key_findings.length > 0 && (
          <div className="findings-section">
            <h4>🔍 Key Findings</h4>
            <ul>
              {summary.key_findings.slice(0, 5).map((finding, idx) => (
                <li key={idx}>{finding}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default InvestigationSummary
