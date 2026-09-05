import React from "react";
import { Scale, ShieldAlert } from "lucide-react";

export default function StructuralImpactCard({ mccAmount = 0, structuralAmount = 0 }) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-border/80">
        <div className="flex items-center gap-2">
          <Scale className="w-4 h-4 text-amber-500"/>
          <h3 className="text-sm font-bold text-foreground tracking-tight">
            Batch Structural Audits
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-secondary text-muted-foreground border border-border">
            Layer 1 Batch Engine
          </span>
        </div>
        <div className="flex items-center gap-1 text-[11px] text-muted-foreground font-mono">
          <ShieldAlert className="w-3.5 h-3.5 text-primary"/>
          <span>Contract Review Evidence</span>
        </div>
      </div>

      {/* Horizontal 2-Column Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* MCC Metric Container */}
        <div className="p-3.5 rounded-lg bg-secondary/50 border border-border space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-foreground">MCC Drift Impact (R12)</span>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
              Illustrative
            </span>
          </div>
          <div className="text-lg font-bold font-mono text-amber-600 dark:text-amber-400">
            ₹{Number(mccAmount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[10px] text-muted-foreground leading-tight">
            Slippage from misassigned high-rate retail MCC instead of enterprise B2B profile.
          </p>
        </div>

        {/* Blended MDR Metric Container */}
        <div className="p-3.5 rounded-lg bg-secondary/50 border border-border space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-foreground">Blended-MDR Spread (R11)</span>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
              IC+ Spread
            </span>
          </div>
          <div className="text-lg font-bold font-mono text-amber-600 dark:text-amber-400">
            ₹{Number(structuralAmount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[10px] text-muted-foreground leading-tight">
            Contracted flat-rate cost above true BIN-tier interchange costs.
          </p>
        </div>
      </div>
    </div>
  );
}

