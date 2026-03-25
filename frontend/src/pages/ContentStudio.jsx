import { useState, useEffect, useRef } from 'react'
import {
  AreaChart, Area, BarChart, Bar,
  LineChart, Line, ComposedChart,
  XAxis, YAxis, ReferenceLine, Cell, Tooltip, CartesianGrid,
} from 'recharts'
import {
  Download, Copy, Sparkles, Check, RefreshCw, X,
  Star, Layout, GitMerge, TrendingUp, List, Calendar, Zap,
} from 'lucide-react'
import { api, fmt, fmtDate } from '../lib/api'

// ── Constants ─────────────────────────────────────────────────

const TEMPLATES = [
  { id: 'snapshot',   label: 'Indicator Snapshot', icon: Star },
  { id: 'summary',    label: 'India Summary',       icon: Layout },
  { id: 'comparison', label: 'Year Comparison',     icon: GitMerge },
  { id: 'trend',      label: 'Trend Chart',         icon: TrendingUp },
  { id: 'ranking',    label: 'Top Rankings',        icon: List },
  { id: 'recap',      label: 'Year Recap',          icon: Calendar },
  { id: 'dual',       label: 'Dual Indicator',      icon: Zap },
]

const FORMATS = [
  { id: 'twitter',   label: 'Twitter',   w: 800, h: 418 },
  { id: 'instagram', label: 'Instagram', w: 800, h: 800 },
  { id: 'linkedin',  label: 'LinkedIn',  w: 800, h: 418 },
  { id: 'portrait',  label: 'Stories',   w: 450, h: 800 },
]

const IND_OPTIONS = [
  { id: 'gdp',   label: 'GDP Growth',     unit: '%',  color: '#22C55E', source: 'MoSPI'  },
  { id: 'cpi',   label: 'CPI Inflation',  unit: '%',  color: '#F59E0B', source: 'MoSPI'  },
  { id: 'wpi',   label: 'WPI Inflation',  unit: '%',  color: '#8B5CF6', source: 'MoSPI'  },
  { id: 'trade', label: 'Trade Balance',  unit: 'B$', color: '#EF4444', source: 'DGCI&S' },
  { id: 'forex', label: 'Forex Reserves', unit: 'B$', color: '#06B6D4', source: 'RBI'    },
  { id: 'repo',  label: 'Repo Rate',      unit: '%',  color: '#7C3AED', source: 'RBI'    },
]

function getDisplayDims(fmtId) {
  const f = FORMATS.find(x => x.id === fmtId) ?? FORMATS[0]
  const scale = Math.min(540 / f.w, 500 / f.h)
  return { displayW: Math.round(f.w * scale), displayH: Math.round(f.h * scale), scale, exportW: f.w, exportH: f.h }
}

function vfmt(n, unit) {
  if (n == null) return '—'
  const v = Number(n)
  if (unit === 'B$') return `${v < 0 ? '-' : ''}$${Math.abs(v).toFixed(1)}B`
  return `${v.toFixed(2)}${unit}`
}

function changeFmt(curr, prev) {
  if (curr == null || prev == null) return null
  const d = curr - prev
  return { d, pos: d >= 0, label: `${d >= 0 ? '+' : ''}${d.toFixed(2)}` }
}

function periodStr(p) {
  if (!p) return '—'
  if (typeof p === 'string' && (p.includes('T') || /^\d{4}-\d{2}-\d{2}/.test(p))) return fmtDate(p)
  return p
}

// ── Shared card primitives (inline styles — html2canvas safe) ─

const FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

function CardShell({ w, h, accent = '#06B6D4', children }) {
  return (
    <div style={{
      width: w, height: h, background: '#0A0A0F',
      fontFamily: FONT, display: 'flex', flexDirection: 'column',
      padding: '30px 34px 22px', position: 'relative',
      overflow: 'hidden', boxSizing: 'border-box',
    }}>
      <div style={{
        position: 'absolute', top: -100, right: -100, width: 320, height: 320,
        borderRadius: '50%',
        background: `radial-gradient(circle, ${accent}1A 0%, transparent 70%)`,
        pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute', bottom: -60, left: -60, width: 200, height: 200,
        borderRadius: '50%',
        background: `radial-gradient(circle, ${accent}0D 0%, transparent 70%)`,
        pointerEvents: 'none',
      }} />
      {children}
    </div>
  )
}

function CardTop({ tag, tagColor = '#06B6D4' }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 22 }}>
      <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.2em', color: '#334155', textTransform: 'uppercase' }}>
        INDIA ECONOMIC PULSE
      </div>
      {tag && (
        <div style={{
          background: tagColor + '1F', border: `1px solid ${tagColor}40`,
          borderRadius: 6, padding: '3px 10px',
          fontSize: 9, color: tagColor, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase',
        }}>
          {tag}
        </div>
      )}
    </div>
  )
}

