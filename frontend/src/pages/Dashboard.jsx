import { useEffect, useState } from 'react'
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { TrendingUp, TrendingDown, Flame, Globe2, Banknote, Percent } from 'lucide-react'
import MetricCard from '../components/MetricCard'
import ChartCard from '../components/ChartCard'
import { api, fmt, fmtB, fmtDate, filterByYear } from '../lib/api'

const TOOLTIP_STYLE = {
  contentStyle: { background: '#1E1E2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 },
  labelStyle: { color: '#94A3B8' },
}

export default function Dashboard() {
  const [overview, setOverview] = useState(null)
  const [gdpData,  setGdpData]  = useState([])
  const [infData,  setInfData]  = useState([])
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    Promise.all([api.overview(), api.gdp(), api.inflation()])
      .then(([ov, gdp, inf]) => {
        setOverview(ov)
        setGdpData(gdp.data ?? [])
        setInfData(inf.data ?? [])
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingScreen />

  const gdpPositive = overview?.gdp_growth >= 0
  const tradeDeficit = overview?.balance_usd < 0

  // last 20 quarters for mini GDP chart
  const gdpChart = gdpData.filter(d => d.gdp_growth != null).slice(-20)

  // last 48 months for inflation chart
  const infChart = infData.filter(d => d.cpi_yoy != null).slice(-48)

  return (
    <div className="p-6 max-w-[1400px]">
      {/* Header */}
      <div className="page-header mb-6">
        <h1>India Economic Pulse</h1>
        <p>Comprehensive macroeconomic intelligence — 2012 to 2025</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-3 mb-6">
        <MetricCard
          label="GDP Growth"
          value={`${fmt(overview?.gdp_growth)}%`}
          sub={overview?.gdp_label ?? 'Latest Quarter'}
          color={gdpPositive ? 'green' : 'red'}
          icon={gdpPositive ? TrendingUp : TrendingDown}
        />
        <MetricCard
          label="CPI Inflation"
          value={`${fmt(overview?.cpi_yoy)}%`}
          sub="YoY · RBI target 4%"
          color="amber"
          icon={Flame}
        />
        <MetricCard
          label="Trade Balance"
          value={fmtB(overview?.balance_usd)}
          sub={tradeDeficit ? 'Monthly deficit' : 'Monthly surplus'}
          color={tradeDeficit ? 'red' : 'green'}
          icon={Globe2}
        />
        <MetricCard
          label="Forex Reserves"
          value={fmtB(overview?.forex_usd)}
          sub={fmtDate(overview?.forex_date)}
          color="cyan"
          icon={Banknote}
        />
        <MetricCard
          label="Repo Rate"
          value={`${fmt(overview?.repo_rate)}%`}
          sub="RBI Policy Rate"
          color="purple"
          icon={Percent}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mb-4">
        <ChartCard
          title="GDP Growth Rate"
          subtitle="Quarterly % change · Last 20 quarters"
        >
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={gdpChart} barCategoryGap="30%">
              <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={35} />
              <Tooltip
                {...TOOLTIP_STYLE}
                formatter={(v) => [`${fmt(v)}%`, 'GDP Growth']}
                labelFormatter={d => fmtDate(d)}
              />
              <Bar dataKey="gdp_growth" radius={[3, 3, 0, 0]}>
                {gdpChart.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.gdp_growth >= 0 ? '#22C55E' : '#EF4444'}
                    fillOpacity={0.85}
                  />
                ))}
              </Bar>
              {/* Moving average line via custom rendering is complex in BarChart, skip for overview */}
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="CPI Inflation"
          subtitle="YoY % · Last 48 months"
        >
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={infChart}>
              <defs>
                <linearGradient id="cpiGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#06B6D4" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} width={35} />
              <Tooltip
                {...TOOLTIP_STYLE}
                formatter={(v, name) => [`${fmt(v)}%`, name === 'cpi_yoy' ? 'CPI' : 'WPI']}
                labelFormatter={d => fmtDate(d)}
              />
              {/* RBI target reference line */}
              <Line
                dataKey={() => 4}
                stroke="#F59E0B"
                strokeWidth={1}
                strokeDasharray="4 3"
                dot={false}
                name="RBI Target"
              />
              <Area
                type="monotone"
                dataKey="cpi_yoy"
                stroke="#06B6D4"
                strokeWidth={2}
                fill="url(#cpiGrad)"
                dot={false}
                name="cpi_yoy"
              />
              {infChart.some(d => d.wpi_yoy != null) && (
                <Line
                  type="monotone"
                  dataKey="wpi_yoy"
                  stroke="#8B5CF6"
                  strokeWidth={1.5}
                  dot={false}
                  name="wpi_yoy"
                  strokeDasharray="3 2"
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-2 ml-2">
            <Legend color="#06B6D4" label="CPI YoY" />
            <Legend color="#8B5CF6" label="WPI YoY" dash />
            <Legend color="#F59E0B" label="RBI Target 4%" dash />
          </div>
        </ChartCard>
      </div>

      {/* Bottom row — trade & forex */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <TradeBalanceCard />
        <ForexMiniCard />
      </div>

      {/* Footer */}
      <p className="text-muted text-xs text-center mt-8">
        Data: MoSPI · RBI · DGCI&S &nbsp;|&nbsp; Built by&nbsp;
        <a href="https://rkjat.in" target="_blank" rel="noreferrer" className="text-cyan hover:underline">
          RK Jat
        </a>
        &nbsp;·&nbsp; @rkjat65
      </p>
    </div>
  )
}

function Legend({ color, label, dash }) {
  return (
    <div className="flex items-center gap-1.5">
      <svg width="16" height="8">
        <line
          x1="0" y1="4" x2="16" y2="4"
          stroke={color} strokeWidth={2}
          strokeDasharray={dash ? '4 2' : undefined}
        />
      </svg>
      <span className="text-muted text-xs">{label}</span>
    </div>
  )
}

function TradeBalanceCard() {
  const [data, setData] = useState([])
  useEffect(() => {
    api.trade().then(r => setData((r.data ?? []).filter(d => d.balance_usd != null).slice(-24)))
  }, [])
  return (
    <ChartCard title="Trade Balance" subtitle="Monthly USD · Last 24 months">
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} barCategoryGap="25%">
          <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={v => `$${(v/1e3).toFixed(0)}B`} tick={{ fontSize: 10 }} width={40} />
          <Tooltip
            contentStyle={{ background: '#1E1E2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
            formatter={v => [`$${(v/1e3).toFixed(1)}B`, 'Balance']}
            labelFormatter={d => fmtDate(d)}
          />
          <Bar dataKey="balance_usd" radius={[2, 2, 0, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.balance_usd >= 0 ? '#22C55E' : '#EF4444'} fillOpacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}

function ForexMiniCard() {
  const [data, setData] = useState([])
  useEffect(() => {
    api.forex().then(r => setData((r.data ?? []).filter(d => d.total_usd != null).slice(-104)))
  }, [])
  return (
    <ChartCard title="Forex Reserves" subtitle="Total USD · Weekly">
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="fxGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#F59E0B" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis dataKey="date" tickFormatter={d => fmtDate(d)} tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={v => `$${(v/1e3).toFixed(0)}B`} tick={{ fontSize: 10 }} width={45} />
          <Tooltip
            contentStyle={{ background: '#1E1E2E', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
            formatter={v => [`$${(v/1e3).toFixed(1)}B`, 'Reserves']}
            labelFormatter={d => fmtDate(d)}
          />
          <Area type="monotone" dataKey="total_usd" stroke="#F59E0B" strokeWidth={2}
                fill="url(#fxGrad)" dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}

function LoadingScreen() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-cyan border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-muted text-sm">Loading economic data…</p>
      </div>
    </div>
  )
}
