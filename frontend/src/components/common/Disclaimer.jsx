import React from 'react'

export default function Disclaimer({ text }) {
  const message =
    text ||
    'This is an AI-assisted prediction and not a confirmed medical diagnosis. Please consult a licensed physician for professional medical advice.'

  return (
    <div className="bg-amber-50 border border-amber-300 text-amber-800 text-sm rounded-lg px-4 py-3 flex gap-2 items-start">
      <span className="mt-0.5">⚠️</span>
      <p>{message}</p>
    </div>
  )
}