function CardFoot({ source }) {
  return (
    <div style={{
      borderTop: '1px solid rgba(255,255,255,0.07)', paddingTop: 11, marginTop: 'auto',
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    }}>
      <div style={{ fontSize: 9, color: '#475569', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase' }}>
        {source ? `Source: ${source}` : 'India Economic Pulse'}
      </div>
      <div style={{ fontSize: 9, color: '#64748B', letterSpacing: '0.06em', fontWeight: 500 }}>
        @rkjat65 · rkjat.in
      </div>
    </div>
  )
}

// ── Recharts chart helpers (explicit px dims — html2canvas-safe) ─

// Tick style helper (inline, not Tailwind — works inside html2canvas)
const tickStyle = { fill: '#475569', fontSize: 9, fontFamily: FONT }

function MiniAreaChart({ data, color, width, height, unit, showAxes = true }) {
  const gradId = `mg_${color.replace('#', '')}_${width}`
  const yFmt = v => unit === 'B$' ? `$${Math.abs(v).toFixed(0)}B` : `${v.toFixed(1)}${unit}`
  return (
    <AreaChart width={width} height={height} data={data}
               margin={{ top: 4, right: 6, left: showAxes ? -8 : -30, bottom: 0 }}>
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="5%"  stopColor={color} stopOpacity={0.4} />
          <stop offset="95%" stopColor={color} stopOpacity={0.02} />
        </linearGradient>
      </defs>
      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
      {showAxes && (
        <XAxis dataKey="date" tickFormatter={v => new Date(v).getFullYear()}
               tick={tickStyle} axisLine={false} tickLine={false}
               interval="preserveStartEnd" />
      )}
      <YAxis tick={showAxes ? tickStyle : { fill: 'transparent', fontSize: 1 }}
             axisLine={false} tickLine={false}
             width={showAxes ? 38 : 10}
             tickFormatter={yFmt} />
      <ReferenceLine y={0} stroke="rgba(255,255,255,0.1)" />
      <Area type="monotone" dataKey="value" stroke={color} strokeWidth={2.5}
            fill={`url(#${gradId})`} dot={false} isAnimationActive={false} />
    </AreaChart>
  )
}

function MiniBarChart({ data, valueKey, color, width, height }) {
  const maxVal = data.length ? Math.max(...data.map(r => Math.abs(r[valueKey] ?? 0))) : 1
  return (
    <BarChart width={width} height={height} data={data}
              layout="vertical"
              margin={{ top: 0, right: 58, left: 4, bottom: 0 }}>
      <XAxis type="number" hide domain={[0, maxVal * 1.05]} />
      <YAxis type="category" dataKey="label"
             tick={tickStyle} axisLine={false} tickLine={false}
             width={64} />
      <Bar dataKey={valueKey} radius={[0, 4, 4, 0]} isAnimationActive={false}
           label={{ position: 'right', fontSize: 10, fill: '#E2E8F0',
                    fontFamily: FONT, fontWeight: 700,
                    formatter: v => v != null ? Number(v).toFixed(2) : '' }}>
        {data.map((_, i) => (
          <Cell key={i} fill={i === 0 ? '#F59E0B' : color}
                fillOpacity={Math.max(0.55, 1 - i * 0.055)} />
        ))}
      </Bar>
    </BarChart>
  )
}

// ── Template 1: Indicator Snapshot ────────────────────────────

function SnapshotCard({ snapshot, config, w, h }) {
  const portrait = h > w
  const ind = IND_OPTIONS.find(i => i.id === config.indicatorId) ?? IND_OPTIONS[0]
  const d = snapshot?.[ind.id]
  const ch = d ? changeFmt(d.value, d.prev) : null

  return (
    <CardShell w={w} h={h} accent={ind.color}>
      <CardTop tag={ind.id.toUpperCase()} tagColor={ind.color} />
      <div style={{ fontSize: portrait ? 16 : 13, color: '#94A3B8', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 14 }}>
        {d?.label ?? ind.label}
      </div>
      <div style={{ display: 'flex', gap: 16, marginBottom: 18, flex: portrait ? 1 : 0, alignItems: portrait ? 'center' : 'flex-end' }}>
        <div style={{ fontSize: portrait ? 88 : 72, fontWeight: 900, color: '#FFFFFF', lineHeight: 1, letterSpacing: '-0.03em' }}>
          {d?.value != null ? vfmt(d.value, ind.unit) : '—'}
        </div>
        {ch && (
          <div style={{ fontSize: portrait ? 20 : 16, fontWeight: 700, color: ch.pos ? '#22C55E' : '#EF4444', paddingBottom: portrait ? 0 : 8 }}>
            {ch.pos ? '▲' : '▼'} {ch.label}{ind.unit === 'B$' ? 'B' : ind.unit === '%' ? 'pp' : ''}
          </div>
        )}
      </div>
      <div style={{ fontSize: 12, color: '#64748B', marginBottom: 4 }}>Period: {periodStr(d?.period)}</div>
      {d?.prev != null && <div style={{ fontSize: 11, color: '#475569' }}>Previous: {vfmt(d.prev, ind.unit)}</div>}
      <div style={{ height: 3, width: 44, background: ind.color, borderRadius: 2, marginTop: 18, marginBottom: 6, opacity: 0.85 }} />
      <CardFoot source={d?.source ?? ind.source} />
    </CardShell>
  )
}

// ── Template 2: India Summary (stat grid + change indicators) ──

function SummaryCard({ snapshot, w, h }) {
  const portrait = h > w
  const stats = [
    { id: 'gdp',   label: 'GDP Growth',     color: '#22C55E' },
    { id: 'cpi',   label: 'CPI Inflation',  color: '#F59E0B' },
    { id: 'wpi',   label: 'WPI Inflation',  color: '#8B5CF6' },
    { id: 'trade', label: 'Trade Balance',  color: '#EF4444' },
    { id: 'forex', label: 'Forex Reserves', color: '#06B6D4' },
    { id: 'repo',  label: 'Repo Rate',      color: '#7C3AED' },
  ]
  const cols = portrait ? 2 : 3
  return (
    <CardShell w={w} h={h} accent="#06B6D4">
      <CardTop />
      <div style={{ fontSize: portrait ? 21 : 18, fontWeight: 800, color: '#FFF', marginBottom: 2, letterSpacing: '-0.01em' }}>
        India Economic Snapshot
      </div>
      <div style={{ fontSize: 10, color: '#475569', marginBottom: portrait ? 20 : 14, letterSpacing: '0.04em' }}>
        {periodStr(snapshot?.gdp?.period ?? snapshot?.cpi?.period)}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: portrait ? 11 : 9, flex: 1 }}>
        {stats.map(s => {
          const d = snapshot?.[s.id]
          const ind = IND_OPTIONS.find(i => i.id === s.id)
          const val = d?.value != null ? vfmt(d.value, ind?.unit ?? '%') : '—'
          const ch  = d ? changeFmt(d.value, d.prev) : null
          return (
            <div key={s.id} style={{
              background: s.color + '10', border: `1px solid ${s.color}25`,
              borderRadius: 10, padding: portrait ? '13px 12px' : '10px 11px',
              display: 'flex', flexDirection: 'column', gap: 3,
              position: 'relative', overflow: 'hidden',
            }}>
              {/* Subtle corner glow */}
              <div style={{ position: 'absolute', top: -20, right: -20, width: 60, height: 60,
                            borderRadius: '50%', background: s.color + '18', pointerEvents: 'none' }} />
              <div style={{ fontSize: 7.5, color: s.color, fontWeight: 700, letterSpacing: '0.12em',
                            textTransform: 'uppercase' }}>{s.label}</div>
              <div style={{ fontSize: portrait ? 26 : 21, fontWeight: 900, color: '#FFF',
                            lineHeight: 1, letterSpacing: '-0.02em' }}>{val}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                {ch && (
                  <span style={{ fontSize: 9, color: ch.pos ? '#22C55E' : '#EF4444', fontWeight: 700 }}>
                    {ch.pos ? '▲' : '▼'} {ch.label}{ind?.unit === 'B$' ? 'B' : ind?.unit === '%' ? 'pp' : ''}
                  </span>
                )}
                {d?.period && (
                  <span style={{ fontSize: 7.5, color: '#334155' }}>{periodStr(d.period)}</span>
                )}
              </div>
            </div>
          )
        })}
      </div>
      <CardFoot source="MoSPI · RBI · DGCI&S" />
    </CardShell>
  )
}

