import React, { useRef } from 'react'
import { uploadCSV, analyzeTransactions } from '../services/api'
import '../styles/FileUpload.css'

const FileUpload = ({ onAnalysisComplete, onLoading, onError }) => {
  const fileInputRef = useRef(null)
  const [isDragging, setIsDragging] = React.useState(false)
  const [fileName, setFileName] = React.useState(null)

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      await handleFile(files[0])
    }
  }

  const handleFileClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e) => {
    const files = e.target.files
    if (files.length > 0) {
      await handleFile(files[0])
    }
  }

  const handleFile = async (file) => {
    try {
      if (!file.name.endsWith('.csv')) {
        onError('Please upload a CSV file')
        return
      }

      setFileName(file.name)
      onLoading(true)
      const response = await uploadCSV(file)
      onAnalysisComplete(response.data)
      onError(null)
    } catch (error) {
      console.error('Upload error:', error)
      onError(error.response?.data?.detail || 'Failed to upload and analyze file')
    } finally {
      onLoading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  return (
    <div className="file-upload-container">
      <div className="upload-header">
        <h3>📊 Transaction Data</h3>
      </div>
      
      <div className="upload-button-wrapper">
        <button
          className={`upload-button ${isDragging ? 'dragging' : ''}`}
          onClick={handleFileClick}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          <span className="button-icon">📁</span>
          <span className="button-text">Upload CSV</span>
        </button>
      </div>

      {fileName && (
        <div className="upload-info">
          <p className="file-name">✓ {fileName}</p>
          <p className="format-hint">CSV format: id, from_account, to_account, amount, timestamp</p>
        </div>
      )}
    </div>
  )
}

export default FileUpload
