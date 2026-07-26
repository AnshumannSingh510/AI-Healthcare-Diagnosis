import React, { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { xrayApi } from '../../services/api'

export default function XrayDropzone() {
  const [dragActive, setDragActive] = useState(false)
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)
  const navigate = useNavigate()

  const handleFile = (f) => {
    if (!f) return
    if (!['image/png', 'image/jpeg'].includes(f.type)) {
      setError('Only PNG or JPEG images are supported.')
      return
    }
    setError(null)
    setFile(f)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    handleFile(e.dataTransfer.files?.[0])
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      const { data } = await xrayApi.upload(file, (evt) => {
        setProgress(Math.round((evt.loaded * 100) / evt.total))
      })
      navigate(`/results/xray/${data.xray_id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition
          ${dragActive ? 'border-brand-500 bg-brand-50' : 'border-gray-300 bg-gray-50'}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/png,image/jpeg"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        {file ? (
          <p className="text-gray-700 font-medium">{file.name}</p>
        ) : (
          <>
            <p className="text-gray-600 font-medium">Drag & drop a chest X-ray image here</p>
            <p className="text-gray-400 text-sm mt-1">or click to browse (PNG / JPEG, max 15MB)</p>
          </>
        )}
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      {uploading && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-brand-600 h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
        </div>
      )}

      <button
        disabled={!file || uploading}
        onClick={handleUpload}
        className="w-full bg-brand-600 disabled:bg-gray-300 text-white font-medium py-2.5 rounded-lg hover:bg-brand-700 transition"
      >
        {uploading ? `Uploading... ${progress}%` : 'Upload & Analyze'}
      </button>
    </div>
  )
}
