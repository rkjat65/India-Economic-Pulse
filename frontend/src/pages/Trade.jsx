import { useEffect, useState } from 'react'
import {
  BarChart, Bar, AreaChart, Area, LineChart, Line, ComposedChart,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  ReferenceLine, Cell
} from 'recharts'
import ChartCard from '../components/ChartCard'
import MetricCard from '../components/MetricCard'
import { api, fmt, fmtB, fmtDate, filterByYear, yearRange } from '../lib/api'
import { Globe2, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownLeft } from 'lucide-react'

const TT = {
  contentStyle: { background: '#1E1E2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 },
  labelStyle: { color: '#94A3B8' },
}

export default function Trade() {
  const [raw,     setRaw]     = useState([])
  const [range,   setRange]   = useState([2012, 2025])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.trade().then(r => {
      const d = r.data ?? []
      setRaw(d)
      const [min, max] = yearRange(d)
      setRange([min, max])
    }).finally(() => setLoading(false))
  }, [])

  const data    = filterByYear(raw, 'date', range[0], range[1])
  const latest  = [...data].filter(d => d.balance_usd != null).slice(-1)[0]
  const deficitMonths = data.filter(d => d.balance_usd != null && d.balance_usd < 0).length
  const expGrowth = [...data].filter(d => d.exports_growth_yoy != null).slice(-1)[0]?.exports_growth_yoy
  const impGrowth = [...data].filter(d => d.imports_growth_yoy != null).slice(-1)[0]?.imports_growth_yoy

  if (loading) return <Spinner />

  const [minY, maxY] = yearRange(raw)
  const balData   = data.filter(d => d.balance_usd != null)
  const eiData    = data.filter(d => d.exports_usd != null && d.imports_usd != null)
  const growthData = data.filter(d => d.exports_growth_yoy != null || d.imports_growth_yoy != null)

  return (
    <div className="p-6 max-w-[1400px]">
      <div className="page-header mb-2">
        <h1>Trade Dynamics</h1>
        <p>Exports, imports and trade balance — monthly USD</p>
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
        <MetricCard label="Latest Exports" value={fmtB(latest?.exports_usd)}
          sub={fmtDate(latest?.date)} color="green" icon={ArrowUpRight} />
        <MetricCard label="Latest Imports" value={fmtB(latest?.imports_usd)}
          sub={fmtDate(latest?.date)} color="red" icon={ArrowDownLeft} />
        <MetricCard label="Trade Balance"
          value={fmtB(latest?.balance_usd)}
          sub={latest?.balance_usd < 0 ? 'Deficit' : 'Surplus'}
          color={latest?.balance_usd < 0 ? 'red' : 'green'} icon={Globe2} />
        <MetricCard label="Export Growth YoY" value={`${fmt(expGrowth)}%`}
          sub="Latest month" color={expGrowth >= 0 ? 'green' : 'red'}
          icon={expGrowth >= 0 ? TrendingUp : TrendingDown} />
      </div>

      {/* Trade balance bars */}
      <ChartCard title="Monthly Trade Balance"
                 subtitle="USD · red = deficit, green = surplus" className="mb-4">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={balData} barCategoryGap="20%">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
            <YAxis tickFormatter={v => `$${(v/1e3).toFixed(0)}B`} tick={{ fontSize: 10 }} width={42} />
            <Tooltip {...TT}
              formatter={v => [`$${(v/1e3).toFixed(2)}B`, 'Trade Balance']}
              labelFormatter={d => fmtDate(d)} />
            <ReferenceLine y={0} stroke="rgba(255,255,255,0.15)" />
            <Bar dataKey="balance_usd" radius={[2, 2, 0, 0]}>
              {balData.map((d, i) => (
                <Cell key={i} fill={d.balance_usd >= 0 ? '#22C55E' : '#EF4444'} fillOpacity={0.8} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Exports vs Imports area */}
      <ChartCard title="Exports vs Imports"
                 subtitle="Monthly USD — filled area shows volume" className="mb-4">
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={eiData}>
            <defs>
              <linearGradient id="expGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#22C55E" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#22C55E" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="impGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#EF4444" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
            <YAxis tickFormatter={v => `$${(v/1e3).toFixed(0)}B`} tick={{ fontSize: 10 }} width={42} />
            <Tooltip {...TT}
              formatter={(v, n) => [`$${(v/1e3).toFixed(2)}B`, n === 'exports_usd' ? 'Exports' : 'Imports']}
              labelFormatter={d => fmtDate(d)} />
            <Area type="monotone" dataKey="exports_usd" stroke="#22C55E" strokeWidth={2}
                  fill="url(#expGrad)" dot={false} name="exports_usd" />
            <Area type="monotone" dataKey="imports_usd" stroke="#EF4444" strokeWidth={2}
                  fill="url(#impGrad)" dot={false} name="imports_usd" />
          </AreaChart>
        </ResponsiveContainer>
        <div className="flex gap-4 mt-2 ml-1">
          <LegendLine color="#22C55E" label="Exports" />
          <LegendLine color="#EF4444" label="Imports" />
        </div>
      </ChartCard>

      {/* YoY Growth */}
      <ChartCard title="Trade Growth Rates (YoY %)"
                 subtitle="Month-over-same-month last year">
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={growthData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
            <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={38} />
            <Tooltip {...TT}
              formatter={(v, n) => [`${fmt(v)}%`, n === 'exports_growth_yoy' ? 'Export Growth' : 'Import Growth']}
              labelFormatter={d => fmtDate(d)} />
            <ReferenceLine y={0} stroke="rgba(255,255,255,0.15)" />
            <Line type="monotone" dataKey="exports_growth_yoy" stroke="#22C55E" strokeWidth={2} dot={false} connectNulls />
            <Line type="monotone" dataKey="imports_growth_yoy" stroke="#EF4444" strokeWidth={2} dot={false} connectNulls />
          </LineChart>
        </ResponsiveContainer>
        <div className="flex gap-4 mt-2 ml-1">
          <LegendLine color="#22C55E" label="Export Growth YoY" />
          <LegendLine color="#EF4444" label="Import Growth YoY" />
        </div>
      </ChartCard>
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
