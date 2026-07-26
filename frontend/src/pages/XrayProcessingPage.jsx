import React, { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useXrayStatusPolling } from '../hooks/useWebSocket.js'
import Card from '../components/common/Card.jsx'

export default function XrayProcessingPage() {
  const { xrayId } = useParams()
  const navigate = useNavigate()
  const { status, predictionId, error } = useXrayStatusPolling(xrayId)

  useEffect(() => {
    if (status === 'completed' && predictionId) {
      navigate(`/results/${predictionId}`, { replace: true })
    }
  }, [status, predictionId, navigate])

  return (
    <div className="max-w-lg mx-auto px-6 py-20">
      <Card className="text-center">
        {status === 'failed' || error ? (
          <>
            <p className="text-red-600 font-medium">Analysis failed.</p>
            <p className="text-gray-500 text-sm mt-2">Please try uploading the image again.</p>
          </>
        ) : (
          <>
            <div className="animate-spin h-10 w-10 border-4 border-brand-500 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-gray-700 font-medium">Analyzing your X-ray...</p>
            <p className="text-gray-400 text-sm mt-1 capitalize">Status: {status}</p>
          </>
        )}
      </Card>
    </div>
  )
}
