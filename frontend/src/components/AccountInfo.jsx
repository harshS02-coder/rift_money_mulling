import React from 'react'
import '../styles/AccountInfo.css'

const AccountInfo = ({ accountDetails, onClose }) => {
  if (!accountDetails) {
    return (
      <div className="account-info-panel empty">
        <p>Select an account to view details</p>
      </div>
    )
  }

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return '#d32f2f'
      case 'HIGH':
        return '#f57c00'
      case 'MEDIUM':
        return '#fbc02d'
      case 'LOW':
        return '#388e3c'
      default:
        return '#1976d2'
    }
  }

  return (
    <div className="account-info-panel">
      <div className="panel-header">
        <h3>{accountDetails.account_id}</h3>
        <button className="close-btn" onClick={onClose}>
          ✕
        </button>
      </div>

      <div className="risk-indicator">
        <div
          className="risk-badge"
          style={{ backgroundColor: getRiskColor(accountDetails.risk_level) }}
        >
          {accountDetails.risk_level}
        </div>
        <div className="score-display">
          <span className="score-label">Suspicion Score</span>
          <span
            className="score-value"
            style={{ color: getRiskColor(accountDetails.risk_level) }}
          >
            {accountDetails.final_score.toFixed(1)}/100
          </span>
        </div>
      </div>

      <div className="score-breakdown">
        <h4>Risk Factor Breakdown</h4>
        <div className="factor">
          <span className="factor-name">Ring Involvement</span>
          <div className="factor-bar">
            <div
              className="factor-fill"
              style={{ width: `${accountDetails.ring_involvement_score}%` }}
            ></div>
          </div>
          <span className="factor-value">
            {accountDetails.ring_involvement_score.toFixed(1)}
          </span>
        </div>

        <div className="factor">
          <span className="factor-name">Smurfing Behavior</span>
          <div className="factor-bar">
            <div
              className="factor-fill"
              style={{ width: `${accountDetails.smurfing_score}%` }}
            ></div>
          </div>
          <span className="factor-value">
            {accountDetails.smurfing_score.toFixed(1)}
          </span>
        </div>

        <div className="factor">
          <span className="factor-name">Shell Characteristics</span>
          <div className="factor-bar">
            <div
              className="factor-fill"
              style={{ width: `${accountDetails.shell_score}%` }}
            ></div>
          </div>
          <span className="factor-value">
            {accountDetails.shell_score.toFixed(1)}
          </span>
        </div>
      </div>

      {accountDetails.risk_factors && accountDetails.risk_factors.length > 0 && (
        <div className="risk-factors">
          <h4>Identified Risk Factors</h4>
          <ul>
            {accountDetails.risk_factors.map((factor, idx) => (
              <li key={idx}>{factor}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="panel-footer">
        <p className="info-text">
          Click on nodes in the graph to view more details
        </p>
      </div>
    </div>
  )
}

export default AccountInfo
