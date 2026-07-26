import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const dashboardPath = user?.role === 'doctor' ? '/doctor' : '/patient'

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-10">
      <Link to="/" className="flex items-center gap-2 font-bold text-brand-700 text-lg">
        <span className="inline-block w-2.5 h-2.5 rounded-full bg-brand-500" />
        ChestScan AI
      </Link>

      {user ? (
        <div className="flex items-center gap-6 text-sm">
          <Link to={dashboardPath} className="text-gray-600 hover:text-brand-700">Dashboard</Link>
          <Link to="/upload" className="text-gray-600 hover:text-brand-700">Upload X-ray</Link>
          <Link to="/reports" className="text-gray-600 hover:text-brand-700">Reports</Link>
          <Link to="/chat" className="text-gray-600 hover:text-brand-700">AI Chat</Link>
          <Link to="/settings" className="text-gray-600 hover:text-brand-700">Settings</Link>
          <span className="text-gray-400">|</span>
          <span className="text-gray-700">{user.name} ({user.role})</span>
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-md"
          >
            Log out
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-gray-600 hover:text-brand-700">Log in</Link>
          <Link to="/register" className="bg-brand-600 text-white px-4 py-1.5 rounded-md hover:bg-brand-700">
            Get started
          </Link>
        </div>
      )}
    </nav>
  )
}
