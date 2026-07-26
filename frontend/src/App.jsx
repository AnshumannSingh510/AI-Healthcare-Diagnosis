import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/common/Navbar.jsx'
import ProtectedRoute from './components/common/ProtectedRoute.jsx'

import Landing from './pages/Landing.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import PatientDashboard from './pages/PatientDashboard.jsx'
import DoctorDashboard from './pages/DoctorDashboard.jsx'
import UploadPage from './pages/UploadPage.jsx'
import XrayProcessingPage from './pages/XrayProcessingPage.jsx'
import PredictionResultPage from './pages/PredictionResultPage.jsx'
import ReportHistoryPage from './pages/ReportHistoryPage.jsx'
import DoctorReviewPage from './pages/DoctorReviewPage.jsx'
import ChatPage from './pages/ChatPage.jsx'
import SettingsPage from './pages/SettingsPage.jsx'

export default function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route path="/patient" element={
          <ProtectedRoute allowedRoles={['patient']}><PatientDashboard /></ProtectedRoute>
        } />
        <Route path="/doctor" element={
          <ProtectedRoute allowedRoles={['doctor', 'admin']}><DoctorDashboard /></ProtectedRoute>
        } />
        <Route path="/doctor/review/:patientId" element={
          <ProtectedRoute allowedRoles={['doctor', 'admin']}><DoctorReviewPage /></ProtectedRoute>
        } />

        <Route path="/upload" element={
          <ProtectedRoute allowedRoles={['patient']}><UploadPage /></ProtectedRoute>
        } />
        <Route path="/results/xray/:xrayId" element={
          <ProtectedRoute><XrayProcessingPage /></ProtectedRoute>
        } />
        <Route path="/results/:predictionId" element={
          <ProtectedRoute><PredictionResultPage /></ProtectedRoute>
        } />

        <Route path="/reports" element={
          <ProtectedRoute><ReportHistoryPage /></ProtectedRoute>
        } />
        <Route path="/chat" element={
          <ProtectedRoute><ChatPage /></ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute><SettingsPage /></ProtectedRoute>
        } />
      </Routes>
    </div>
  )
}
