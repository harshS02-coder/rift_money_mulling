import React, { useState, useEffect } from 'react'
import { getRecommendations } from '../services/api'
import '../styles/RecommendationsList.css'

function RecommendationsList({ accountId }) {
  const [recommendations, setRecommendations] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expandedSteps, setExpandedSteps] = useState({})

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!accountId) return

      setLoading(true)
      setError(null)
      try {
        const data = await getRecommendations(accountId)
        setRecommendations(data)
      } catch (err) {
        console.error('Error fetching recommendations:', err)
        setError('Failed to load recommendations')
      } finally {
        setLoading(false)
      }
    }

    fetchRecommendations()
  }, [accountId])

  const toggleStep = (idx) => {
    setExpandedSteps(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }))
  }

  if (loading) {
    return (
      <div className="recommendations-list loading">
        <div className="skeleton-list"></div>
      </div>
    )
  }

  if (error) {
    return <div className="recommendations-list error">{error}</div>
  }

  if (!recommendations || !recommendations.steps) return null

  return (
    <div className="recommendations-list">
      <h4>📋 Investigation Steps</h4>
      <ol className="steps-list">
        {recommendations.steps.map((step, idx) => (
          <li key={idx} className="step-item">
            <div 
              className="step-header"
              onClick={() => toggleStep(idx)}
            >
              <span className="step-title">{step.title || `Step ${idx + 1}`}</span>
              {step.priority && <span className={`priority-badge ${step.priority.toLowerCase()}`}>{step.priority}</span>}
            </div>
            {expandedSteps[idx] && step.description && (
              <div className="step-details">
                <p>{step.description}</p>
              </div>
            )}
          </li>
        ))}
      </ol>
    </div>
  )
}

export default RecommendationsList
