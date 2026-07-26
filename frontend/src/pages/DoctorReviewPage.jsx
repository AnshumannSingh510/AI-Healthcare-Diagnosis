import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { xrayApi, doctorApi, reportApi } from '../services/api'
import Card from '../components/common/Card.jsx'
import Disclaimer from '../components/common/Disclaimer.jsx'
import HeatmapViewer from '../components/diagnosis/HeatmapViewer.jsx'
import ConfidenceBadge from '../components/diagnosis/ConfidenceBadge.jsx'

export default function DoctorReviewPage() {
  const { patientId } = useParams()
  const [history, setHistory] = useState([])
  const [selected, setSelected] = useState(null)
  const [notes, setNotes] = useState('')
  const [comment, setComment] = useState('')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    xrayApi.history(patientId).then(({ data }) => {
      setHistory(data)
      if (data.length > 0) {
        setSelected(data[0])
        setNotes(data[0].notes || '')
      }
    })
  }, [patientId])

  const handleSelect = (p) => {
    setSelected(p)
    setNotes(p.notes || '')
    setMessage(null)
  }

  const handleSaveReview = async (approve) => {
    setSaving(true)
    setMessage(null)
    try {
      await doctorApi.review(selected.id, { notes, approve, doctor_comment: comment })
      if (approve) {
        const { data } = await reportApi.generate(selected.id, { doctor_comment: comment, approve: true })
        setMessage(`Report approved and generated (report id: ${data.id}).`)
      } else {
        setMessage('Notes saved.')
      }
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Failed to save review.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 grid md:grid-cols-3 gap-6">
      <Card title="Scan History" className="md:col-span-1 h-fit">
        <ul className="space-y-2">
          {history.map((p) => (
            <li key={p.id}>
              <button
                onClick={() => handleSelect(p)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm ${selected?.id === p.id ? 'bg-brand-50 text-brand-700' : 'hover:bg-gray-50'}`}
              >
                <p className="font-medium">{p.disease}</p>
                <p className="text-xs text-gray-400">{new Date(p.created_at).toLocaleDateString()}</p>
              </button>
            </li>
          ))}
          {history.length === 0 && <p className="text-gray-400 text-sm">No scans found.</p>}
        </ul>
      </Card>

      <div className="md:col-span-2 space-y-6">
        {selected ? (
          <>
            <Card>
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <p className="text-gray-400 text-sm">Predicted Finding</p>
                  <p className="text-xl font-bold text-gray-900">{selected.disease}</p>
                </div>
                <ConfidenceBadge confidence={selected.confidence} severity={selected.severity} />
              </div>
            </Card>

            <Card title="Grad-CAM Heatmap">
              <HeatmapViewer heatmapPath={selected.heatmap_path} />
            </Card>

            <Card title="AI Explanation">
              <p className="text-sm text-gray-700">{selected.ai_explanation}</p>
            </Card>

            <Card title="Doctor Notes & Comment">
              <textarea
                value={notes} onChange={(e) => setNotes(e.target.value)}
                placeholder="Clinical notes (visible to patient)"
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <textarea
                value={comment} onChange={(e) => setComment(e.target.value)}
                placeholder="Comment to include on the PDF report"
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => handleSaveReview(false)} disabled={saving}
                  className="bg-gray-100 text-gray-700 px-5 py-2 rounded-lg font-medium hover:bg-gray-200"
                >
                  Save Notes
                </button>
                <button
                  onClick={() => handleSaveReview(true)} disabled={saving}
                  className="bg-brand-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-brand-700"
                >
                  Approve & Generate Report
                </button>
              </div>
              {message && <p className="text-sm text-gray-600 mt-3">{message}</p>}
            </Card>

            <Disclaimer />
          </>
        ) : (
          <Card><p className="text-gray-400 text-sm">Select a scan to review.</p></Card>
        )}
      </div>
    </div>
  )
}
