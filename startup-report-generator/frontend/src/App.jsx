import React, { useState } from 'react'
import './App.css'

function App() {
  const [company, setCompany] = useState('')
  const [companyUrl, setCompanyUrl] = useState('')
  const [reportType, setReportType] = useState('one_pager')
  const [generateBoth, setGenerateBoth] = useState(false)
  const [pitchDeckContent, setPitchDeckContent] = useState('')
  const [internalNotes, setInternalNotes] = useState('')
  const [notesFile, setNotesFile] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [message, setMessage] = useState('')



  const readTextFile = async (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target.result)
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }



  const handleNotesDrop = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    const files = Array.from(e.dataTransfer.files)
    const txtFile = files.find(file => file.type === 'text/plain' || file.name.endsWith('.txt'))
    
    if (txtFile) {
      setNotesFile(txtFile)
      setMessage('Loading text file...')
      const content = await readTextFile(txtFile)
      setInternalNotes(content)
      setMessage('Text file loaded successfully!')
    } else {
      setMessage('Please drop a TXT file for internal notes')
    }
  }

  const handleNotesFileChange = async (e) => {
    const file = e.target.files[0]
    if (file && (file.type === 'text/plain' || file.name.endsWith('.txt'))) {
      setNotesFile(file)
      setMessage('Loading text file...')
      const content = await readTextFile(file)
      setInternalNotes(content)
      setMessage('Text file loaded successfully!')
    }
  }

  const generateSingleReport = async (companyName, url, type) => {
    const response = await fetch('http://localhost:8000/generate-report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_name: companyName,
        company_url: url || `https://${companyName.toLowerCase().replace(/\s+/g, '')}.com`,
        report_type: type,
        pitch_deck_content: pitchDeckContent,
        internal_notes: internalNotes
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(`HTTP ${response.status}: ${errorData.detail || 'Unknown error'}`)
    }

    const blob = await response.blob()
    
    // Create download link
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.style.display = 'none'
    a.href = downloadUrl
    a.download = `${companyName.toLowerCase().replace(/\s+/g, '_')}_${type}.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(downloadUrl)
    document.body.removeChild(a)

    return `${companyName}_${type}.pdf`
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!company.trim()) {
      setMessage('Please enter a company name')
      return
    }

    setIsGenerating(true)
    const companyName = company.trim()
    const url = companyUrl.trim()

    try {
      if (generateBoth) {
        setMessage('Generating both reports... This may take several minutes.')
        
        // Generate both reports
        const onePagerPromise = generateSingleReport(companyName, url, 'one_pager')
        const deepDivePromise = generateSingleReport(companyName, url, 'deep_dive')
        
        const [onePagerFile, deepDiveFile] = await Promise.all([onePagerPromise, deepDivePromise])
        
        setMessage(`Both reports generated successfully! Downloaded: ${onePagerFile} and ${deepDiveFile}`)
      } else {
        setMessage(`Generating ${reportType === 'one_pager' ? 'one-pager' : 'deep dive'} report... This may take a few minutes.`)
        
        const filename = await generateSingleReport(companyName, url, reportType)
        setMessage(`Report generated successfully! Downloaded: ${filename}`)
      }
    } catch (error) {
      console.error('Error generating report:', error)
      setMessage(`Error generating report: ${error.message}`)
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Startup Report Generator</h1>
        <p>Generate professional investment reports for any company</p>
      </header>

      <main className="App-main">
        <form onSubmit={handleSubmit} className="report-form">
          <div className="form-group">
            <label htmlFor="company">Company Name:</label>
            <input
              type="text"
              id="company"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g., Tesla, Microsoft, OpenAI"
              disabled={isGenerating}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="companyUrl">Company Website (optional):</label>
            <input
              type="url"
              id="companyUrl"
              value={companyUrl}
              onChange={(e) => setCompanyUrl(e.target.value)}
              placeholder="e.g., https://tesla.com (auto-generated if empty)"
              disabled={isGenerating}
            />
            <small>If empty, we'll auto-generate the URL based on company name</small>
          </div>

          <div className="form-group">
            <label htmlFor="pitchDeckContent">Pitch Deck Content (optional):</label>
            <textarea
              id="pitchDeckContent"
              value={pitchDeckContent}
              onChange={(e) => setPitchDeckContent(e.target.value)}
              placeholder="Paste key information from your pitch deck here to enhance research accuracy..."
              disabled={isGenerating}
              rows={4}
            />
            <small>Include key points from your pitch deck to improve research quality</small>
          </div>

          <div className="form-group">
            <label htmlFor="internalNotes">Internal Notes (optional):</label>
            <div 
              className={`dropzone notes-dropzone ${notesFile ? 'has-file' : ''}`}
              onDragOver={handleDragOver}
              onDragEnter={handleDragEnter}
              onDragLeave={handleDragLeave}
              onDrop={handleNotesDrop}
            >
              <input
                type="file"
                accept=".txt"
                onChange={handleNotesFileChange}
                disabled={isGenerating}
                className="file-input"
                id="notesFile"
              />
              <label htmlFor="notesFile" className="file-label">
                {notesFile ? (
                  <span>📝 {notesFile.name}</span>
                ) : (
                  <>
                    <span>📁 Drop TXT file here or click to upload</span>
                    <span className="drag-hint">Or type/paste text below</span>
                  </>
                )}
              </label>
            </div>
            <textarea
              id="internalNotes"
              value={internalNotes}
              onChange={(e) => setInternalNotes(e.target.value)}
              placeholder="Paste or type your internal notes, research insights, competitive analysis, or additional context here..."
              disabled={isGenerating}
              rows={4}
              className="notes-textarea"
            />
            <small>Upload TXT file or paste research notes, competitive insights, or additional context</small>
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={generateBoth}
                onChange={(e) => setGenerateBoth(e.target.checked)}
                disabled={isGenerating}
              />
              Generate Both Reports (One-Pager + Deep Dive)
            </label>
          </div>

          {!generateBoth && (
            <div className="form-group">
              <label htmlFor="reportType">Report Type:</label>
              <select
                id="reportType"
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                disabled={isGenerating}
              >
                <option value="one_pager">One-Pager (Executive Summary)</option>
                <option value="deep_dive">Deep Dive (Comprehensive Analysis)</option>
              </select>
            </div>
          )}

          <button 
            type="submit" 
            className="generate-btn"
            disabled={isGenerating}
          >
            {isGenerating 
              ? (generateBoth ? 'Generating Both Reports...' : 'Generating...') 
              : (generateBoth ? 'Generate Both Reports' : 'Generate Report')
            }
          </button>
        </form>

        {message && (
          <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}


      </main>
    </div>
  )
}

export default App
