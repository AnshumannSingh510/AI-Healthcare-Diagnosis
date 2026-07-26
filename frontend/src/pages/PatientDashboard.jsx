import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { xrayApi } from '../services/api'
import Card from '../components/common/Card.jsx'

export default function PatientDashboard() {
  const { user } = useAuth()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    xrayApi.history(user.id)
      .then(({ data }) => setHistory(data))
      .finally(() => setLoading(false))
  }, [user])

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome back, {user?.name}</h1>
          <p className="text-gray-500 text-sm mt-1">Here's an overview of your chest X-ray history.</p>
        </div>
        <Link to="/upload" className="bg-brand-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-brand-700">
          + Upload X-ray
        </Link>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <Card title="Total Scans"><p className="text-3xl font-bold text-gray-800">{history.length}</p></Card>
        <Card title="Latest Finding">
          <p className="text-lg font-semibold text-gray-800">{history[0]?.disease || 'No scans yet'}</p>
        </Card>
        <Card title="Latest Severity">
          <p className="text-lg font-semibold text-gray-800">{history[0]?.severity || '—'}</p>
        </Card>
      </div>

      <Card title="Prediction History">
        {loading ? (
          <p className="text-gray-400 text-sm">Loading...</p>
        ) : history.length === 0 ? (
          <p className="text-gray-400 text-sm">No X-rays uploaded yet. Upload your first scan to get started.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-200">
                <th className="py-2">Date</th><th>Finding</th><th>Confidence</th><th>Severity</th><th></th>
              </tr>
            </thead>
            <tbody>
              {history.map((p) => (
                <tr key={p.id} className="border-b border-gray-100">
                  <td className="py-2">{new Date(p.created_at).toLocaleDateString()}</td>
                  <td>{p.disease}</td>
                  <td>{Math.round(p.confidence * 100)}%</td>
                  <td>{p.severity}</td>
                  <td>
                    <Link to={`/results/${p.id}`} className="text-brand-600 font-medium">View</Link>
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
