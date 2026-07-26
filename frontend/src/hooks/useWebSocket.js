import { useEffect, useRef, useState, useCallback } from 'react'
import { xrayApi } from '../services/api'

/**
 * Polls the xray status endpoint until processing completes.
 * A true WebSocket channel can replace this later (e.g. FastAPI
 * WebSocket route pushing status updates) without changing the
 * component API this hook exposes.
 */
export function useXrayStatusPolling(xrayId, { intervalMs = 2000 } = {}) {
  const [status, setStatus] = useState('uploaded')
  const [predictionId, setPredictionId] = useState(null)
  const [error, setError] = useState(null)
  const timerRef = useRef(null)

  const poll = useCallback(async () => {
    if (!xrayId) return
    try {
      const { data } = await xrayApi.status(xrayId)
      setStatus(data.status)
      if (data.prediction_id) setPredictionId(data.prediction_id)
      if (data.status === 'completed' || data.status === 'failed') {
        clearInterval(timerRef.current)
      }
    } catch (err) {
      setError(err)
      clearInterval(timerRef.current)
    }
  }, [xrayId])

  useEffect(() => {
    if (!xrayId) return
    poll()
    timerRef.current = setInterval(poll, intervalMs)
    return () => clearInterval(timerRef.current)
  }, [xrayId, intervalMs, poll])

  return { status, predictionId, error }
}
