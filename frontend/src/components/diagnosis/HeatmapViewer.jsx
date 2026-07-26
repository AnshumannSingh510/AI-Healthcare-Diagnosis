import React from 'react'

const STORAGE_BASE_URL = import.meta.env.VITE_STORAGE_BASE_URL || 'http://localhost:8000/storage'

// Converts a backend absolute container path like
// "/app/storage/heatmaps/xxx.png" into a servable URL.
function toStorageUrl(path) {
  if (!path) return null
  const marker = '/storage/'
  const idx = path.indexOf(marker)
  const relative = idx >= 0 ? path.slice(idx + marker.length) : path
  return `${STORAGE_BASE_URL}/${relative}`
}

export default function HeatmapViewer({ heatmapPath, altText = 'Grad-CAM heatmap' }) {
  const url = toStorageUrl(heatmapPath)
  if (!url) {
    return <div className="text-gray-400 text-sm italic">Heatmap not yet available.</div>
  }
  return (
    <div className="rounded-lg overflow-hidden border border-gray-200">
      <img src={url} alt={altText} className="w-full object-contain" />
    </div>
  )
}
