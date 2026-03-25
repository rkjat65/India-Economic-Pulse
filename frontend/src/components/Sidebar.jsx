import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, TrendingUp, Flame, Globe2,
  Banknote, Sparkles, PenSquare,
} from 'lucide-react'

const links = [
  { to: '/dashboard',      icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/gdp',            icon: TrendingUp,      label: 'GDP Analysis' },
  { to: '/inflation',      icon: Flame,           label: 'Inflation' },
  { to: '/trade',          icon: Globe2,          label: 'Trade' },
  { to: '/forex',          icon: Banknote,        label: 'Forex & Rates' },
  { to: '/ai-studio',      icon: Sparkles,        label: 'AI Studio' },
  { to: '/content-studio', icon: PenSquare,       label: 'Content Studio' },
]

export default function Sidebar() {
  return (
    <aside className="w-[60px] flex-shrink-0 flex flex-col items-center py-4 gap-1"
           style={{ background: '#0D0D16', borderRight: '1px solid rgba(255,255,255,0.06)' }}>

      {/* Brand */}
      <div className="w-9 h-9 rounded-xl bg-cyan flex items-center justify-center
                      text-black font-bold text-sm mb-4 flex-shrink-0">
        IE
      </div>

      {/* Nav links */}
      <nav className="flex flex-col gap-1 flex-1 w-full px-2">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            title={label}
            className={({ isActive }) =>
              `flex items-center justify-center w-full h-10 rounded-lg transition-all duration-150 group relative
               ${isActive
                 ? 'bg-cyan/10 text-cyan'
                 : 'text-muted hover:text-white hover:bg-white/[0.05]'
               }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5
                                   bg-cyan rounded-r-full" />
                )}
                <Icon size={18} strokeWidth={isActive ? 2.5 : 1.8} />

                {/* Tooltip */}
                <span className="absolute left-full ml-3 px-2 py-1 bg-card border border-white/[0.07]
                                  text-white text-xs rounded-md whitespace-nowrap
                                  opacity-0 pointer-events-none group-hover:opacity-100
                                  transition-opacity duration-150 z-50">
                  {label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom avatar */}
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan to-purple
                      flex items-center justify-center text-xs font-bold text-white
                      flex-shrink-0 cursor-pointer"
           title="RK Jat | rkjat.in">
        RJ
      </div>
    </aside>
  )
}
