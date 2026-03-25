export default function MetricCard({ label, value, sub, color = 'cyan', icon: Icon }) {
  const colors = {
    cyan:   'text-cyan',
    green:  'text-green',
    red:    'text-red',
    amber:  'text-amber',
    purple: 'text-purple',
  }

  return (
    <div className="card p-5 flex flex-col gap-2">
      <div className="flex items-center gap-2">
        {Icon && (
          <span className={`${colors[color]} opacity-70`}>
            <Icon size={14} strokeWidth={2} />
          </span>
        )}
        <span className="text-muted text-xs uppercase tracking-widest font-medium">
          {label}
        </span>
      </div>
      <div className={`text-2xl font-bold font-mono tracking-tight ${colors[color]}`}>
        {value ?? '—'}
      </div>
      {sub && <div className="text-muted text-xs">{sub}</div>}
    </div>
  )
}
