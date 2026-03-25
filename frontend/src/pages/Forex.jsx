import { useEffect, useState } from 'react'
import {
  AreaChart, Area, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell as PieCell
} from 'recharts'
import ChartCard from '../components/ChartCard'
import MetricCard from '../components/MetricCard'
import { api, fmt, fmtB, fmtDate, filterByYear, yearRange } from '../lib/api'
import { Banknote, Percent, Shield, TrendingUp } from 'lucide-react'

const TT = {
  contentStyle: { background: '#1E1E2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 },
  labelStyle: { color: '#94A3B8' },
}

const RATE_COLORS = {
  repo_rate:    '#06B6D4',
  reverse_repo: '#22C55E',
  bank_rate:    '#F59E0B',
  sdf_rate:     '#8B5CF6',
  msf_rate:     '#EF4444',
}

const PIE_COLORS = ['#06B6D4', '#F59E0B', '#8B5CF6', '#22C55E']

export default function Forex() {
  const [forex,   setForex]   = useState([])
  const [rbi,     setRbi]     = useState([])
  const [fxRange, setFxRange] = useState([2012, 2025])
  const [rbRange, setRbRange] = useState([2012, 2025])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.forex(), api.rbiRates()]).then(([f, r]) => {
      const fd = f.data ?? []; const rd = r.data ?? []
      setForex(fd); setRbi(rd)
      setFxRange(yearRange(fd)); setRbRange(yearRange(rd))
    }).finally(() => setLoading(false))
  }, [])

  const fxData  = filterByYear(forex, 'date', fxRange[0], fxRange[1]).filter(d => d.total_usd != null)
  const rbiData = filterByYear(rbi,   'date', rbRange[0], rbRange[1])

  const latestFx  = fxData[fxData.length - 1]
  const latestRbi = [...rbiData].filter(d => d.repo_rate != null).slice(-1)[0]

  // Composition pie data
  const pieData = latestFx ? [
    { name: 'FCA',  value: latestFx.fca_usd  ?? 0 },
    { name: 'Gold', value: latestFx.gold_usd ?? 0 },
    { name: 'SDR',  value: latestFx.sdr_usd  ?? 0 },
    { name: 'IMF',  value: latestFx.imf_usd  ?? 0 },
  ].filter(d => d.value > 0) : []

  const [fxMinY, fxMaxY] = yearRange(forex)
  const [rbMinY, rbMaxY] = yearRange(rbi)

  if (loading) return <Spinner />

  return (
    <div className="p-6 max-w-[1400px]">
      <div className="page-header mb-2">
        <h1>Forex & Rates</h1>
        <p>Foreign exchange reserves · RBI monetary policy rates</p>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <MetricCard label="Total Reserves" value={fmtB(latestFx?.total_usd)}
          sub={fmtDate(latestFx?.date)} color="amber" icon={Banknote} />
        <MetricCard label="Gold Reserves" value={fmtB(latestFx?.gold_usd)}
          sub={`${fmt(latestFx?.gold_pct)}% of total`} color="amber" icon={Shield} />
        <MetricCard label="Repo Rate" value={`${fmt(latestRbi?.repo_rate)}%`}
          sub="RBI Policy Rate" color="cyan" icon={Percent} />
        <MetricCard label="Reverse Repo" value={`${fmt(latestRbi?.reverse_repo)}%`}
          sub="RBI Absorption Rate" color="purple" icon={TrendingUp} />
      </div>

      {/* Forex chart + pie */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 mb-4">
        <div className="xl:col-span-2">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-muted text-xs uppercase tracking-wider">Year Range</span>
            <select className="filter-select" value={fxRange[0]}
                    onChange={e => setFxRange([+e.target.value, fxRange[1]])}>
              {Array.from({ length: fxMaxY - fxMinY + 1 }, (_, i) => fxMinY + i).map(y => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
            <span className="text-muted text-xs">to</span>
            <select className="filter-select" value={fxRange[1]}
                    onChange={e => setFxRange([fxRange[0], +e.target.value])}>
              {Array.from({ length: fxMaxY - fxMinY + 1 }, (_, i) => fxMinY + i).map(y => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>
          <ChartCard title="Forex Reserves" subtitle="Total · Gold · FCA (USD Billion)">
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={fxData}>
                <defs>
                  <linearGradient id="fxTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#F59E0B" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="fxGold" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#22C55E" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#22C55E" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
                <YAxis tickFormatter={v => `$${(v/1e3).toFixed(0)}B`} tick={{ fontSize: 10 }} width={45} />
                <Tooltip {...TT}
                  formatter={(v, n) => [`$${(v/1e3).toFixed(1)}B`, { total_usd: 'Total', fca_usd: 'FCA', gold_usd: 'Gold' }[n] ?? n]}
                  labelFormatter={d => fmtDate(d)} />
                <Area type="monotone" dataKey="total_usd" stroke="#F59E0B" strokeWidth={2.5}
                      fill="url(#fxTotal)" dot={false} name="total_usd" />
                {fxData.some(d => d.gold_usd) && (
                  <Area type="monotone" dataKey="gold_usd" stroke="#22C55E" strokeWidth={1.8}
                        fill="url(#fxGold)" dot={false} name="gold_usd" />
                )}
              </AreaChart>
            </ResponsiveContainer>
            <div className="flex gap-4 mt-2 ml-1">
              <LegendLine color="#F59E0B" label="Total Reserves" />
              <LegendLine color="#22C55E" label="Gold" />
            </div>
          </ChartCard>
        </div>

        {/* Pie chart */}
        <ChartCard title="Reserve Composition" subtitle="Latest breakdown">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name"
                   cx="50%" cy="50%" innerRadius={55} outerRadius={80}
                   paddingAngle={3}>
                {pieData.map((_, i) => (
                  <PieCell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#1E1E2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                formatter={v => [`$${(v/1e3).toFixed(1)}B`]} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 justify-center">
            {pieData.map((d, i) => (
              <div key={d.name} className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ background: PIE_COLORS[i] }} />
                <span className="text-muted text-xs">{d.name}</span>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>

      {/* RBI Rates */}
      <div className="flex items-center gap-3 mb-3">
        <span className="text-muted text-xs uppercase tracking-wider">Year Range</span>
        <select className="filter-select" value={rbRange[0]}
                onChange={e => setRbRange([+e.target.value, rbRange[1]])}>
          {Array.from({ length: rbMaxY - rbMinY + 1 }, (_, i) => rbMinY + i).map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
        <span className="text-muted text-xs">to</span>
        <select className="filter-select" value={rbRange[1]}
                onChange={e => setRbRange([rbRange[0], +e.target.value])}>
          {Array.from({ length: rbMaxY - rbMinY + 1 }, (_, i) => rbMinY + i).map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <ChartCard title="RBI Policy Rates" subtitle="Repo · Reverse Repo · Bank Rate · SDF">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={rbiData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={35} domain={['auto', 'auto']} />
              <Tooltip {...TT} formatter={(v, n) => [`${fmt(v)}%`, n]} labelFormatter={d => fmtDate(d)} />
              {Object.entries(RATE_COLORS).slice(0, 4).map(([key, color]) =>
                rbiData.some(d => d[key] != null) && (
                  <Line key={key} type="stepAfter" dataKey={key} stroke={color}
                        strokeWidth={2} dot={false} name={key} connectNulls />
                )
              )}
            </LineChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-3 mt-2 ml-1">
            {Object.entries(RATE_COLORS).slice(0, 4).map(([k, c]) => (
              <LegendLine key={k} color={c} label={k.replace('_', ' ')} />
            ))}
          </div>
        </ChartCard>

        <ChartCard title="CRR & SLR" subtitle="Reserve requirements (%)">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={rbiData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={35} domain={['auto', 'auto']} />
              <Tooltip {...TT} formatter={(v, n) => [`${fmt(v)}%`, n.toUpperCase()]} labelFormatter={d => fmtDate(d)} />
              {rbiData.some(d => d.crr != null) && (
                <Line type="stepAfter" dataKey="crr" stroke="#06B6D4" strokeWidth={2} dot={false} name="crr" connectNulls />
              )}
              {rbiData.some(d => d.slr != null) && (
                <Line type="stepAfter" dataKey="slr" stroke="#F59E0B" strokeWidth={2} dot={false} name="slr" connectNulls />
              )}
            </LineChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-2 ml-1">
            <LegendLine color="#06B6D4" label="CRR" />
            <LegendLine color="#F59E0B" label="SLR" />
          </div>
        </ChartCard>
      </div>
    </div>
  )
}

const LegendLine = ({ color, label }) => (
  <div className="flex items-center gap-1.5">
    <svg width="16" height="8">
      <line x1="0" y1="4" x2="16" y2="4" stroke={color} strokeWidth={2} />
    </svg>
    <span className="text-muted text-xs">{label}</span>
  </div>
)

const Spinner = () => (
  <div className="flex items-center justify-center h-full">
    <div className="w-6 h-6 border-2 border-cyan border-t-transparent rounded-full animate-spin" />
  </div>
)
