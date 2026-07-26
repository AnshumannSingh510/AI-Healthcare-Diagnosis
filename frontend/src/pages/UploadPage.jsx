import React from 'react'
import Card from '../components/common/Card.jsx'
import Disclaimer from '../components/common/Disclaimer.jsx'
import XrayDropzone from '../components/upload/XrayDropzone.jsx'

export default function UploadPage() {
  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Upload Chest X-ray</h1>
      <p className="text-gray-500 text-sm mb-6">
        Your image will be analyzed by our AI model. This typically takes a few seconds.
      </p>
      <Card className="mb-6">
        <XrayDropzone />
      </Card>
      <Disclaimer />
    </div>
  )
}
