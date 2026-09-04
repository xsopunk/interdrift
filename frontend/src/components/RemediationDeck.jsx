import React, { useState } from "react";
import { AlertOctagon, ArrowUpRight, Check, Sparkles } from "lucide-react";

export default function RemediationDeck({ offenders = [] }) {
  const [reclaimedIds, setReclaimedIds] = useState(new Set());

  if (!offenders || offenders.length === 0) return null;

  const toggleReclaim = (txnId) => {
    setReclaimedIds((prev) => {
      const next = new Set(prev);
      if (next.has(txnId)) {
        next.delete(txnId);
      } else {
        next.add(txnId);
      }
      return next;
    });
  };

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-border gap-2">
        <div>
          <div className="flex items-center gap-2">
            <AlertOctagon className="w-4 h-4 text-destructive dark:text-red-400"/>
            <h3 className="text-base font-bold text-foreground tracking-tight">
              Granular Transaction Spotlights (Row-Level Evidence)
            </h3>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Individual transaction overcharge line items. Strategic root-cause remediation is orchestrated in the Agent Priority Queue above.
          </p>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-destructive/10 text-destructive dark:text-red-400 border border-destructive/20 font-medium self-start sm:self-auto">
          {offenders.length} Transaction Highlights
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {offenders.map((item, idx) => {
          const isReclaimed = reclaimedIds.has(item.transaction_id);

          return (
            <div
              key={idx}
              className="rounded-lg border border-border bg-card hover:border-border/80 transition-all p-4 flex flex-col justify-between space-y-4 shadow-xs"
            >
              <div className="space-y-3">
                {/* Header row: Transaction & Delta */}
                <div className="flex items-center justify-between gap-2 border-b border-border/60 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-foreground">
                      {item.transaction_id}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground border border-border">
                      Rule {item.rule_id}
                    </span>
                  </div>
                  <div className="text-right font-mono">
                    <span className="text-xs font-bold text-destructive dark:text-red-400">
                      +₹{Number(item.delta).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>

                {/* LLM Diagnostic Explanation */}
                <div className="space-y-1.5">
                  <div className="flex items-center gap-1.5 text-[10px] font-mono text-primary uppercase font-semibold">
                    <Sparkles className="w-3 h-3"/>
                    <span>Agent Diagnostic Verdict</span>
                  </div>
                  <p className="text-sm leading-relaxed text-foreground/90 font-sans">
                    {item.explanation || "Statutory fee discrepancy flagged by deterministic engine."}
                  </p>
                </div>
              </div>

              {/* Action Bar */}
              <div className="pt-3 border-t border-border/60 flex items-center justify-between text-xs">
                <span className="text-[11px] font-mono text-muted-foreground">
                  Status: <span className="text-destructive font-medium">Overcharged</span>
                </span>
                <button
                  type="button"
                  onClick={() => toggleReclaim(item.transaction_id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors cursor-pointer ${
                    isReclaimed
                      ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30"
                      : "bg-primary text-primary-foreground hover:opacity-90"
                  }`}
                >
                  {isReclaimed ? (
                    <>
                      <Check className="w-3.5 h-3.5"/>
                      <span>Remediation Staged</span>
                    </>
                  ) : (
                    <>
                      <ArrowUpRight className="w-3.5 h-3.5"/>
                      <span>Stage Remediation</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
