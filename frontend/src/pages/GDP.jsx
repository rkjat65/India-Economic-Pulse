import { useEffect, useState } from 'react'
import {
  BarChart, Bar, LineChart, Line, ComposedChart,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  CartesianGrid, Legend as RLegend
} from 'recharts'
import ChartCard from '../components/ChartCard'
import MetricCard from '../components/MetricCard'
import { api, fmt, fmtDate, filterByYear, yearRange } from '../lib/api'
import { TrendingUp, TrendingDown, Activity, Minus } from 'lucide-react'

const TT = {
  contentStyle: { background: '#1E1E2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 },
  labelStyle: { color: '#94A3B8' },
}

const COMPONENTS = [
  { key: 'pfce',    label: 'Private Consumption', color: '#06B6D4' },
  { key: 'gfce',    label: 'Govt Consumption',    color: '#22C55E' },
  { key: 'gfcf',    label: 'Gross Fixed Capital',  color: '#F59E0B' },
  { key: 'exports', label: 'Exports',              color: '#8B5CF6' },
  { key: 'imports', label: 'Imports',              color: '#EF4444' },
]

export default function GDP() {
  const [raw,     setRaw]     = useState([])
  const [range,   setRange]   = useState([2012, 2025])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.gdp().then(r => {
      const d = r.data ?? []
      setRaw(d)
      setRange(yearRange(d))
    }).finally(() => setLoading(false))
  }, [])

  const data    = filterByYear(raw, 'date', range[0], range[1])
  const gdpRows = data.filter(d => d.gdp_growth != null)
  const latest  = gdpRows[gdpRows.length - 1]
  const avg     = gdpRows.length ? gdpRows.reduce((s, d) => s + d.gdp_growth, 0) / gdpRows.length : null
  const peak    = gdpRows.length ? Math.max(...gdpRows.map(d => d.gdp_growth)) : null
  const trough  = gdpRows.length ? Math.min(...gdpRows.map(d => d.gdp_growth)) : null

  if (loading) return <Spinner />

  const [minY, maxY] = yearRange(raw)

  return (
    <div className="p-6 max-w-[1400px]">
      <div className="page-header mb-2">
        <h1>GDP Analysis</h1>
        <p>Quarterly growth rates across India's economic sectors · 2012–2025</p>
      </div>

      {/* Year filter */}
      <div className="flex items-center gap-3 mb-6 flex-wrap">
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
        <MetricCard label="Latest Growth" value={`${fmt(latest?.gdp_growth)}%`}
          sub={latest ? `${latest.quarter} · ${latest.year}` : ''}
          color={latest?.gdp_growth >= 0 ? 'green' : 'red'} icon={TrendingUp} />
        <MetricCard label="Period Average" value={`${fmt(avg)}%`}
          sub={`${range[0]} – ${range[1]}`} color="cyan" icon={Activity} />
        <MetricCard label="Peak Growth" value={`${fmt(peak)}%`}
          sub="Best quarter" color="green" icon={TrendingUp} />
        <MetricCard label="Trough Growth" value={`${fmt(trough)}%`}
          sub="Worst quarter" color="red" icon={TrendingDown} />
      </div>

      {/* Main bar chart */}
      <ChartCard title="GDP Growth Rate" subtitle="Quarterly % · green = positive, red = negative" className="mb-4">
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={gdpRows} barCategoryGap="25%">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
            <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={38} />
            <Tooltip {...TT} formatter={(v, n) => [`${fmt(v)}%`, n === 'gdp_growth' ? 'GDP Growth' : '4Q Avg']}
                     labelFormatter={d => fmtDate(d)} />
            <Bar dataKey="gdp_growth" radius={[3, 3, 0, 0]} name="gdp_growth">
              {gdpRows.map((d, i) => (
                <Cell key={i} fill={d.gdp_growth >= 0 ? '#22C55E' : '#EF4444'} fillOpacity={0.85} />
              ))}
            </Bar>
            <Line type="monotone" dataKey="gdp_ma4" stroke="#F59E0B" strokeWidth={2}
                  dot={false} strokeDasharray="5 3" name="gdp_ma4" />
          </ComposedChart>
        </ResponsiveContainer>
        <div className="flex gap-4 mt-1 ml-1">
          <LegendDot color="#22C55E" label="Positive growth" />
          <LegendDot color="#EF4444" label="Negative growth" />
          <LegendLine color="#F59E0B" label="4Q Moving Avg" />
        </div>
      </ChartCard>

      {/* Components chart */}
      <ChartCard title="GDP Component Growth Rates"
                 subtitle="Private Consumption · Govt Spending · Capital Formation · Trade"
                 className="mb-4">
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data.filter(d => COMPONENTS.some(c => d[c.key] != null))}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
            <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={38} />
            <Tooltip {...TT} formatter={(v, n) => [`${fmt(v)}%`, COMPONENTS.find(c => c.key === n)?.label ?? n]}
                     labelFormatter={d => fmtDate(d)} />
            {COMPONENTS.map(c => (
              <Line key={c.key} type="monotone" dataKey={c.key}
                    stroke={c.color} strokeWidth={1.8} dot={false} name={c.key} connectNulls />
            ))}
          </LineChart>
        </ResponsiveContainer>
        <div className="flex flex-wrap gap-4 mt-2 ml-1">
          {COMPONENTS.map(c => <LegendLine key={c.key} color={c.color} label={c.label} />)}
        </div>
      </ChartCard>

      {/* Heatmap table */}
      <ChartCard title="GDP Growth Heatmap" subtitle="Year × Quarter">
        <HeatmapTable data={gdpRows} />
      </ChartCard>
    </div>
  )
}

function HeatmapTable({ data }) {
  const years = [...new Set(data.map(d => d.year))].sort()
  const quarters = ['Q1', 'Q2', 'Q3', 'Q4']

  function lookup(year, q) {
    return data.find(d => d.year === year && d.quarter === q)?.gdp_growth ?? null
  }

  function heatColor(v) {
    if (v == null) return 'rgba(255,255,255,0.03)'
    if (v >= 8)  return 'rgba(34,197,94,0.55)'
    if (v >= 5)  return 'rgba(34,197,94,0.30)'
    if (v >= 2)  return 'rgba(34,197,94,0.15)'
    if (v >= 0)  return 'rgba(34,197,94,0.07)'
    if (v >= -5) return 'rgba(239,68,68,0.25)'
    return 'rgba(239,68,68,0.50)'
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr>
            <th className="text-left text-muted font-medium py-2 pr-4 pl-1">Year</th>
            {quarters.map(q => (
              <th key={q} className="text-center text-muted font-medium py-2 px-4">{q}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {years.map(yr => (
            <tr key={yr} className="border-t border-white/[0.04]">
              <td className="text-muted py-2 pr-4 pl-1 font-mono">{yr}</td>
              {quarters.map(q => {
                const v = lookup(yr, q)
                return (
                  <td key={q} className="text-center py-2 px-4">
                    <span className="inline-block px-3 py-1 rounded text-white font-mono"
                          style={{ background: heatColor(v), minWidth: 52 }}>
                      {v != null ? `${fmt(v)}%` : '—'}
                    </span>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const LegendDot = ({ color, label }) => (
  <div className="flex items-center gap-1.5">
    <span className="w-2.5 h-2.5 rounded-sm inline-block" style={{ background: color }} />
    <span className="text-muted text-xs">{label}</span>
  </div>
)

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