// ── Template 3: Year Comparison ───────────────────────────────

function ComparisonCard({ yearSummaries, config, w, h }) {
  const portrait = h > w
  const ind = IND_OPTIONS.find(i => i.id === config.indicatorId) ?? IND_OPTIONS[0]
  const y1data = yearSummaries?.[config.year1]
  const y2data = yearSummaries?.[config.year2]
  const v1 = y1data?.[ind.id]?.avg ?? null
  const v2 = y2data?.[ind.id]?.avg ?? null
  const diff = v1 != null && v2 != null ? v1 - v2 : null

  const Col = ({ year, val }) => (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      padding: portrait ? '24px 14px' : '18px 14px',
      background: 'rgba(255,255,255,0.025)', borderRadius: 11, border: '1px solid rgba(255,255,255,0.07)',
    }}>
      <div style={{ fontSize: 10, color: '#475569', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 12 }}>
        FY {year}-{String(Number(year) + 1).slice(-2)}
      </div>
      <div style={{ fontSize: portrait ? 56 : 44, fontWeight: 900, color: '#FFF', lineHeight: 1, letterSpacing: '-0.03em' }}>
        {val != null ? vfmt(val, ind.unit) : '—'}
      </div>
      <div style={{ fontSize: 10, color: '#64748B', marginTop: 10 }}>Avg. {ind.label}</div>
    </div>
  )

  return (
    <CardShell w={w} h={h} accent={ind.color}>
      <CardTop tag="COMPARISON" tagColor={ind.color} />
      <div style={{ fontSize: portrait ? 18 : 15, fontWeight: 800, color: '#FFF', marginBottom: portrait ? 20 : 14 }}>
        {ind.label} · Year-on-Year
      </div>
      <div style={{ display: 'flex', gap: 10, flex: 1, flexDirection: portrait ? 'column' : 'row' }}>
        <Col year={config.year1} val={v1} />
        <div style={{ display: 'flex', flexDirection: portrait ? 'row' : 'column', alignItems: 'center', justifyContent: 'center', gap: 3, minWidth: portrait ? 0 : 52 }}>
          {diff != null && <>
            <div style={{ fontSize: 12, fontWeight: 700, color: diff >= 0 ? '#22C55E' : '#EF4444' }}>{diff >= 0 ? '▲' : '▼'}</div>
            <div style={{ fontSize: 11, fontWeight: 700, color: diff >= 0 ? '#22C55E' : '#EF4444' }}>{Math.abs(diff).toFixed(2)}{ind.unit === 'B$' ? 'B' : 'pp'}</div>
          </>}
        </div>
        <Col year={config.year2} val={v2} />
      </div>
      <CardFoot source={ind.source} />
    </CardShell>
  )
}

// ── Template 4: Trend Chart (Recharts AreaChart) ──────────────

