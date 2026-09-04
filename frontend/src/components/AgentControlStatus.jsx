import React from "react";
import { Shield, Clock, CheckCircle2, AlertTriangle, Eye, XCircle } from "lucide-react";

const STATUS_CONFIG = {
  OPEN: { label: "Open", icon: Clock, color: "text-blue-500", bg: "bg-blue-500/10", border: "border-blue-500/20" },
  INVESTIGATING: { label: "Investigating", icon: Eye, color: "text-amber-500", bg: "bg-amber-500/10", border: "border-amber-500/20" },
  ACTION_RECOMMENDED: { label: "Action Ready", icon: AlertTriangle, color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/20" },
  AWAITING_HUMAN_APPROVAL: { label: "Awaiting Approval", icon: Shield, color: "text-purple-500", bg: "bg-purple-500/10", border: "border-purple-500/20" },
  MONITORING: { label: "Monitoring", icon: Eye, color: "text-cyan-500", bg: "bg-cyan-500/10", border: "border-cyan-500/20" },
  IMPROVED: { label: "Improved", icon: CheckCircle2, color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
  ESCALATED: { label: "Escalated", icon: AlertTriangle, color: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/20" },
  CLOSED: { label: "Closed", icon: XCircle, color: "text-zinc-400", bg: "bg-zinc-500/10", border: "border-zinc-500/20" },
};

export default function AgentControlStatus({ summary = {} }) {
  const statusCounts = summary.status_counts || {};
  const totalCases = summary.total_cases || 0;
  const totalExposure = summary.total_exposure_inr || 0;
  const actionable = summary.actionable_count || 0;

  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground">Agent Control Status</h3>
            <p className="text-[11px] text-muted-foreground">
              {totalCases} active cases · ₹{totalExposure.toLocaleString("en-IN", { minimumFractionDigits: 2 })} total exposure
            </p>
          </div>
        </div>
        {actionable > 0 && (
          <span className="text-[10px] font-mono px-2 py-1 rounded bg-purple-500/10 text-purple-500 border border-purple-500/20 font-medium animate-pulse">
            {actionable} Awaiting Action
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {Object.entries(statusCounts).map(([status, count]) => {
          const config = STATUS_CONFIG[status] || STATUS_CONFIG.OPEN;
          const Icon = config.icon;
          return (
            <div
              key={status}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg ${config.bg} border ${config.border} transition-all`}
            >
              <Icon className={`w-3.5 h-3.5 ${config.color}`} />
              <div>
                <span className={`text-sm font-bold ${config.color}`}>{count}</span>
                <span className="text-[10px] text-muted-foreground ml-1.5">{config.label}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
