import React from 'react'

const SEVERITY_COLORS = {
  'Mild / Uncertain': 'bg-yellow-100 text-yellow-800 border-yellow-300',
  'Moderate': 'bg-orange-100 text-orange-800 border-orange-300',
  'High Confidence': 'bg-red-100 text-red-800 border-red-300',
}

export default function ConfidenceBadge({ confidence, severity }) {
  const pct = Math.round((confidence || 0) * 100)
  const colorClass = SEVERITY_COLORS[severity] || 'bg-gray-100 text-gray-800 border-gray-300'

  return (
    <div className="flex items-center gap-4">
      <div className="relative w-24 h-24">
        <svg viewBox="0 0 36 36" className="w-24 h-24 -rotate-90">
          <path
            className="text-gray-200"
            strokeWidth="3.5"
            stroke="currentColor"
            fill="none"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            className="text-brand-600"
            strokeWidth="3.5"
            strokeDasharray={`${pct}, 100`}
            strokeLinecap="round"
            stroke="currentColor"
            fill="none"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center font-semibold text-gray-800">
          {pct}%
        </div>
      </div>
      {severity && (
        <span className={`text-xs font-medium border rounded-full px-3 py-1 ${colorClass}`}>
          {severity}
        </span>
      )}
    </div>
  )
}
