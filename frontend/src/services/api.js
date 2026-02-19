import axios from 'axios'

// Use environment variable if available, otherwise use localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method.toUpperCase(), config.url)
    return config
  },
  (error) => Promise.reject(error)
)

// Add response interceptor for logging
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// Transaction Analysis APIs
export const analyzeTransactions = (transactions) => {
  return api.post('/api/analyze', { transactions })
}

export const uploadCSV = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return axios.post(`${API_BASE_URL}/api/upload-csv`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getAnalysis = (analysisId) => {
  return api.get(`/api/analysis/${analysisId}`)
}

export const getAccountDetails = (accountId) => {
  return api.get(`/api/accounts/${accountId}`)
}

export const getStatistics = () => {
  return api.get('/api/stats')
}

export const healthCheck = () => {
  return api.get('/')
}

// LLM APIs
export const getLLMStatus = () => {
  return api.get('/api/llm-status')
}

export const getInvestigationSummary = (analysisId) => {
  return api.get(`/api/investigation-summary/${analysisId}`)
    .then(response => response.data)
    .catch(err => {
      console.warn('Failed to fetch investigation summary:', err.message)
      return {
        overview: 'AI summary generation failed',
        top_suspects: [],
        key_findings: []
      }
    })
}

export const getAccountNarrative = (accountId) => {
  return api.get(`/api/account-narrative/${accountId}`)
    .then(response => response.data)
    .catch(err => {
      console.warn('Failed to fetch account narrative:', err.message)
      return {
        narrative: 'Unable to generate AI narrative for this account.',
        risk_level: 'UNKNOWN'
      }
    })
}

export const getRecommendations = (accountId) => {
  return api.get(`/api/recommendations/${accountId}`)
    .then(response => response.data)
    .catch(err => {
      console.warn('Failed to fetch recommendations:', err.message)
      return {
        steps: [
          { title: 'Review Transaction History', priority: 'HIGH', description: 'Examine all transactions' },
          { title: 'Check Connected Accounts', priority: 'HIGH', description: 'Verify account connections' },
          { title: 'Verify Documentation', priority: 'MEDIUM', description: 'Check KYC documents' }
        ]
      }
    })
}

export const getCycleAnalysis = (analysisId, ringIndex) => {
  return api.get(`/api/cycle-analysis/${analysisId}/${ringIndex}`)
    .then(response => response.data)
    .catch(err => {
      console.warn('Failed to fetch cycle analysis:', err.message)
      return {
        ring_details: { length: 0, total_amount: 0 },
        participants: [],
        ai_analysis: 'Unable to generate cycle analysis.'
      }
    })
}

export default api