function TrendCard({ snapshot, timeseries, config, w, h }) {
  const portrait = h > w
  const ind = IND_OPTIONS.find(i => i.id === config.indicatorId) ?? IND_OPTIONS[0]
  const d = snapshot?.[ind.id]
  const vals = (timeseries ?? []).map(t => t.value).filter(v => v != null)

  // Compute explicit chart dimensions (required — no ResponsiveContainer in export cards)
  const HPAD = 34
  const chartW = w - HPAD * 2
  // Space budget: CardTop ~55px, label ~30px, hero ~75px, margins, footer ~55px
  const reservedH = portrait ? 215 : 190
  const chartH = Math.max(80, Math.min(h - reservedH, portrait ? 320 : 170))

  const ch = d ? changeFmt(d.value, d.prev) : null

  return (
    <CardShell w={w} h={h} accent={ind.color}>
      <CardTop tag="TREND" tagColor={ind.color} />
      <div style={{ fontSize: portrait ? 15 : 12, color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: 6 }}>
        {ind.label}
      </div>

      {/* Hero row */}
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 14, marginBottom: portrait ? 20 : 14 }}>
        <div style={{ fontSize: portrait ? 64 : 52, fontWeight: 900, color: '#FFFFFF', lineHeight: 1, letterSpacing: '-0.03em' }}>
          {d?.value != null ? vfmt(d.value, ind.unit) : '—'}
        </div>
        {ch && (
          <div style={{ fontSize: portrait ? 17 : 14, fontWeight: 700, color: ch.pos ? '#22C55E' : '#EF4444', paddingBottom: portrait ? 6 : 5 }}>
            {ch.pos ? '▲' : '▼'} {ch.label}{ind.unit === 'B$' ? 'B' : 'pp'}
          </div>
        )}
        <div style={{ fontSize: 10, color: '#475569', paddingBottom: portrait ? 4 : 3 }}>Latest · {periodStr(d?.period)}</div>
      </div>

      {/* Recharts AreaChart */}
      <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 10, padding: '12px 4px 8px 0', flex: 1 }}>
        {timeseries?.length > 1
          ? <MiniAreaChart data={timeseries} color={ind.color} width={chartW} height={chartH} unit={ind.unit} showAxes />
          : <div style={{ height: chartH, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#334155', fontSize: 11 }}>Loading…</div>
        }
        {/* Min / Max labels */}
        {vals.length > 0 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '2px 14px 0', fontSize: 9, color: '#334155' }}>
            <span>Min {vfmt(Math.min(...vals), ind.unit)}</span>
            <span>{timeseries?.length} periods</span>
            <span>Max {vfmt(Math.max(...vals), ind.unit)}</span>
          </div>
        )}
      </div>

      {timeseries?.length >= 2 && (
        <div style={{ fontSize: 9, color: '#334155', textAlign: 'center', marginTop: 6 }}>
          {fmtDate(timeseries[0]?.date)} — {fmtDate(timeseries[timeseries.length - 1]?.date)}
        </div>
      )}
      <CardFoot source={ind.source} />
    </CardShell>
  )
}

// ── Template 5: Top Rankings (Recharts horizontal BarChart) ───

