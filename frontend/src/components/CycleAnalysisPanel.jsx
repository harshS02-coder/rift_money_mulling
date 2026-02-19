import React, { useState, useEffect } from 'react'
import { getCycleAnalysis } from '../services/api'
import '../styles/CycleAnalysisPanel.css'

function CycleAnalysisPanel({ analysisId, ringIndex }) {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (!analysisId || ringIndex === undefined) return

      setLoading(true)
      setError(null)
      try {
        const data = await getCycleAnalysis(analysisId, ringIndex)
        setAnalysis(data)
      } catch (err) {
        console.error('Error fetching cycle analysis:', err)
        setError('Failed to load ring analysis')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalysis()
  }, [analysisId, ringIndex])

  if (loading) {
    return (
      <div className="cycle-analysis-panel loading">
        <div className="skeleton-panel"></div>
      </div>
    )
  }

  if (error) {
    return <div className="cycle-analysis-panel error">{error}</div>
  }

  if (!analysis) return null

  return (
    <div className="cycle-analysis-panel">
      <h3>🔄 Ring Analysis</h3>
      
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'participants' ? 'active' : ''}`}
          onClick={() => setActiveTab('participants')}
        >
          Participants
        </button>
        <button 
          className={`tab ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          AI Analysis
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {analysis.ring_details && (
              <>
                <p><strong>Ring Length:</strong> {analysis.ring_details.length} accounts</p>
                <p><strong>Total Volume:</strong> ${(analysis.ring_details.total_amount || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}</p>
                <p><strong>Detection Type:</strong> {analysis.ring_details.type || 'Cycle'}</p>
              </>
            )}
          </div>
        )}

        {activeTab === 'participants' && (
          <div className="participants-tab">
            {analysis.participants && analysis.participants.length > 0 ? (
              <ul className="participants-list">
                {analysis.participants.map((participant, idx) => (
                  <li key={idx} className="participant">
                    <span className="account-id">{participant}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No participants data available</p>
            )}
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="analysis-tab">
            {analysis.ai_analysis ? (
              <p className="analysis-text">{analysis.ai_analysis}</p>
            ) : (
              <p>No AI analysis available</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default CycleAnalysisPanel
