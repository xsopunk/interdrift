import React from "react";
import { TrendingDown, TrendingUp, Minus, Activity, ShieldCheck, AlertTriangle } from "lucide-react";

export default function ControlEffectivenessCard({ effectiveness = null }) {
  if (!effectiveness || effectiveness.status !== "computed") {
    return null;
  }

  const { verdict, baseline_snapshot_id, baseline_captured_at, metrics = {}, by_category = {} } = effectiveness;

  const totalLeaked = metrics.total_leaked || {};
  const structural = metrics.structural_overcharge || {};
  const exceptions = metrics.exception_count || {};
  const matchRate = metrics.match_rate || {};

  const getVerdictBadge = (v) => {
    switch (v) {
      case "IMPROVING":
        return {
          label: "Control Effective (Improving)",
          color: "text-emerald-500 bg-emerald-500/10 border-emerald-500/30",
          icon: TrendingDown,
        };
      case "REGRESSING":
        return {
          label: "Fee Leakage Increased",
          color: "text-red-500 bg-red-500/10 border-red-500/30",
          icon: TrendingUp,
        };
      case "MIXED":
        return {
          label: "Partial Effectiveness (Review Needed)",
          color: "text-amber-500 bg-amber-500/10 border-amber-500/30",
          icon: AlertTriangle,
        };
      case "STABLE":
      default:
        return {
          label: "Baseline Locked (Stable)",
          color: "text-blue-500 bg-blue-500/10 border-blue-500/30",
          icon: Minus,
        };
    }
  };

  const badge = getVerdictBadge(verdict);
  const VerdictIcon = badge.icon;

  const formatDelta = (val, isPercentage = true, invertGood = false) => {
    if (val === null || val === undefined) return "—";
    const sign = val > 0 ? "+" : "";
    const isGood = invertGood ? val < 0 : val > 0;
    const color = val === 0 ? "text-muted-foreground" : isGood ? "text-emerald-500" : "text-destructive";
    return <span className={`font-bold font-mono ${color}`}>{sign}{val}{isPercentage ? "%" : ""}</span>;
  };

  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-foreground">Control Effectiveness & Multi-Batch Tracking</h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-secondary text-secondary-foreground border border-border">
                Module 10
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground mt-0.5">
              Comparative audit against baseline <span className="font-mono text-foreground font-medium">{baseline_snapshot_id}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className={`flex items-center gap-1.5 px-3 py-1 rounded-lg border text-xs font-semibold ${badge.color}`}>
            <VerdictIcon className="w-3.5 h-3.5" />
            <span>{badge.label}</span>
          </div>
        </div>
      </div>

      {/* Metric Comparison Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Direct Leakage */}
        <div className="p-3.5 rounded-lg bg-secondary/30 border border-border space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Direct Leakage</span>
          <div className="flex items-baseline justify-between">
            <span className="text-base font-bold font-mono text-foreground">
              ₹{(totalLeaked.current_inr || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </span>
            <div className="text-xs">
              {formatDelta(totalLeaked.percent_change ?? totalLeaked.percent_reduction, true, true)}
            </div>
          </div>
          <p className="text-[10px] text-muted-foreground">
            Baseline: ₹{(totalLeaked.baseline_inr || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </p>
        </div>

        {/* Structural Spread */}
        <div className="p-3.5 rounded-lg bg-secondary/30 border border-border space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Structural Spread (R11)</span>
          <div className="flex items-baseline justify-between">
            <span className="text-base font-bold font-mono text-foreground">
              ₹{(structural.current_inr || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </span>
            <div className="text-xs">
              {formatDelta(structural.percent_change ?? structural.percent_reduction, true, true)}
            </div>
          </div>
          <p className="text-[10px] text-muted-foreground">
            Baseline: ₹{(structural.baseline_inr || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </p>
        </div>

        {/* Compliance Rate */}
        <div className="p-3.5 rounded-lg bg-secondary/30 border border-border space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Statutory Match Rate</span>
          <div className="flex items-baseline justify-between">
            <span className="text-base font-bold font-mono text-foreground">
              {matchRate.current_pct || 0}%
            </span>
            <div className="text-xs">
              {formatDelta(matchRate.delta_pct, true, false)}
            </div>
          </div>
          <p className="text-[10px] text-muted-foreground">
            Baseline: {matchRate.baseline_pct || 0}%
          </p>
        </div>

        {/* Exceptions */}
        <div className="p-3.5 rounded-lg bg-secondary/30 border border-border space-y-1">
          <span className="text-[10px] font-mono text-muted-foreground uppercase">Unresolved Exceptions</span>
          <div className="flex items-baseline justify-between">
            <span className="text-base font-bold font-mono text-foreground">
              {exceptions.current || 0} Items
            </span>
            <div className="text-xs">
              {formatDelta(exceptions.percent_change ?? exceptions.percent_reduction, true, true)}
            </div>
          </div>
          <p className="text-[10px] text-muted-foreground">
            Baseline: {exceptions.baseline || 0} items
          </p>
        </div>
      </div>
    </div>
  );
}