function RankingCard({ rankings, config, w, h }) {
  const portrait = h > w
  const rawData = rankings?.data ?? []
  const valKey  = rankings?.value_key ?? 'value'
  const label   = rankings?.label ?? config.rankIndicator
  const color   = IND_OPTIONS.find(i => i.id === config.rankIndicator)?.color ?? '#06B6D4'

  // Build recharts-ready rows with a short period label
  const chartData = rawData.map((item, i) => ({
    ...item,
    label: item.quarter
      ? `${item.quarter} '${String(item.year ?? '').slice(2, 4)}`
      : fmtDate(item.date),
    rank: i + 1,
  }))

  // Explicit chart dimensions
  const HPAD = 34
  const chartW = w - HPAD * 2
  // Header ~55 (CardTop) + title ~38 + footer ~55 = 148; leave rest for chart
  const chartH = Math.max(100, Math.min(h - 148, portrait ? 540 : 270))

  return (
    <CardShell w={w} h={h} accent={color}>
      <CardTop tag="RANKINGS" tagColor={color} />
      <div style={{ fontSize: portrait ? 17 : 14, fontWeight: 800, color: '#FFF', marginBottom: portrait ? 16 : 10, letterSpacing: '-0.01em' }}>
        Top {chartData.length} · {label}
      </div>

      {/* Recharts horizontal BarChart */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
        {chartData.length > 0
          ? <MiniBarChart
              data={chartData}
              valueKey={valKey}
              color={color}
              width={chartW}
              height={chartH}
            />
          : <div style={{ width: chartW, height: chartH, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#334155', fontSize: 11 }}>
              Loading rankings…
            </div>
        }
      </div>
      <CardFoot source="MoSPI · RBI" />
    </CardShell>
  )
}

// ── Template 6: Year Recap ─────────────────────────────────────

function RecapCard({ snapshot, yearSummaries, config, w, h }) {
  const portrait = h > w
  const year = config.fiscalYear
  const ys = yearSummaries?.[year]
  const yearLabel = `FY ${year}-${String(Number(year) + 1).slice(-2)}`
  const stats = [
    { id: 'gdp',   label: 'GDP Growth',    color: '#22C55E', unit: '%'  },
    { id: 'cpi',   label: 'CPI (Avg)',     color: '#F59E0B', unit: '%'  },
    { id: 'wpi',   label: 'WPI (Avg)',     color: '#8B5CF6', unit: '%'  },
    { id: 'trade', label: 'Trade Balance', color: '#EF4444', unit: 'B$' },
    { id: 'forex', label: 'Forex (EOY)',   color: '#06B6D4', unit: 'B$' },
    { id: 'repo',  label: 'Repo Rate',     color: '#7C3AED', unit: '%'  },
  ]

  return (
    <CardShell w={w} h={h} accent="#06B6D4">
      <CardTop tag="ANNUAL RECAP" tagColor="#06B6D4" />
      <div style={{ marginBottom: portrait ? 22 : 15 }}>
        <div style={{ fontSize: portrait ? 26 : 21, fontWeight: 900, color: '#FFF', letterSpacing: '-0.02em', lineHeight: 1.1 }}>{yearLabel}</div>
        <div style={{ fontSize: 11, color: '#475569', marginTop: 4 }}>Economic Performance Review</div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: portrait ? '1fr 1fr' : 'repeat(3, 1fr)', gap: portrait ? 9 : 7, flex: 1 }}>
        {stats.map(s => {
          const val = ys?.[s.id]?.avg ?? snapshot?.[s.id]?.value ?? null
          return (
            <div key={s.id} style={{ borderLeft: `3px solid ${s.color}`, paddingLeft: 9, paddingTop: 5, paddingBottom: 5, background: s.color + '0A', borderRadius: '0 8px 8px 0' }}>
              <div style={{ fontSize: 7, color: s.color, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 3 }}>{s.label}</div>
              <div style={{ fontSize: portrait ? 20 : 17, fontWeight: 800, color: '#FFF', lineHeight: 1 }}>
                {val != null ? vfmt(val, s.unit) : '—'}
              </div>
            </div>
          )
        })}
      </div>
      <CardFoot source="MoSPI · RBI · DGCI&S" />
    </CardShell>
  )
}

// ── Template 7: Dual Indicator (two stats + recharts ComposedChart) ──

function DualCard({ snapshot, timeseries: ts1, config, w, h }) {
  const portrait = h > w
  const ind1 = IND_OPTIONS.find(i => i.id === (config.ind1 ?? 'cpi')) ?? IND_OPTIONS[1]
  const ind2 = IND_OPTIONS.find(i => i.id === (config.ind2 ?? 'wpi')) ?? IND_OPTIONS[2]
  const d1 = snapshot?.[ind1.id]
  const d2 = snapshot?.[ind2.id]
  const diff = d1?.value != null && d2?.value != null ? Math.abs(d1.value - d2.value) : null

  const HPAD = 34
  const chartW = w - HPAD * 2
  // Reserved: header ~55, title ~36, stat row ~(portrait?90:70), diff line ~24, footer ~55
  const reservedH = portrait ? 260 : 220
  const chartH = Math.max(70, Math.min(h - reservedH, portrait ? 200 : 130))

  const gradId1 = `dg1_${ind1.id}`
  const gradId2 = `dg2_${ind2.id}`

  return (
    <CardShell w={w} h={h} accent={ind1.color}>
      <CardTop tag="DUAL INDICATOR" tagColor="#F59E0B" />
      <div style={{ fontSize: portrait ? 17 : 14, fontWeight: 800, color: '#FFF', marginBottom: portrait ? 18 : 12, letterSpacing: '-0.01em' }}>
        {ind1.label} <span style={{ color: '#475569', fontWeight: 400 }}>vs</span> {ind2.label}
      </div>

      {/* Side-by-side stat boxes */}
      <div style={{ display: 'flex', gap: 10, marginBottom: portrait ? 16 : 12, flexDirection: portrait ? 'column' : 'row' }}>
        {[{ ind: ind1, d: d1 }, { ind: ind2, d: d2 }].map(({ ind, d }) => {
          const ch = d ? changeFmt(d.value, d.prev) : null
          return (
            <div key={ind.id} style={{
              flex: 1, padding: portrait ? '14px 16px' : '10px 14px',
              background: ind.color + '0F', border: `1px solid ${ind.color}22`, borderRadius: 10,
            }}>
              <div style={{ fontSize: 8, color: ind.color, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: 6 }}>{ind.label}</div>
              <div style={{ fontSize: portrait ? 46 : 36, fontWeight: 900, color: '#FFF', lineHeight: 1, letterSpacing: '-0.03em' }}>
                {d?.value != null ? vfmt(d.value, ind.unit) : '—'}
              </div>
              <div style={{ display: 'flex', gap: 6, marginTop: 6, alignItems: 'center' }}>
                {ch && <span style={{ fontSize: 10, color: ch.pos ? '#22C55E' : '#EF4444', fontWeight: 700 }}>{ch.pos ? '▲' : '▼'} {ch.label}{ind.unit === '%' ? 'pp' : 'B'}</span>}
                <span style={{ fontSize: 9, color: '#334155' }}>{periodStr(d?.period)}</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Recharts ComposedChart — both series on same axes */}
      <div style={{ flex: 1, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 8, padding: '10px 4px 6px 0' }}>
        <ComposedChart width={chartW} height={chartH}
                       margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
          <defs>
            <linearGradient id={gradId1} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor={ind1.color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={ind1.color} stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id={gradId2} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor={ind2.color} stopOpacity={0.2} />
              <stop offset="95%" stopColor={ind2.color} stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
          <XAxis dataKey="date" tickFormatter={v => new Date(v).getFullYear()}
                 tick={tickStyle} axisLine={false} tickLine={false} interval="preserveStartEnd"
                 data={ts1} />
          <YAxis tick={tickStyle} axisLine={false} tickLine={false} width={36}
                 tickFormatter={v => `${v.toFixed(1)}%`} />
          <ReferenceLine y={4} stroke="#22C55E" strokeDasharray="4 3" strokeWidth={1} />
          {/* ind1 area */}
          <Area type="monotone" dataKey="value" data={ts1}
                stroke={ind1.color} strokeWidth={2.5} fill={`url(#${gradId1})`}
                dot={false} isAnimationActive={false} />
        </ComposedChart>
      </div>

      {diff != null && (
        <div style={{ textAlign: 'center', marginTop: 8, fontSize: 9.5, color: '#64748B' }}>
          Current divergence:
          <span style={{ color: '#F59E0B', fontWeight: 700, marginLeft: 4 }}>{diff.toFixed(2)}pp</span>
          <span style={{ margin: '0 6px', opacity: 0.4 }}>·</span>
          RBI target: <span style={{ color: '#22C55E', fontWeight: 700 }}>4%</span>
        </div>
      )}
      <CardFoot source="MoSPI" />
    </CardShell>
  )
}

// ── Live Preview wrapper ───────────────────────────────────────

function LivePreview({ template, format, snapshot, timeseries, rankings, yearSummaries, formData, cardRef }) {
  const { displayW, displayH, scale, exportW, exportH } = getDisplayDims(format)
  const fmtObj = FORMATS.find(f => f.id === format) ?? FORMATS[0]

  const props = { snapshot, timeseries, rankings, yearSummaries, config: formData, w: exportW, h: exportH }
  const card = {
    snapshot:   <SnapshotCard   {...props} />,
    summary:    <SummaryCard    {...props} />,
    comparison: <ComparisonCard {...props} />,
    trend:      <TrendCard      {...props} />,
    ranking:    <RankingCard    {...props} />,
    recap:      <RecapCard      {...props} />,
    dual:       <DualCard       {...props} />,
  }[template] ?? <SnapshotCard {...props} />

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
      <div className="text-muted text-xs uppercase tracking-wider">
        {fmtObj.label} · {exportW}×{exportH}px
      </div>
      <div style={{
        width: displayW, height: displayH, overflow: 'hidden',
        position: 'relative', borderRadius: 10, flexShrink: 0,
        boxShadow: '0 0 0 1px rgba(255,255,255,0.07), 0 16px 48px rgba(0,0,0,0.7)',
      }}>
        <div ref={cardRef} style={{ transformOrigin: 'top left', transform: `scale(${scale})`, position: 'absolute', top: 0, left: 0 }}>
          {card}
        </div>
      </div>
    </div>
  )
}

// ── Configure Panel ────────────────────────────────────────────

const SEL = "w-full bg-bg border border-white/[0.07] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan/50"

function ConfigurePanel({ template, format, setFormat, formData, setFormData, periods, onDownload, onCopy, onCaption, exporting, copied }) {
  const upd = (k, v) => setFormData(p => ({ ...p, [k]: v }))

  return (
    <div className="space-y-4">

      {/* Format selector */}
      <div className="card p-4">
        <p className="text-muted text-xs uppercase tracking-wider mb-3">Output Format</p>
        <div className="grid grid-cols-2 gap-1.5">
          {FORMATS.map(f => (
            <button key={f.id} onClick={() => setFormat(f.id)}
                    className={`text-xs px-2 py-2 rounded-lg border transition-colors text-left
                      ${format === f.id ? 'bg-cyan/10 border-cyan/40 text-cyan' : 'border-white/[0.07] text-muted hover:text-white'}`}>
              <div>{f.label}</div>
              <div className="text-[9px] opacity-50 mt-0.5">{f.w}×{f.h}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Template-specific fields */}
      <div className="card p-4 space-y-3">
        <p className="text-muted text-xs uppercase tracking-wider">Configure Data</p>

        {(template === 'snapshot' || template === 'trend') && (
          <div>
            <label className="text-muted text-xs mb-1 block">Indicator</label>
            <select className={SEL} value={formData.indicatorId} onChange={e => upd('indicatorId', e.target.value)}>
              {IND_OPTIONS.map(i => <option key={i.id} value={i.id}>{i.label}</option>)}
            </select>
          </div>
        )}

        {template === 'trend' && (
          <div>
            <label className="text-muted text-xs mb-1 block">Periods: {formData.nPeriods}</label>
            <input type="range" min={8} max={24} step={4} value={formData.nPeriods}
                   onChange={e => upd('nPeriods', +e.target.value)} className="w-full accent-cyan" />
            <div className="flex justify-between text-muted text-[9px] mt-0.5">
              <span>8</span><span>16</span><span>24</span>
            </div>
          </div>
        )}

        {template === 'comparison' && <>
          <div>
            <label className="text-muted text-xs mb-1 block">Indicator</label>
            <select className={SEL} value={formData.indicatorId} onChange={e => upd('indicatorId', e.target.value)}>
              {IND_OPTIONS.map(i => <option key={i.id} value={i.id}>{i.label}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-muted text-xs mb-1 block">Year 1</label>
              <select className={SEL} value={formData.year1} onChange={e => upd('year1', +e.target.value)}>
                {periods.map(y => <option key={y} value={y}>FY {y}-{String(y+1).slice(-2)}</option>)}
              </select>
            </div>
            <div>
              <label className="text-muted text-xs mb-1 block">Year 2</label>
              <select className={SEL} value={formData.year2} onChange={e => upd('year2', +e.target.value)}>
                {periods.map(y => <option key={y} value={y}>FY {y}-{String(y+1).slice(-2)}</option>)}
              </select>
            </div>
          </div>
        </>}

        {template === 'ranking' && <>
          <div>
            <label className="text-muted text-xs mb-1 block">Rank by</label>
            <select className={SEL} value={formData.rankIndicator} onChange={e => upd('rankIndicator', e.target.value)}>
              {[{ id: 'gdp', label: 'GDP Growth' }, { id: 'cpi', label: 'CPI Inflation' }, { id: 'forex', label: 'Forex Reserves' }]
                .map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
            </select>
          </div>
          <div>
            <label className="text-muted text-xs mb-1 block">Show top</label>
            <div className="flex gap-2">
              {[5, 8, 10].map(n => (
                <button key={n} onClick={() => upd('nItems', n)}
                        className={`flex-1 text-xs py-1.5 rounded-lg border transition-colors
                          ${formData.nItems === n ? 'bg-cyan/10 border-cyan/40 text-cyan' : 'border-white/[0.07] text-muted hover:text-white'}`}>
                  {n}
                </button>
              ))}
            </div>
          </div>
        </>}

        {template === 'recap' && (
          <div>
            <label className="text-muted text-xs mb-1 block">Fiscal Year</label>
            <select className={SEL} value={formData.fiscalYear} onChange={e => upd('fiscalYear', +e.target.value)}>
              {periods.map(y => <option key={y} value={y}>FY {y}-{String(y+1).slice(-2)}</option>)}
            </select>
          </div>
        )}

        {template === 'dual' && <>
          <div>
            <label className="text-muted text-xs mb-1 block">Indicator 1</label>
            <select className={SEL} value={formData.ind1 ?? 'cpi'} onChange={e => upd('ind1', e.target.value)}>
              {IND_OPTIONS.map(i => <option key={i.id} value={i.id}>{i.label}</option>)}
            </select>
          </div>
          <div>
            <label className="text-muted text-xs mb-1 block">Indicator 2</label>
            <select className={SEL} value={formData.ind2 ?? 'wpi'} onChange={e => upd('ind2', e.target.value)}>
              {IND_OPTIONS.map(i => <option key={i.id} value={i.id}>{i.label}</option>)}
            </select>
          </div>
        </>}

        {template === 'summary' && (
          <p className="text-muted text-xs">Automatically shows all latest indicators.</p>
        )}
      </div>

      {/* Export */}
      <div className="card p-4 space-y-2">
        <p className="text-muted text-xs uppercase tracking-wider mb-3">Export</p>
        <button onClick={onDownload} disabled={exporting}
                className="w-full btn-primary py-2.5 flex items-center justify-center gap-2 text-sm disabled:opacity-50">
          {exporting ? <RefreshCw size={14} className="animate-spin" /> : <Download size={14} />}
          {exporting ? 'Exporting…' : 'Download PNG'}
        </button>
        <button onClick={onCopy}
                className="w-full py-2.5 flex items-center justify-center gap-2 text-sm border border-white/[0.07] rounded-lg text-muted hover:text-white transition-colors">
          {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
          {copied ? 'Copied!' : 'Copy to Clipboard'}
        </button>
        <button onClick={onCaption}
                className="w-full py-2.5 flex items-center justify-center gap-2 text-sm border border-white/[0.07] rounded-lg text-muted hover:text-cyan transition-colors">
          <Sparkles size={14} className="text-cyan" /> AI Caption
        </button>
      </div>
    </div>
  )
}

// ── Caption Modal ──────────────────────────────────────────────

function CaptionModal({ open, platform, setPlatform, caption, loading, onClose, onGenerate }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="card p-6 max-w-lg w-full space-y-4" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles size={15} className="text-cyan" />
            <span className="font-semibold text-white text-sm">AI Caption Generator</span>
          </div>
          <button onClick={onClose} className="text-muted hover:text-white"><X size={15} /></button>
        </div>

        <div className="flex gap-2 flex-wrap">
          {['twitter', 'instagram', 'linkedin', 'portrait'].map(p => (
            <button key={p} onClick={() => setPlatform(p)}
                    className={`text-xs px-3 py-1.5 rounded-lg border transition-colors
                      ${platform === p ? 'bg-cyan/10 border-cyan/40 text-cyan' : 'border-white/[0.07] text-muted hover:text-white'}`}>
              {p === 'portrait' ? 'Stories' : p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>

        <button onClick={onGenerate} disabled={loading}
                className="w-full btn-primary py-2.5 flex items-center justify-center gap-2 text-sm disabled:opacity-50">
          {loading ? <RefreshCw size={13} className="animate-spin" /> : <Sparkles size={13} />}
          {loading ? 'Writing caption…' : 'Generate Caption'}
        </button>

        {caption && (
          <div className="bg-white/[0.04] border border-white/[0.08] rounded-lg p-4">
            <p className="text-sm text-white/90 leading-relaxed whitespace-pre-wrap">{caption}</p>
            <button onClick={() => navigator.clipboard.writeText(caption)}
                    className="mt-3 text-xs text-cyan hover:underline flex items-center gap-1.5">
              <Copy size={11} /> Copy caption
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────

export default function ContentStudio() {
  const [template,      setTemplate]      = useState('snapshot')
  const [format,        setFormat]        = useState('twitter')
  const [formData,      setFormData]      = useState({
    indicatorId: 'gdp', ind1: 'cpi', ind2: 'wpi',
    year1: 2024, year2: 2023,
    nPeriods: 16, rankIndicator: 'gdp', nItems: 8, fiscalYear: 2024,
  })
  const [snapshot,      setSnapshot]      = useState(null)
  const [timeseries,    setTimeseries]    = useState([])
  const [rankings,      setRankings]      = useState(null)
  const [yearSummaries, setYearSummaries] = useState({})
  const [periods,       setPeriods]       = useState([])
  const [exporting,     setExporting]     = useState(false)
  const [copied,        setCopied]        = useState(false)
  const [captionOpen,   setCaptionOpen]   = useState(false)
  const [captionPlatform, setCaptionPlatform] = useState('twitter')
  const [caption,       setCaption]       = useState('')
  const [captionLoading, setCaptionLoading] = useState(false)
  const cardRef = useRef(null)

  // Initial data
  useEffect(() => {
    api.studioSnapshot().then(setSnapshot)
    api.studioPeriods().then(d => {
      const yrs = d.years ?? []
      setPeriods(yrs)
      if (yrs.length >= 2) setFormData(p => ({ ...p, year1: yrs[0], year2: yrs[1], fiscalYear: yrs[0] }))
    })
  }, [])

  // Trend timeseries (also used by dual indicator card for ind1)
  useEffect(() => {
    if (template === 'trend') {
      api.studioTimeseries(formData.indicatorId, formData.nPeriods)
        .then(d => setTimeseries(d.data ?? []))
    } else if (template === 'dual') {
      api.studioTimeseries(formData.ind1 ?? 'cpi', 24)
        .then(d => setTimeseries(d.data ?? []))
    }
  }, [template, formData.indicatorId, formData.nPeriods, formData.ind1])

  // Rankings
  useEffect(() => {
    if (template === 'ranking') {
      api.studioRankings(formData.rankIndicator, formData.nItems).then(setRankings)
    }
  }, [template, formData.rankIndicator, formData.nItems])

  // Year summaries for comparison + recap
  useEffect(() => {
    const years = template === 'comparison'
      ? [formData.year1, formData.year2]
      : template === 'recap' ? [formData.fiscalYear] : []
    years.filter(y => y != null && !yearSummaries[y]).forEach(y => {
      api.studioYearSummary(y).then(d => setYearSummaries(prev => ({ ...prev, [y]: d })))
    })
  }, [template, formData.year1, formData.year2, formData.fiscalYear])

  // Export: download PNG
  async function handleDownload() {
    if (!cardRef.current) return
    setExporting(true)
    try {
      const { default: html2canvas } = await import('html2canvas')
      const canvas = await html2canvas(cardRef.current, {
        scale: 1, useCORS: true, allowTaint: true,
        backgroundColor: null, logging: false,
      })
      canvas.toBlob(blob => {
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `IndiaEconomicPulse_${template}_${format}.png`
        a.click()
        URL.revokeObjectURL(url)
      }, 'image/png')
    } catch (e) {
      console.error('Export failed', e)
    } finally {
      setExporting(false)
    }
  }

  // Export: copy to clipboard
  async function handleCopy() {
    if (!cardRef.current) return
    try {
      const { default: html2canvas } = await import('html2canvas')
      const canvas = await html2canvas(cardRef.current, { scale: 1, useCORS: true, backgroundColor: null })
      canvas.toBlob(async blob => {
        await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
        setCopied(true)
        setTimeout(() => setCopied(false), 2500)
      }, 'image/png')
    } catch (e) {
      console.error('Copy failed', e)
    }
  }

  // AI caption
  async function handleCaption() {
    setCaptionLoading(true); setCaption('')
    try {
      const res = await api.aiCaption(template, { template, indicatorId: formData.indicatorId, format }, captionPlatform)
      setCaption(res.caption)
    } catch (e) {
      setCaption(`Error: ${e.message}`)
    } finally {
      setCaptionLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-[1400px]">
      <div className="page-header mb-4">
        <h1>Content Studio</h1>
        <p>Design shareable economic data graphics · Export PNG · AI-powered captions</p>
      </div>

      {/* Template tab bar */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-1 scrollbar-hide">
        {TEMPLATES.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setTemplate(id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl border whitespace-nowrap text-sm flex-shrink-0 transition-all
                    ${template === id
                      ? 'bg-cyan/10 border-cyan/30 text-cyan'
                      : 'border-white/[0.07] text-muted hover:text-white hover:border-white/[0.15]'
                    }`}>
            <Icon size={13} /> {label}
          </button>
        ))}
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 xl:grid-cols-[260px_1fr] gap-5 items-start">
        <ConfigurePanel
          template={template} format={format} setFormat={setFormat}
          formData={formData} setFormData={setFormData} periods={periods}
          onDownload={handleDownload} onCopy={handleCopy}
          onCaption={() => setCaptionOpen(true)}
          exporting={exporting} copied={copied}
        />

        <div className="flex flex-col items-center">
          <LivePreview
            template={template} format={format}
            snapshot={snapshot} timeseries={timeseries}
            rankings={rankings} yearSummaries={yearSummaries}
            formData={formData} cardRef={cardRef}
          />
        </div>
      </div>

      <CaptionModal
        open={captionOpen}
        platform={captionPlatform} setPlatform={setCaptionPlatform}
        caption={caption} loading={captionLoading}
        onClose={() => setCaptionOpen(false)}
        onGenerate={handleCaption}
      />
    </div>
  )
}
