import React, { useState } from 'react'
import '../styles/SuspiciousAccountsList.css'

function SuspiciousAccountsList({ analysisData, onAccountSelect }) {
  const [sortBy, setSortBy] = useState('risk_score')
  const [filterRisk, setFilterRisk] = useState('all')

  // Get all suspicious accounts
  const suspiciousAccounts = analysisData.account_scores.filter(account => {
    const isSuspicious = 
      analysisData.critical_accounts.includes(account.account_id) || 
      analysisData.high_risk_accounts.includes(account.account_id)
    
    if (filterRisk === 'critical') {
      return analysisData.critical_accounts.includes(account.account_id)
    } else if (filterRisk === 'high') {
      return analysisData.high_risk_accounts.includes(account.account_id)
    }
    return isSuspicious
  })

  // Sort accounts
  const sortedAccounts = [...suspiciousAccounts].sort((a, b) => {
    if (sortBy === 'risk_score') {
      return b.final_score - a.final_score
    } else if (sortBy === 'account_id') {
      return a.account_id.localeCompare(b.account_id)
    } else if (sortBy === 'risk_level') {
      const riskOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }
      return riskOrder[a.risk_level] - riskOrder[b.risk_level]
    }
    return 0
  })

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return '#dc2626'
      case 'HIGH':
        return '#f97316'
      case 'MEDIUM':
        return '#eab308'
      case 'LOW':
        return '#22c55e'
      default:
        return '#666'
    }
  }

  return (
    <div className="suspicious-accounts-list">
      <div className="list-header">
        <h3>🚨 Suspicious Accounts ({suspiciousAccounts.length})</h3>
        <div className="controls">
          <select 
            value={filterRisk} 
            onChange={(e) => setFilterRisk(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Risk Levels</option>
            <option value="critical">🔴 Critical Only</option>
            <option value="high">🟠 High Only</option>
          </select>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="risk_score">Sort by Risk Score</option>
            <option value="risk_level">Sort by Risk Level</option>
            <option value="account_id">Sort by Account ID</option>
          </select>
        </div>
      </div>

      {sortedAccounts.length === 0 ? (
        <div className="empty-state">
          <p>No suspicious accounts found</p>
        </div>
      ) : (
        <div className="accounts-table-wrapper">
          <table className="accounts-table">
            <thead>
              <tr>
                <th className="col-account">Account ID</th>
                <th className="col-risk-level">Risk Level</th>
                <th className="col-score">Risk Score</th>
                <th className="col-breakdown">Score Breakdown</th>
                <th className="col-action">Action</th>
              </tr>
            </thead>
            <tbody>
              {sortedAccounts.map((account, idx) => (
                <tr key={idx} className={`account-row ${account.risk_level.toLowerCase()}`}>
                  <td className="col-account">
                    <code>{account.account_id}</code>
                  </td>
                  <td className="col-risk-level">
                    <span 
                      className="risk-badge"
                      style={{ backgroundColor: getRiskColor(account.risk_level) }}
                    >
                      {account.risk_level}
                    </span>
                  </td>
                  <td className="col-score">
                    <div className="score-container">
                      <span className="score-value">{account.final_score.toFixed(1)}</span>
                      <div className="score-bar">
                        <div 
                          className="score-fill"
                          style={{ 
                            width: `${account.final_score}%`,
                            backgroundColor: getRiskColor(account.risk_level)
                          }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="col-breakdown">
                    <div className="score-breakdown">
                      {account.ring_involvement_score > 0 && (
                        <span className="factor" title="Ring Involvement">
                          🔄 {account.ring_involvement_score.toFixed(0)}
                        </span>
                      )}
                      {account.smurfing_score > 0 && (
                        <span className="factor" title="Smurfing">
                          💰 {account.smurfing_score.toFixed(0)}
                        </span>
                      )}
                      {account.shell_score > 0 && (
                        <span className="factor" title="Shell Activity">
                          🏚️ {account.shell_score.toFixed(0)}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="col-action">
                    <button 
                      className="view-btn"
                      onClick={() => onAccountSelect(account.account_id)}
                      title="View account details"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="list-footer">
        <div className="stats">
          <div className="stat">
            <span className="label">Critical:</span>
            <span className="value critical">{analysisData.critical_accounts.length}</span>
          </div>
          <div className="stat">
            <span className="label">High:</span>
            <span className="value high">{analysisData.high_risk_accounts.length}</span>
          </div>
          <div className="stat">
            <span className="label">Total:</span>
            <span className="value">{suspiciousAccounts.length}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SuspiciousAccountsList
