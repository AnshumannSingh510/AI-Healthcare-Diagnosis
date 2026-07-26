import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { doctorApi } from '../services/api'
import Card from '../components/common/Card.jsx'

export default function DoctorDashboard() {
  const { user } = useAuth()
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) return
    doctorApi.patients(user.id)
      .then(({ data }) => setPatients(data))
      .finally(() => setLoading(false))
  }, [user])

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Welcome, Dr. {user?.name}</h1>
      <p className="text-gray-500 text-sm mb-8">Review AI predictions for your assigned patients.</p>

      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <Card title="Assigned Patients"><p className="text-3xl font-bold text-gray-800">{patients.length}</p></Card>
        <Card title="Pending Reviews">
          <p className="text-3xl font-bold text-gray-800">—</p>
          <p className="text-xs text-gray-400 mt-1">Open a patient's history to review individual predictions.</p>
        </Card>
      </div>

      <Card title="Assigned Patients">
        {loading ? (
          <p className="text-gray-400 text-sm">Loading...</p>
        ) : patients.length === 0 ? (
          <p className="text-gray-400 text-sm">No patients assigned yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-200">
                <th className="py-2">Name</th><th>Email</th><th></th>
              </tr>
            </thead>
            <tbody>
              {patients.map((p) => (
                <tr key={p.id} className="border-b border-gray-100">
                  <td className="py-2">{p.name}</td>
                  <td>{p.email}</td>
                  <td>
                    <Link to={`/doctor/review/${p.id}`} className="text-brand-600 font-medium">Review history</Link>
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
