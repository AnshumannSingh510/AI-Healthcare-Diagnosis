import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import Card from '../components/common/Card.jsx'

export default function SettingsPage() {
  const { user } = useAuth()
  const [name, setName] = useState(user?.name || '')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [message, setMessage] = useState(null)

  // NOTE: Profile update / password change endpoints are not part of the
  // MVP checklist's required endpoint list; wire these handlers to new
  // PATCH /api/v1/auth/me and POST /api/v1/auth/change-password endpoints
  // when added.
  const handleSaveProfile = (e) => {
    e.preventDefault()
    setMessage('Profile update endpoint not yet implemented in this MVP.')
  }

  const handleChangePassword = (e) => {
    e.preventDefault()
    setMessage('Password change endpoint not yet implemented in this MVP.')
  }

  return (
    <div className="max-w-xl mx-auto px-6 py-10 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      <Card title="Profile">
        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Email</label>
            <input disabled value={user?.email || ''}
              className="mt-1 w-full border border-gray-200 bg-gray-50 rounded-lg px-3 py-2 text-gray-400" />
          </div>
          <button className="bg-brand-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-brand-700">
            Save changes
          </button>
        </form>
      </Card>

      <Card title="Change Password">
        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Current password</label>
            <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)}
              className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">New password</label>
            <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)}
              className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <button className="bg-brand-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-brand-700">
            Update password
          </button>
        </form>
      </Card>

      {message && <p className="text-sm text-gray-500">{message}</p>}
    </div>
  )
}
