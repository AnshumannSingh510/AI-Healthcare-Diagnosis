import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { predictionApi, reportApi } from '../services/api'
import Card from '../components/common/Card.jsx'
import Disclaimer from '../components/common/Disclaimer.jsx'
import ConfidenceBadge from '../components/diagnosis/ConfidenceBadge.jsx'
import HeatmapViewer from '../components/diagnosis/HeatmapViewer.jsx'

export default function PredictionResultPage() {
  const { predictionId } = useParams()
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    predictionApi.get(predictionId)
      .then(({ data }) => setPrediction(data))
      .finally(() => setLoading(false))
  }, [predictionId])

  const handleGenerateReport = async () => {
    setGenerating(true)
    try {
      const { data } = await reportApi.generate(predictionId, {})
      const res = await reportApi.download(data.id)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `report_${data.id}.pdf`
      a.click()
    } finally {
      setGenerating(false)
    }
  }

  if (loading) return <div className="max-w-3xl mx-auto px-6 py-10 text-gray-400">Loading...</div>
  if (!prediction) return <div className="max-w-3xl mx-auto px-6 py-10 text-gray-400">Prediction not found.</div>

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Diagnosis Result</h1>
        <Link to="/patient" className="text-sm text-brand-600 font-medium">Back to dashboard</Link>
      </div>

      <Card>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <p className="text-gray-400 text-sm">Predicted Finding</p>
            <p className="text-2xl font-bold text-gray-900">{prediction.disease}</p>
          </div>
          <ConfidenceBadge confidence={prediction.confidence} severity={prediction.severity} />
        </div>
      </Card>

      <Card title="Grad-CAM Heatmap">
        <HeatmapViewer heatmapPath={prediction.heatmap_path} />
      </Card>

      <Card title="AI Explanation">
        <p className="text-gray-700 text-sm leading-relaxed">{prediction.ai_explanation}</p>
      </Card>

      <Card title="Clinical Recommendations">
        <ul className="list-disc list-inside space-y-1 text-gray-700 text-sm">
          {(prediction.recommendation || []).map((r, i) => <li key={i}>{r}</li>)}
        </ul>
      </Card>

      {prediction.notes && (
        <Card title="Doctor's Notes">
          <p className="text-gray-700 text-sm">{prediction.notes}</p>
        </Card>
      )}

      <Disclaimer text={prediction.disclaimer} />

      <button
        onClick={handleGenerateReport}
        disabled={generating}
        className="bg-brand-600 disabled:bg-gray-300 text-white font-medium px-6 py-2.5 rounded-lg hover:bg-brand-700"
      >
        {generating ? 'Generating PDF...' : 'Download PDF Report'}
      </button>
    </div>
  )
}
