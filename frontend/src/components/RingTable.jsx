import React from 'react'
import '../styles/RingTable.css'

const RingTable = ({ rings, smurfingAlerts, shellAccounts }) => {
  const [activeTab, setActiveTab] = React.useState('rings')

  const renderRingRow = (ring, index) => (
    <tr key={`ring-${index}`} className={`ring-row`}>
      <td className="ring-id">{ring.ring_id}</td>
      <td className="accounts">
        <div className="account-list">
          {ring.accounts.map((acc, i) => (
            <span key={`${ring.ring_id}-${i}`} className="account-badge">
              {acc}
            </span>
          ))}
        </div>
      </td>
      <td className="length">{ring.length}</td>
      <td className="amount">${ring.total_amount.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}</td>
      <td className="txn-count">{ring.transactions.length}</td>
    </tr>
  )

  const renderSmurfingRow = (alert, index) => (
    <tr key={`smurf-${index}`} className="smurf-row">
      <td className="account-id">{alert.account_id}</td>
      <td className="txn-count">{alert.transaction_count}</td>
      <td className="fan-in-out">
        <span className="fan-in">{alert.fan_in}→</span>
        <span>{alert.account_id}</span>
        <span className="fan-out">→{alert.fan_out}</span>
      </td>
      <td className="amount">${alert.total_amount.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}</td>
      <td className="risk-score">
        <div className="score-bar">
          <div
            className="score-fill"
            style={{
              width: `${alert.risk_score}%`,
              backgroundColor:
                alert.risk_score > 80
                  ? '#d32f2f'
                  : alert.risk_score > 60
                    ? '#f57c00'
                    : alert.risk_score > 40
                      ? '#fbc02d'
                      : '#388e3c',
            }}
          ></div>
          <span className="score-text">{alert.risk_score.toFixed(1)}</span>
        </div>
      </td>
    </tr>
  )

  const renderShellRow = (shell, index) => (
    <tr key={`shell-${index}`} className="shell-row">
      <td className="account-id">{shell.account_id}</td>
      <td className="txn-count">{shell.total_transactions}</td>
      <td className="throughput">${shell.total_throughput.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}</td>
      <td className="avg-value">${shell.avg_transaction_value.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}</td>
      <td className="risk-score">
        <div className="score-bar">
          <div
            className="score-fill"
            style={{
              width: `${shell.risk_score}%`,
              backgroundColor:
                shell.risk_score > 80
                  ? '#d32f2f'
                  : shell.risk_score > 60
                    ? '#f57c00'
                    : shell.risk_score > 40
                      ? '#fbc02d'
                      : '#388e3c',
            }}
          ></div>
          <span className="score-text">{shell.risk_score.toFixed(1)}</span>
        </div>
      </td>
    </tr>
  )

  return (
    <div className="ring-table-container">
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'rings' ? 'active' : ''}`}
          onClick={() => setActiveTab('rings')}
        >
          🔄 Cycles ({rings?.length || 0})
        </button>
        <button
          className={`tab ${activeTab === 'smurfing' ? 'active' : ''}`}
          onClick={() => setActiveTab('smurfing')}
        >
          💰 Smurfing ({smurfingAlerts?.length || 0})
        </button>
        <button
          className={`tab ${activeTab === 'shells' ? 'active' : ''}`}
          onClick={() => setActiveTab('shells')}
        >
          🏚️ Shell Accounts ({shellAccounts?.length || 0})
        </button>
      </div>

      <div className="table-wrapper">
        {activeTab === 'rings' && (
          <table className="data-table rings-table">
            <thead>
              <tr>
                <th>Ring ID</th>
                <th>Accounts Involved</th>
                <th>Length</th>
                <th>Total Amount</th>
                <th>Transactions</th>
              </tr>
            </thead>
            <tbody>
              {rings && rings.length > 0 ? (
                rings.map((ring, idx) => renderRingRow(ring, idx))
              ) : (
                <tr>
                  <td colSpan="5" className="no-data">
                    No cycles detected
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

        {activeTab === 'smurfing' && (
          <table className="data-table smurfing-table">
            <thead>
              <tr>
                <th>Account ID</th>
                <th>Transactions</th>
                <th>Fan In/Out</th>
                <th>Total Amount</th>
                <th>Risk Score</th>
              </tr>
            </thead>
            <tbody>
              {smurfingAlerts && smurfingAlerts.length > 0 ? (
                smurfingAlerts.map((alert, idx) => renderSmurfingRow(alert, idx))
              ) : (
                <tr>
                  <td colSpan="5" className="no-data">
                    No smurfing patterns detected
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

        {activeTab === 'shells' && (
          <table className="data-table shells-table">
            <thead>
              <tr>
                <th>Account ID</th>
                <th>Transactions</th>
                <th>Total Throughput</th>
                <th>Avg per Transaction</th>
                <th>Risk Score</th>
              </tr>
            </thead>
            <tbody>
              {shellAccounts && shellAccounts.length > 0 ? (
                shellAccounts.map((shell, idx) => renderShellRow(shell, idx))
              ) : (
                <tr>
                  <td colSpan="5" className="no-data">
                    No shell accounts detected
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default RingTable
