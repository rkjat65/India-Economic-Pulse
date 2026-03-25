export default function ChartCard({ title, subtitle, children, action }) {
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-1 h-5 bg-cyan rounded-full inline-block" />
            <h3 className="text-white font-semibold text-sm">{title}</h3>
          </div>
          {subtitle && <p className="text-muted text-xs mt-1 ml-3">{subtitle}</p>}
        </div>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>
      {children}
    </div>
  )
}
