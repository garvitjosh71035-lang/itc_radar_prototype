import axios from 'axios'

// Declare Vite environment variables for TypeScript
interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

const configured = (import.meta.env.VITE_API_URL || '').trim()

function normalizeApiBase(value: string) {
  const clean = value.replace(/\/+$/, '')
  return clean.endsWith('/api') ? clean : `${clean}/api`
}

// Keep the currently deployed Render API as the zero-config fallback.
// Any VITE_API_URL provided by Render overrides it automatically.
const API_URL = configured
  ? normalizeApiBase(configured)
  : 'https://pace-backend-cqiy.onrender.com/api'

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

export default apiClient
