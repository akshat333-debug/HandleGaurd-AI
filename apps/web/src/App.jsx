import { NavLink, Route, Routes } from "react-router-dom";
import {
  Activity,
  Bot,
  ClipboardList,
  LayoutDashboard,
  ShieldAlert,
  Video,
} from "lucide-react";
import Dashboard from "./pages/Dashboard.jsx";
import Incidents from "./pages/Incidents.jsx";
import IncidentDetail from "./pages/IncidentDetail.jsx";
import Videos from "./pages/Videos.jsx";
import Assistant from "./pages/Assistant.jsx";

const links = [
  { to: "/", label: "Operations", icon: LayoutDashboard },
  { to: "/incidents", label: "Incidents", icon: ClipboardList },
  { to: "/videos", label: "Videos", icon: Video },
  { to: "/assistant", label: "Assistant", icon: Bot },
];

export default function App() {
  return (
    <div className="min-h-dvh flex bg-canvas">
      <aside className="w-60 shrink-0 border-r border-slate-200 bg-white px-4 py-6">
        <div className="flex items-center gap-2 px-2 mb-8">
          <ShieldAlert className="text-accent" size={22} aria-hidden="true" />
          <div>
            <p className="font-mono text-sm font-semibold tracking-tight">HandleGuard AI</p>
            <p className="text-xs text-slate-500">Damage-prevention ops</p>
          </div>
        </div>
        <nav aria-label="Primary" className="space-y-1">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-md px-3 py-2 text-sm min-h-11 cursor-pointer transition-colors duration-200 ${
                  isActive ? "bg-slate-800 text-white" : "text-slate-600 hover:bg-muted"
                }`
              }
            >
              <Icon size={16} aria-hidden="true" />
              {label}
            </NavLink>
          ))}
        </nav>
        <p className="mt-10 px-2 text-[11px] leading-relaxed text-slate-400">
          Behaviour analysis only. No worker identity. Risk events are decision support, not confirmed damage.
        </p>
      </aside>
      <div className="flex-1 min-w-0">
        <header className="h-14 border-b border-slate-200 bg-white flex items-center justify-between px-6">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <Activity size={16} className="text-accent" aria-hidden="true" />
            Supervisor console
          </div>
          <span className="font-mono text-xs text-slate-400">prototype 0.1.0</span>
        </header>
        <main className="p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/incidents/:id" element={<IncidentDetail />} />
            <Route path="/videos" element={<Videos />} />
            <Route path="/assistant" element={<Assistant />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
