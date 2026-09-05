import React from "react";
import { LayoutDashboard, Bot, ShieldAlert, FileText } from "lucide-react";

export default function Sidebar({ activeSection, setActiveSection }) {
  const navItems = [
    { id: "overview", label: "Executive Overview", icon: LayoutDashboard },
    { id: "governance", label: "Agent Governance", icon: Bot },
    { id: "remediation", label: "Remediation & Review", icon: ShieldAlert },
    { id: "audit", label: "Audit Ledger", icon: FileText },
  ];

  return (
    <aside className="w-14 border-r border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xl flex flex-col items-center py-4 gap-3 sticky top-14 h-[calc(100vh-3.5rem)] z-30 shrink-0 shadow-xs transition-colors select-none">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = activeSection === item.id;
        return (
          <button
            key={item.id}
            onClick={() => setActiveSection(item.id)}
            title={item.label}
            className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200 cursor-pointer relative group ${
              isActive
                ? "bg-gradient-to-r from-zinc-800 to-zinc-900 text-white border border-zinc-700/80 shadow-[0_0_12px_rgba(255,255,255,0.05)] font-semibold"
                : "text-zinc-400 hover:bg-zinc-900/80 hover:text-white"
            }`}
          >
            <Icon className={`w-4 h-4 ${isActive ? "text-emerald-400" : ""}`} />

            {/* Active Pill Accent Bar */}
            {isActive && (
              <span className="absolute -left-2.5 top-1/2 -translate-y-1/2 w-1 h-5 rounded-r-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
            )}

            {/* Tooltip on hover */}
            <span className="absolute left-14 px-2.5 py-1 bg-zinc-900 text-zinc-100 text-xs font-mono font-medium rounded-lg shadow-2xl border border-zinc-700/80 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
              {item.label}
            </span>
          </button>
        );
      })}
    </aside>
  );
}




