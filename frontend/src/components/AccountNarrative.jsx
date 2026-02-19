import React, { useState, useEffect } from 'react'
import { getAccountNarrative } from '../services/api'
import '../styles/AccountNarrative.css'

function AccountNarrative({ accountId }) {
  const [narrative, setNarrative] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchNarrative = async () => {
      if (!accountId) return

      setLoading(true)
      setError(null)
      try {
        const data = await getAccountNarrative(accountId)
        setNarrative(data)
      } catch (err) {
        console.error('Error fetching account narrative:', err)
        setError('Failed to load account narrative')
      } finally {
        setLoading(false)
      }
    }

    fetchNarrative()
  }, [accountId])

  if (loading) {
    return (
      <div className="account-narrative loading">
        <div className="skeleton-text"></div>
      </div>
    )
  }

  if (error) {
    return <div className="account-narrative error">{error}</div>
  }

  if (!narrative) return null

  return (
    <div className="account-narrative">
      <h4>💼 Account Risk Profile</h4>
      <div className="narrative-content">
        <p className="account-id">Account: <strong>{accountId}</strong></p>
        <p className="narrative-text">{narrative.narrative}</p>
        {narrative.risk_level && (
          <div className={`risk-badge ${narrative.risk_level.toLowerCase()}`}>
            {narrative.risk_level} RISK
          </div>
        )}
      </div>
    </div>
  )
}

export default AccountNarrative
