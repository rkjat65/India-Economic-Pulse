const BASE = '/api'

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json()
}

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail ?? `API error ${res.status}`)
  }
  return res.json()
}

export const api = {
  overview:   () => get('/overview'),
  gdp:        () => get('/gdp'),
  inflation:  () => get('/inflation'),
  trade:      () => get('/trade'),
  forex:      () => get('/forex'),
  rbiRates:   () => get('/rbi-rates'),
  // AI
  aiAnalyze:  (topic, question)         => post('/ai/analyze', { topic, question }),
  aiImage:    (prompt, model)           => post('/ai/image',   { prompt, model }),
  aiCaption:  (template, data, platform) => post('/ai/caption', { template, data, platform }),
  // Content Studio
  studioSnapshot:    ()                    => get('/studio/snapshot'),
  studioTimeseries:  (indicator, n = 16)   => get(`/studio/timeseries?indicator=${indicator}&n=${n}`),
  studioRankings:    (indicator, n = 10)   => get(`/studio/rankings?indicator=${indicator}&n=${n}`),
  studioPeriods:     ()                    => get('/studio/periods'),
  studioYearSummary: (year)               => get(`/studio/year-summary?year=${year}`),
}

// ── helpers ──────────────────────────────────────────────────
export function fmt(n, decimals = 2) {
  if (n == null) return '—'
  return Number(n).toFixed(decimals)
}

// API returns USD values in millions — convert to readable
export function fmtB(n) {
  if (n == null) return '—'
  const abs = Math.abs(n)
  if (abs >= 1000) return `$${(abs / 1000).toFixed(1)}B`   // millions → billions
  if (abs >= 1)    return `$${abs.toFixed(1)}M`             // stay as millions
  return `$${abs.toFixed(2)}M`
}

export function fmtDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })
}

export function filterByYear(data, dateKey, min, max) {
  return data.filter(r => {
    const yr = new Date(r[dateKey]).getFullYear()
    return yr >= min && yr <= max
  })
}

export function yearRange(data, dateKey = 'date') {
  if (!data?.length) return [2012, 2025]
  const years = data.map(r => new Date(r[dateKey]).getFullYear())
  return [Math.min(...years), Math.max(...years)]
}
