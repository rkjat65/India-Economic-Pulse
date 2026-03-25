import { useEffect, useState } from 'react'
import {
  AreaChart, Area, LineChart, Line, ComposedChart,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine
} from 'recharts'
import ChartCard from '../components/ChartCard'
import MetricCard from '../components/MetricCard'
import { api, fmt, fmtDate, filterByYear, yearRange } from '../lib/api'
import { Flame, TrendingDown, Minus } from 'lucide-react'

const TT = {
  contentStyle: { background: '#1E1E2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 },
  labelStyle: { color: '#94A3B8' },
}

export default function Inflation() {
  const [raw,     setRaw]     = useState([])
  const [range,   setRange]   = useState([2014, 2025])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.inflation().then(r => {
      const d = r.data ?? []
      setRaw(d)
      const [min, max] = yearRange(d)
      setRange([min, max])
    }).finally(() => setLoading(false))
  }, [])

  const data    = filterByYear(raw, 'date', range[0], range[1])
  const cpiRows = data.filter(d => d.cpi_yoy != null)
  const latest  = cpiRows[cpiRows.length - 1]
  const avg     = cpiRows.length ? cpiRows.reduce((s, d) => s + d.cpi_yoy, 0) / cpiRows.length : null
  const aboveTarget = cpiRows.filter(d => d.cpi_yoy > 6).length
  const pct = cpiRows.length ? Math.round((aboveTarget / cpiRows.length) * 100) : 0

  if (loading) return <Spinner />

  const [minY, maxY] = yearRange(raw)

  return (
    <div className="p-6 max-w-[1400px]">
      <div className="page-header mb-2">
        <h1>Inflation Tracker</h1>
        <p>Consumer & wholesale price indices — YoY % change</p>
      </div>

      {/* Year filter */}
      <div className="flex items-center gap-3 mb-6">
        <span className="text-muted text-xs uppercase tracking-wider">Year Range</span>
        <select className="filter-select" value={range[0]}
                onChange={e => setRange([+e.target.value, range[1]])}>
          {Array.from({ length: maxY - minY + 1 }, (_, i) => minY + i).map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
        <span className="text-muted text-xs">to</span>
        <select className="filter-select" value={range[1]}
                onChange={e => setRange([range[0], +e.target.value])}>
          {Array.from({ length: maxY - minY + 1 }, (_, i) => minY + i).map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <MetricCard label="Latest CPI" value={`${fmt(latest?.cpi_yoy)}%`}
          sub={fmtDate(latest?.date)} color="amber" icon={Flame} />
        <MetricCard label="Latest WPI" value={`${fmt(latest?.wpi_yoy)}%`}
          sub={fmtDate(latest?.date)} color="purple" icon={Flame} />
        <MetricCard label="Period Avg CPI" value={`${fmt(avg)}%`}
          sub={`${range[0]}–${range[1]}`} color="cyan" icon={Minus} />
        <MetricCard label="Above 6% Tolerance" value={`${pct}%`}
          sub={`${aboveTarget} of ${cpiRows.length} months`}
          color={pct > 30 ? 'red' : 'green'} icon={pct > 30 ? Flame : TrendingDown} />
      </div>

      {/* CPI vs WPI */}
      <ChartCard title="CPI vs WPI Inflation" subtitle="YoY % · RBI upper tolerance 6%"
                 className="mb-4">
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={cpiRows}>
            <defs>
              <linearGradient id="cpiGrad2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#06B6D4" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
            <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={38} />
            <Tooltip {...TT} formatter={(v, n) => [`${fmt(v)}%`, n === 'cpi_yoy' ? 'CPI' : 'WPI']}
                     labelFormatter={d => fmtDate(d)} />
            <ReferenceLine y={4} stroke="#F59E0B" strokeDasharray="5 3" strokeWidth={1.5}
                           label={{ value: 'RBI Target 4%', fill: '#F59E0B', fontSize: 10, position: 'insideTopRight' }} />
            <ReferenceLine y={6} stroke="#EF4444" strokeDasharray="5 3" strokeWidth={1.5}
                           label={{ value: 'Tolerance 6%', fill: '#EF4444', fontSize: 10, position: 'insideTopRight' }} />
            <Area type="monotone" dataKey="cpi_yoy" stroke="#06B6D4" strokeWidth={2.5}
                  fill="url(#cpiGrad2)" dot={false} name="cpi_yoy" />
            <Line type="monotone" dataKey="wpi_yoy" stroke="#8B5CF6" strokeWidth={2}
                  dot={false} strokeDasharray="4 2" name="wpi_yoy" connectNulls />
          </ComposedChart>
        </ResponsiveContainer>
        <div className="flex gap-4 mt-2 ml-1">
          <LegendLine color="#06B6D4" label="CPI YoY" />
          <LegendLine color="#8B5CF6" label="WPI YoY" dash />
          <LegendLine color="#F59E0B" label="RBI Target 4%" dash />
          <LegendLine color="#EF4444" label="Upper Tolerance 6%" dash />
        </div>
      </ChartCard>

      {/* Rural vs Urban */}
      {data.some(d => d.cpi_rural_yoy != null) && (
        <ChartCard title="Rural vs Urban CPI" subtitle="Divergence between India's two economic segments">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={data.filter(d => d.cpi_rural_yoy != null || d.cpi_urban_yoy != null)}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={38} />
              <Tooltip {...TT} formatter={(v, n) => [`${fmt(v)}%`, n === 'cpi_rural_yoy' ? 'Rural CPI' : 'Urban CPI']}
                       labelFormatter={d => fmtDate(d)} />
              <ReferenceLine y={4} stroke="#F59E0B" strokeDasharray="4 3" strokeWidth={1} />
              <Line type="monotone" dataKey="cpi_rural_yoy" stroke="#22C55E" strokeWidth={2}
                    dot={false} name="cpi_rural_yoy" connectNulls />
              <Line type="monotone" dataKey="cpi_urban_yoy" stroke="#F59E0B" strokeWidth={2}
                    dot={false} name="cpi_urban_yoy" connectNulls />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-2 ml-1">
            <LegendLine color="#22C55E" label="Rural CPI" />
            <LegendLine color="#F59E0B" label="Urban CPI" />
          </div>
        </ChartCard>
      )}
    </div>
  )
}

const LegendLine = ({ color, label, dash }) => (
  <div className="flex items-center gap-1.5">
    <svg width="16" height="8">
      <line x1="0" y1="4" x2="16" y2="4" stroke={color} strokeWidth={2}
            strokeDasharray={dash ? '4 2' : undefined} />
    </svg>
    <span className="text-muted text-xs">{label}</span>
  </div>
)

const Spinner = () => (
  <div className="flex items-center justify-center h-full">
    <div className="w-6 h-6 border-2 border-cyan border-t-transparent rounded-full animate-spin" />
  </div>
)
