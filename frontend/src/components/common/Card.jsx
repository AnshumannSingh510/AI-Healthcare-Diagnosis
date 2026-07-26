import React from 'react'

export default function Card({ title, children, className = '' }) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200 shadow-sm p-6 ${className}`}>
      {title && <h3 className="text-base font-semibold text-gray-800 mb-4">{title}</h3>}
      {children}
    </div>
  )
}
