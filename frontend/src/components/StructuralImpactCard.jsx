import React from "react";
import { Scale, ShieldAlert } from "lucide-react";

export default function StructuralImpactCard({ mccAmount = 0, structuralAmount = 0 }) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col justify-between h-full space-y-6">
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Scale className="w-4 h-4 text-amber-500"/>
          <h3 className="text-base font-bold text-foreground tracking-tight">
            Batch Structural Audits
          </h3>
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          Aggregated contract anomalies detected across the entire settlement batch via Layer 1 batch auditing.
        </p>

        {/* MCC Metric Container */}
        <div className="p-4 rounded-lg bg-secondary border border-border space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-foreground">MCC Drift Impact (R12)</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
              Illustrative
            </span>
          </div>
          <div className="text-xl font-bold font-mono text-amber-600 dark:text-amber-400">
            ₹{Number(mccAmount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-muted-foreground">
            Slippage from misassigned high-rate retail MCC instead of enterprise B2B profile.
          </p>
        </div>

        {/* Blended MDR Metric Container */}
        <div className="p-4 rounded-lg bg-secondary border border-border space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-foreground">Blended-MDR Spread (R11)</span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
              IC+ Spread
            </span>
          </div>
          <div className="text-xl font-bold font-mono text-amber-600 dark:text-amber-400">
            ₹{Number(structuralAmount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-muted-foreground">
            Contracted flat-rate cost above true BIN-tier interchange costs.
          </p>
        </div>
      </div>

      <div className="pt-4 border-t border-border flex items-center justify-between text-[11px] text-muted-foreground font-mono">
        <span className="flex items-center gap-1">
          <ShieldAlert className="w-3.5 h-3.5 text-primary"/>
          Pre-negotiation audit
        </span>
        <span>Reclaimable</span>
      </div>
    </div>
  );
}
