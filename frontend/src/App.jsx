import React, { useState, useEffect } from 'react'
import FileUpload from './components/FileUpload'
import GraphView from './components/GraphView'
import RingTable from './components/RingTable'
import AccountInfo from './components/AccountInfo'
import AccountNarrative from './components/AccountNarrative'
import RecommendationsList from './components/RecommendationsList'
import CycleAnalysisPanel from './components/CycleAnalysisPanel'
import InvestigationSummary from './components/InvestigationSummary'
import SuspiciousAccountsList from './components/SuspiciousAccountsList'
import { healthCheck } from './services/api'
import './App.css'

function App() {
  const [analysisData, setAnalysisData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedAccount, setSelectedAccount] = useState(null)
  const [selectedRing, setSelectedRing] = useState(null)
  const [backendHealthy, setBackendHealthy] = useState(false)

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await healthCheck()
        setBackendHealthy(true)
      } catch (err) {
        console.error('Backend health check failed:', err)
        setBackendHealthy(false)
        setError('Unable to connect to backend. Make sure the FastAPI server is running on http://localhost:8000')
      }
    }
    checkHealth()
  }, [])

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data)
    setSelectedAccount(null)
  }

  const handleAccountClick = (accountId) => {
    const account = analysisData?.account_scores.find(
      (s) => s.account_id === accountId
    )
    setSelectedAccount(account)
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>🔍 RIFT 2026</h1>
            <p>Financial Ring Forensic Tracker - Money Muling Detection Engine</p>
          </div>
          <div className="header-status">
            <div className={`status-indicator ${backendHealthy ? 'healthy' : 'unhealthy'}`}></div>
            <span>{backendHealthy ? 'Backend Connected' : 'Backend Disconnected'}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <aside className="app-sidebar">
          <FileUpload
            onAnalysisComplete={handleAnalysisComplete}
            onLoading={setLoading}
            onError={setError}
          />
          {error && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
              <button onClick={() => setError(null)}>Dismiss</button>
            </div>
          )}
          {loading && (
            <div className="loading-indicator">
              <div className="spinner"></div>
              <p>Analyzing transactions...</p>
            </div>
          )}
          {analysisData && (
            <>
              {/* Investigation Summary - AI Generated Overview */}
              <InvestigationSummary analysisId={analysisData.analysis_id} />
              
              {/* Selected Account LLM Analysis */}
              {selectedAccount && (
                <div className="account-llm-section">
                  <AccountNarrative accountId={selectedAccount.account_id} />
                  <RecommendationsList accountId={selectedAccount.account_id} />
                </div>
              )}
              
              {/* Selected Ring Analysis */}
              {selectedRing && (
                <div className="ring-llm-section">
                  <CycleAnalysisPanel analysisId={analysisData.analysis_id} ringIndex={selectedRing.index} />
                </div>
              )}
              
              <div className="analysis-summary">
              <h3>📊 Analysis Summary</h3>
              
              {/* Transaction Statistics */}
              <div className="summary-section">
                <h4>Transaction Data</h4>
                <div className="summary-stat">
                  <span className="stat-label">Total Transactions</span>
                  <span className="stat-value">{analysisData.total_transactions}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Total Volume</span>
                  <span className="stat-value">${(analysisData.summary?.total_volume || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Avg Transaction</span>
                  <span className="stat-value">${(analysisData.summary?.avg_transaction || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Median Transaction</span>
                  <span className="stat-value">${(analysisData.summary?.median_transaction || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Max Transaction</span>
                  <span className="stat-value">${(analysisData.summary?.max_transaction || 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
                </div>
              </div>

              {/* Account Statistics */}
              <div className="summary-section">
                <h4>Account Analysis</h4>
                <div className="summary-stat">
                  <span className="stat-label">Total Accounts</span>
                  <span className="stat-value">{analysisData.total_accounts}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Accounts in Rings</span>
                  <span className="stat-value">{analysisData.summary?.accounts_in_rings || 0}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Suspicious Accounts</span>
                  <span className="stat-value">{analysisData.summary?.suspicious_accounts || 0} ({(analysisData.summary?.suspicious_percent || 0).toFixed(1)}%)</span>
                </div>
              </div>

              {/* Detection Results */}
              <div className="summary-section">
                <h4>Pattern Detection</h4>
                <div className="summary-stat">
                  <span className="stat-label">Cycles Detected</span>
                  <span className="stat-value">{analysisData.rings_detected.length}</span>
                </div>
                {analysisData.rings_detected.length > 0 && (
                  <div className="summary-stat">
                    <span className="stat-label">Avg Cycle Length</span>
                    <span className="stat-value">{(analysisData.summary?.avg_cycle_length || 0).toFixed(1)}</span>
                  </div>
                )}
                <div className="summary-stat">
                  <span className="stat-label">Smurfing Alerts</span>
                  <span className="stat-value">{analysisData.smurfing_alerts.length}</span>
                </div>
                <div className="summary-stat">
                  <span className="stat-label">Shell Accounts</span>
                  <span className="stat-value">{analysisData.shell_accounts.length}</span>
                </div>
              </div>

              {/* Risk Assessment */}
              <div className="summary-section">
                <h4>Risk Assessment</h4>
                <div className="summary-stat critical">
                  <span className="stat-label">🚨 Critical Risk</span>
                  <span className="stat-value">{analysisData.critical_accounts.length}</span>
                </div>
                <div className="summary-stat high-risk">
                  <span className="stat-label">⚠️ High Risk</span>
                  <span className="stat-value">{analysisData.high_risk_accounts.length}</span>
                </div>
              </div>
              </div>
            </>
          )}
        </aside>

        <section className="app-content">
          {analysisData ? (
            <>
              <div className="content-grid">
                <div className="graph-section">
                  <GraphView
                    data={analysisData}
                    onAccountClick={handleAccountClick}
                  />
                </div>
                <div className="info-section">
                  <AccountInfo
                    accountDetails={selectedAccount}
                    onClose={() => setSelectedAccount(null)}
                  />
                </div>
              </div>
              <div className="table-section">
                <RingTable
                  rings={analysisData.rings_detected}
                  smurfingAlerts={analysisData.smurfing_alerts}
                  shellAccounts={analysisData.shell_accounts}
                />
              </div>
              <div className="table-section">
                <SuspiciousAccountsList
                  analysisData={analysisData}
                  onAccountSelect={handleAccountClick}
                />
              </div>
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">📊</div>
              <h2>Upload a Transaction File to Begin</h2>
              <p>
                Upload a CSV file containing transaction data to analyze money
                muling patterns using our graph-based detection engine.
              </p>
              <p className="hint">
                Supports CSV with: id, from_account, to_account, amount,
                timestamp
              </p>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          RIFT 2026 © Detecting Financial Crimes Through Graph Analysis | v1.0.0
        </p>
      </footer>
    </div>
  )
}

export default App
