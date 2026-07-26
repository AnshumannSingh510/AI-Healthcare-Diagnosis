import React, { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { xrayApi, reportApi } from '../services/api'
import Card from '../components/common/Card.jsx'

export default function ReportHistoryPage() {
  const { user } = useAuth()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    xrayApi.history(user.id).then(({ data }) => setHistory(data)).finally(() => setLoading(false))
  }, [user])

  const handleDownload = async (predictionId) => {
    const { data } = await reportApi.generate(predictionId, {})
    const res = await reportApi.download(data.id)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `report_${data.id}.pdf`
    a.click()
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Report History</h1>
      <Card>
        {loading ? (
          <p className="text-gray-400 text-sm">Loading...</p>
        ) : history.length === 0 ? (
          <p className="text-gray-400 text-sm">No reports yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-200">
                <th className="py-2">Date</th><th>Finding</th><th>Severity</th><th></th>
              </tr>
            </thead>
            <tbody>
              {history.map((p) => (
                <tr key={p.id} className="border-b border-gray-100">
                  <td className="py-2">{new Date(p.created_at).toLocaleDateString()}</td>
                  <td>{p.disease}</td>
                  <td>{p.severity}</td>
                  <td>
                    <button onClick={() => handleDownload(p.id)} className="text-brand-600 font-medium">
                      Download PDF
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
