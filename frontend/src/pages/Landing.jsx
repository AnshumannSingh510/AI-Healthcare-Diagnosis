import React from 'react'
import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-20 text-center">
      <span className="inline-block bg-brand-100 text-brand-700 text-xs font-semibold px-3 py-1 rounded-full mb-6">
        AI-Assisted Clinical Decision Support
      </span>
      <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
        Faster chest X-ray insight,<br /> reviewed by real doctors.
      </h1>
      <p className="text-gray-600 mt-6 max-w-2xl mx-auto">
        Upload a chest X-ray and get an AI-generated prediction with a Grad-CAM heatmap,
        plain-language explanation, and clinical recommendations — routed to a licensed
        doctor for review before anything is finalized.
      </p>
      <div className="mt-8 flex justify-center gap-4">
        <Link to="/register" className="bg-brand-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-brand-700">
          Get started
        </Link>
        <Link to="/login" className="bg-white border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-50">
          Log in
        </Link>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mt-20 text-left">
        {[
          { title: 'Upload & Analyze', desc: 'Drag and drop a chest X-ray. A DenseNet121 deep learning model runs analysis in seconds.' },
          { title: 'Explainable AI', desc: 'Grad-CAM heatmaps and plain-language explanations show exactly what the model saw.' },
          { title: 'Doctor Reviewed', desc: 'Every AI result is routed to a licensed doctor for review, notes, and approval before a report is finalized.' },
        ].map((f) => (
          <div key={f.title} className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-800 mb-2">{f.title}</h3>
            <p className="text-gray-500 text-sm">{f.desc}</p>
          </div>
        ))}
      </div>

      <p className="text-xs text-gray-400 mt-16 max-w-xl mx-auto">
        This platform is a clinical decision-support prototype, not an approved medical device.
        All predictions require professional medical confirmation.
      </p>
    </div>
  )
}
