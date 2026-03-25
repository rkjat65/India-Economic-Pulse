import { useState, useEffect } from 'react'
import {
  BarChart, Bar, AreaChart, Area, LineChart, Line, ComposedChart,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  ReferenceLine, Cell,
} from 'recharts'
import {
  Sparkles, Download, RefreshCw, Brain, ImageIcon,
  TrendingUp, TrendingDown, Minus, AlertCircle,
} from 'lucide-react'
import ChartCard from '../components/ChartCard'
import { api, fmt, fmtB, fmtDate } from '../lib/api'

const TT = {
  contentStyle: { background: '#1E1E2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 },
  labelStyle:   { color: '#94A3B8' },
}

const TOPICS = [
  { id: 'gdp',       label: 'GDP Growth',    color: '#22C55E', sub: 'Quarterly % YoY' },
  { id: 'inflation', label: 'Inflation',     color: '#F59E0B', sub: 'CPI & WPI % YoY' },
  { id: 'trade',     label: 'Trade Balance', color: '#EF4444', sub: 'Monthly USD' },
  { id: 'forex',     label: 'Forex Reserves',color: '#06B6D4', sub: 'Weekly USD' },
  { id: 'rbi',       label: 'RBI Rates',     color: '#8B5CF6', sub: 'Policy rates %' },
]

const MODELS = [
  { id: 'imagen-4.0-generate-001',      label: 'Imagen 4 (Best)' },
  { id: 'imagen-4.0-fast-generate-001', label: 'Imagen 4 Fast' },
]

const SUGGESTED_PROMPTS = [
  'Futuristic neon infographic: India GDP growth 2012–2025, dark minimal style, glowing cyan charts',
  'Abstract data art: RBI monetary policy timeline, interest rate decisions as flowing neon light streams',
  'Isometric 3D visualization: India forex reserves $700B milestone, amber glow on black background',
  'Sleek economic poster: India trade balance, exports vs imports, neon green and red opposing forces',
  'India inflation heatmap: CPI vs WPI divergence over decade, dark background, RBI target zones visible',
]

// ── Topic chart ───────────────────────────────────────────────
function TopicChart({ topic, data }) {
  if (!data.length) return (
    <div className="flex items-center justify-center h-[240px]">
      <div className="w-5 h-5 border-2 border-cyan border-t-transparent rounded-full animate-spin" />
    </div>
  )

  if (topic === 'gdp') return (
    <>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} barCategoryGap="25%">
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis dataKey="date" tickFormatter={fmtDate} tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={35} />
          <Tooltip {...TT} formatter={v => [`${fmt(v)}%`, 'GDP Growth']} labelFormatter={fmtDate} />
          <ReferenceLine y={0} stroke="rgba(255,255,255,0.15)" />
          <Bar dataKey="gdp_growth" radius={[3, 3, 0, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.gdp_growth >= 0 ? '#22C55E' : '#EF4444'} fillOpacity={0.85} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <Legend color="#22C55E" label="GDP Growth %" />
    </>
  )

  if (topic === 'inflation') return (
    <>
      <ResponsiveContainer width="100%" height={240}>
        <ComposedChart data={data}>
          <defs>
            <linearGradient id="cpiG" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#F59E0B" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis dataKey="date" tickFormatter={fmtDate} tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={35} />
          <Tooltip {...TT}
            formatter={(v, n) => [`${fmt(v)}%`, n === 'cpi_yoy' ? 'CPI' : n === 'wpi_yoy' ? 'WPI' : n]}
            labelFormatter={fmtDate} />
          <ReferenceLine y={4} stroke="#22C55E" strokeDasharray="4 3" strokeWidth={1} />
          <ReferenceLine y={6} stroke="#EF4444" strokeDasharray="4 3" strokeWidth={1} />
          <Area type="monotone" dataKey="cpi_yoy" stroke="#F59E0B" strokeWidth={2}
                fill="url(#cpiG)" dot={false} />
          {data.some(d => d.wpi_yoy != null) && (
            <Line type="monotone" dataKey="wpi_yoy" stroke="#8B5CF6" strokeWidth={1.5}
                  dot={false} strokeDasharray="3 2" connectNulls />
          )}
        </ComposedChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-2 ml-1">
        <Legend color="#F59E0B" label="CPI YoY" />
        <Legend color="#8B5CF6" label="WPI YoY" dash />
        <Legend color="#22C55E" label="RBI Target 4%" dash />
        <Legend color="#EF4444" label="Upper band 6%" dash />
      </div>
    </>
  )

  if (topic === 'trade') return (
    <>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} barCategoryGap="20%">
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis dataKey="date" tickFormatter={fmtDate} tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={v => `$${(v/1e3).toFixed(0)}B`} tick={{ fontSize: 10 }} width={42} />
          <Tooltip {...TT}
            formatter={v => [`$${(v/1e3).toFixed(1)}B`, 'Trade Balance']}
            labelFormatter={fmtDate} />
          <ReferenceLine y={0} stroke="rgba(255,255,255,0.15)" />
          <Bar dataKey="balance_usd" radius={[2, 2, 0, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.balance_usd >= 0 ? '#22C55E' : '#EF4444'} fillOpacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-2 ml-1">
        <Legend color="#22C55E" label="Surplus" />
        <Legend color="#EF4444" label="Deficit" />
      </div>
    </>
  )

  if (topic === 'forex') return (
    <>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="fxAI" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#06B6D4" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis dataKey="date" tickFormatter={fmtDate} tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={v => `$${(v/1e3).toFixed(0)}B`} tick={{ fontSize: 10 }} width={45} />
          <Tooltip {...TT}
            formatter={v => [`$${(v/1e3).toFixed(1)}B`, 'Total Reserves']}
            labelFormatter={fmtDate} />
          <Area type="monotone" dataKey="total_usd" stroke="#06B6D4" strokeWidth={2}
                fill="url(#fxAI)" dot={false} />
        </AreaChart>
      </ResponsiveContainer>
      <Legend color="#06B6D4" label="Total Reserves (USD)" />
    </>
  )

  if (topic === 'rbi') return (
    <>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis dataKey="date" tickFormatter={fmtDate} tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={35} domain={['auto', 'auto']} />
          <Tooltip {...TT} formatter={(v, n) => [`${fmt(v)}%`, n]} labelFormatter={fmtDate} />
          {data.some(d => d.repo_rate != null) && (
            <Line type="stepAfter" dataKey="repo_rate" stroke="#06B6D4" strokeWidth={2} dot={false} connectNulls name="Repo Rate" />
          )}
          {data.some(d => d.reverse_repo != null) && (
            <Line type="stepAfter" dataKey="reverse_repo" stroke="#22C55E" strokeWidth={1.8} dot={false} connectNulls name="Reverse Repo" />
          )}
          {data.some(d => d.crr != null) && (
            <Line type="stepAfter" dataKey="crr" stroke="#F59E0B" strokeWidth={1.5} dot={false} connectNulls name="CRR" strokeDasharray="4 2" />
          )}
        </LineChart>
      </ResponsiveContainer>
      <div className="flex gap-4 mt-2 ml-1">
        <Legend color="#06B6D4" label="Repo Rate" />
        <Legend color="#22C55E" label="Reverse Repo" />
        <Legend color="#F59E0B" label="CRR" dash />
      </div>
    </>
  )

  return null
}

// ── Content Studio ────────────────────────────────────────────
function ContentStudio() {
  const [topic,     setTopic]     = useState('gdp')
  const [question,  setQuestion]  = useState('')
  const [chartData, setChartData] = useState([])
  const [analysis,  setAnalysis]  = useState(null)
  const [loading,   setLoading]   = useState(false)
  const [chartLoad, setChartLoad] = useState(false)
  const [error,     setError]     = useState(null)

  useEffect(() => {
    setChartData([])
    setChartLoad(true)
    const loaders = {
      gdp:       () => api.gdp().then(r       => (r.data ?? []).filter(d => d.gdp_growth   != null).slice(-20)),
      inflation: () => api.inflation().then(r => (r.data ?? []).filter(d => d.cpi_yoy      != null).slice(-36)),
      trade:     () => api.trade().then(r     => (r.data ?? []).filter(d => d.balance_usd  != null).slice(-30)),
      forex:     () => api.forex().then(r     => (r.data ?? []).filter(d => d.total_usd    != null).slice(-78)),
      rbi:       () => api.rbiRates().then(r  => (r.data ?? []).filter(d => d.repo_rate    != null).slice(-60)),
    }
    loaders[topic]?.()
      .then(setChartData)
      .finally(() => setChartLoad(false))
  }, [topic])

  async function analyze() {
    setLoading(true); setError(null); setAnalysis(null)
    try {
      const res = await api.aiAnalyze(topic, question)
      setAnalysis(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const trendIcon = {
    rising:   <TrendingUp  size={14} className="text-green-400" />,
    falling:  <TrendingDown size={14} className="text-red-400" />,
    stable:   <Minus        size={14} className="text-yellow-400" />,
    volatile: <AlertCircle  size={14} className="text-orange-400" />,
  }

  const sentimentColor = {
    positive: 'text-green-400',
    negative: 'text-red-400',
    neutral:  'text-yellow-400',
  }

  const activeTopic = TOPICS.find(t => t.id === topic)

  return (
    <div className="grid grid-cols-1 xl:grid-cols-5 gap-5">

      {/* Left panel — controls + AI response */}
      <div className="xl:col-span-2 space-y-4">

        {/* Topic selector */}
        <div className="card p-4">
          <p className="text-muted text-xs uppercase tracking-wider mb-3">Select Topic</p>
          <div className="flex flex-col gap-1.5">
            {TOPICS.map(t => (
              <button key={t.id} onClick={() => { setTopic(t.id); setAnalysis(null); setError(null) }}
                      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all
                        ${topic === t.id
                          ? 'bg-white/[0.07] border border-white/[0.12]'
                          : 'hover:bg-white/[0.04] border border-transparent'
                        }`}>
                <span className="w-2 h-2 rounded-full flex-shrink-0"
                      style={{ background: t.color, boxShadow: topic === t.id ? `0 0 6px ${t.color}` : 'none' }} />
                <div>
                  <p className={`text-sm font-medium ${topic === t.id ? 'text-white' : 'text-muted'}`}>{t.label}</p>
                  <p className="text-muted text-xs">{t.sub}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Question input */}
        <div className="card p-4">
          <label className="text-muted text-xs uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Brain size={12} /> Ask Gemini
          </label>
          <textarea
            value={question}
            onChange={e => setQuestion(e.target.value)}
            rows={3}
            placeholder={`e.g. What does the latest ${activeTopic?.label} data tell us about the economy?`}
            className="w-full bg-bg border border-white/[0.07] rounded-lg px-3 py-2.5 text-sm
                       text-white placeholder-muted focus:outline-none focus:border-cyan/50
                       resize-none leading-relaxed mt-2"
          />
          {error && (
            <p className="text-red-400 text-xs mt-2 flex items-center gap-1.5">
              <AlertCircle size={11} /> {error}
            </p>
          )}
          <button onClick={analyze} disabled={loading}
                  className="w-full mt-3 btn-primary py-2.5 flex items-center justify-center gap-2
                             disabled:opacity-50 disabled:cursor-not-allowed text-sm">
            {loading
              ? <><RefreshCw size={13} className="animate-spin" /> Analysing…</>
              : <><Brain size={13} /> Analyse with Gemini</>
            }
          </button>
        </div>

        {/* AI Analysis result */}
        {analysis && (
          <div className="card p-4 space-y-3">
            <div className="flex items-center gap-2 mb-1">
              <Sparkles size={13} className="text-cyan" />
              <span className="text-cyan text-xs uppercase tracking-wider font-medium">AI Analysis</span>
              <span className="ml-auto flex items-center gap-1">
                {trendIcon[analysis.trend]}
                <span className="text-muted text-xs capitalize">{analysis.trend}</span>
              </span>
              <span className={`text-xs font-medium capitalize ${sentimentColor[analysis.sentiment]}`}>
                {analysis.sentiment}
              </span>
            </div>
            <p className="text-sm text-white/90 leading-relaxed">{analysis.summary}</p>
            {analysis.key_points?.length > 0 && (
              <ul className="space-y-1.5 mt-2">
                {analysis.key_points.map((pt, i) => (
                  <li key={i} className="flex gap-2 text-xs text-muted leading-relaxed">
                    <span className="text-cyan mt-0.5">▸</span>
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      {/* Right panel — chart */}
      <div className="xl:col-span-3">
        <ChartCard
          title={activeTopic?.label}
          subtitle={`${activeTopic?.sub} · Interactive chart`}
        >
          {chartLoad
            ? <div className="flex items-center justify-center h-[240px]">
                <div className="w-5 h-5 border-2 border-cyan border-t-transparent rounded-full animate-spin" />
              </div>
            : <TopicChart topic={topic} data={chartData} />
          }
        </ChartCard>

        {/* Quick-fire questions */}
        <div className="mt-4">
          <p className="text-muted text-xs uppercase tracking-wider mb-2">Quick Questions</p>
          <div className="flex flex-wrap gap-2">
            {[
              `What is the current ${activeTopic?.label} trend?`,
              `Is India's ${activeTopic?.label} data concerning?`,
              `Compare the latest vs historical ${activeTopic?.label}.`,
              `What risks does the ${activeTopic?.label} data highlight?`,
            ].map((q, i) => (
              <button key={i} onClick={() => setQuestion(q)}
                      className="text-xs px-3 py-1.5 rounded-full border border-white/[0.08]
                                 text-muted hover:text-white hover:border-white/20 transition-colors">
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Image Studio ──────────────────────────────────────────────
function ImageStudio() {
  const [model,   setModel]   = useState(MODELS[0].id)
  const [prompt,  setPrompt]  = useState('')
  const [imgB64,  setImgB64]  = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState(null)

  async function generate() {
    if (!prompt.trim()) { setError('Enter a prompt.'); return }
    setError(null); setLoading(true); setImgB64(null)
    try {
      const res = await api.aiImage(prompt, model)
      setImgB64(res.image_b64)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function download() {
    if (!imgB64) return
    const a = document.createElement('a')
    a.href = `data:image/png;base64,${imgB64}`
    a.download = 'EconomicPulse_DAwithRK.png'
    a.click()
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

      {/* Controls */}
      <div className="space-y-4">
        <div className="card p-4">
          <p className="text-muted text-xs uppercase tracking-wider mb-3">Model</p>
          <div className="flex gap-2 mt-1">
            {MODELS.map(m => (
              <button key={m.id} onClick={() => setModel(m.id)}
                      className={`text-xs px-3 py-1.5 rounded-lg border transition-colors
                        ${model === m.id
                          ? 'bg-cyan/10 border-cyan/40 text-cyan'
                          : 'border-white/[0.07] text-muted hover:text-white hover:border-white/20'
                        }`}>
                {m.label}
              </button>
            ))}
          </div>
        </div>

        <div className="card p-4">
          <p className="text-muted text-xs uppercase tracking-wider mb-2">Quick Prompts</p>
          <div className="flex flex-col gap-1.5 mt-2">
            {SUGGESTED_PROMPTS.map((s, i) => (
              <button key={i} onClick={() => setPrompt(s)}
                      className="text-left text-xs text-muted hover:text-white
                                 bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.05]
                                 rounded-lg px-3 py-2 transition-colors leading-relaxed">
                {s.slice(0, 80)}…
              </button>
            ))}
          </div>
        </div>

        <div className="card p-4">
          <label className="text-muted text-xs uppercase tracking-wider mb-2 block">Art Prompt</label>
          <textarea
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            rows={5}
            placeholder="Describe the economic visualization you want…"
            className="w-full bg-bg border border-white/[0.07] rounded-lg px-3 py-2.5 text-sm
                       text-white placeholder-muted focus:outline-none focus:border-cyan/50
                       resize-none leading-relaxed mt-2"
          />
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 text-red-400 text-xs rounded-lg px-4 py-3 flex gap-2">
            <AlertCircle size={12} className="mt-0.5 flex-shrink-0" /> {error}
          </div>
        )}

        <button onClick={generate} disabled={loading}
                className="w-full btn-primary py-3 flex items-center justify-center gap-2
                           disabled:opacity-50 disabled:cursor-not-allowed">
          {loading
            ? <><RefreshCw size={15} className="animate-spin" /> Generating…</>
            : <><ImageIcon size={15} /> Generate Image</>
          }
        </button>
      </div>

      {/* Preview */}
      <div className="card p-4 min-h-[500px] flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <span className="text-muted text-xs uppercase tracking-wider">Preview</span>
          {imgB64 && (
            <button onClick={download}
                    className="btn-ghost flex items-center gap-1.5 text-xs py-1.5">
              <Download size={13} /> Download PNG
            </button>
          )}
        </div>

        {loading && (
          <div className="flex-1 flex flex-col items-center justify-center gap-3">
            <div className="w-10 h-10 border-2 border-cyan border-t-transparent rounded-full animate-spin" />
            <p className="text-muted text-sm">Generating high-fidelity asset…</p>
          </div>
        )}

        {!loading && imgB64 && (
          <div className="flex-1 flex flex-col gap-3">
            <img src={`data:image/png;base64,${imgB64}`} alt="Generated"
                 className="w-full rounded-lg object-contain" />
            <p className="text-muted text-xs text-center">@rkjat65 · India Economic Pulse · rkjat.in</p>
          </div>
        )}

        {!loading && !imgB64 && (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center">
            <ImageIcon size={40} className="text-muted opacity-20" />
            <p className="text-muted text-sm">
              Enter a prompt and click Generate<br />
              <span className="text-xs opacity-60">Your image will appear here</span>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────
export default function AIStudio() {
  const [tab, setTab] = useState('content')

  return (
    <div className="p-6 max-w-[1400px]">
      <div className="page-header mb-4">
        <h1>AI Studio</h1>
        <p>Gemini-powered economic analysis · Imagen art generation</p>
      </div>

      {/* Tab switcher */}
      <div className="flex gap-1 mb-6 bg-white/[0.03] border border-white/[0.07] rounded-xl p-1 w-fit">
        <button onClick={() => setTab('content')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all
                  ${tab === 'content'
                    ? 'bg-cyan/10 text-cyan border border-cyan/20'
                    : 'text-muted hover:text-white'
                  }`}>
          <Brain size={14} /> Content Studio
        </button>
        <button onClick={() => setTab('image')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all
                  ${tab === 'image'
                    ? 'bg-cyan/10 text-cyan border border-cyan/20'
                    : 'text-muted hover:text-white'
                  }`}>
          <ImageIcon size={14} /> Image Studio
        </button>
      </div>

      {tab === 'content' ? <ContentStudio /> : <ImageStudio />}
    </div>
  )
}

// ── Helpers ───────────────────────────────────────────────────
function Legend({ color, label, dash }) {
  return (
    <div className="flex items-center gap-1.5 inline-flex mr-4 mt-2 ml-1">
      <svg width="16" height="8">
        <line x1="0" y1="4" x2="16" y2="4" stroke={color} strokeWidth={2}
              strokeDasharray={dash ? '4 2' : undefined} />
      </svg>
      <span className="text-muted text-xs">{label}</span>
    </div>
  )
}
