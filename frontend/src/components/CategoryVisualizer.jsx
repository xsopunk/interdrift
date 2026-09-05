import React from "react";
import { Layers } from "lucide-react";

const RAIL_METADATA = {
  R2: { name: "RuPay Debit Zero-Fee Rule", ruleTag: "Rule R2" },
  R3: { name: "RuPay Credit on UPI (Small Ticket ≤ ₹2k)", ruleTag: "Rule R3" },
  R4: { name: "RuPay Credit on UPI (Large Ticket > ₹2k)", ruleTag: "Rule R4" },
  R5: { name: "PPI Wallet on UPI (Small Ticket ≤ ₹2k)", ruleTag: "Rule R5" },
  R6b: { name: "PPI Wallet on UPI (Large Ticket > ₹2k)", ruleTag: "Rule R6b" },
  R8: { name: "Non-RuPay Debit Fee Cap (RBI ₹1,000 Cap)", ruleTag: "Rule R8" },
  R10: { name: "Commercial Card L2/L3 Downgrades", ruleTag: "Rule R10" },
  R11: { name: "Blended Flat-Rate Pricing Spread", ruleTag: "Rule R11" },
  R12: { name: "Merchant Category Code (MCC) Misalignment", ruleTag: "Rule R12" },
};

export default function CategoryVisualizer({ categories = [] }) {
  const totalLeakage = categories.reduce((sum, item) => sum + Math.abs(item.total_leaked || 0), 0);

  return (
    <div className="rounded-xl border border-border bg-card p-4 shadow-sm transition-colors space-y-3">
      <div className="pb-3 border-b border-border/80 space-y-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-primary"/>
            <h3 className="text-sm font-bold text-foreground tracking-tight">
              Fee Leakage by Rail
            </h3>
          </div>
          <span className="px-2 py-0.5 rounded bg-secondary text-secondary-foreground border border-border text-[10px] font-mono font-medium">
            {categories.length} Rails
          </span>
        </div>
        <p className="text-[11px] text-muted-foreground leading-tight">
          Detected fee slippage across statutory caps & contract pricing spreads
        </p>
      </div>

      <div className="divide-y divide-border/50">
        {categories.map((cat, idx) => {
          const share = totalLeakage > 0 ? ((Math.abs(cat.total_leaked || 0) / totalLeakage) * 100).toFixed(1) : "0.0";
          const illustrative = cat.source_status ? cat.source_status === "illustrative" : RAIL_METADATA[cat.category]?.name?.includes("Spread") || false;
          const fallbackMeta = RAIL_METADATA[cat.category] || {};
          const displayName = cat.rule_name || fallbackMeta.name || cat.category.replace(/_/g, " ");
          const ruleTag = fallbackMeta.ruleTag || (cat.category?.startsWith("R") ? `Rule ${cat.category}` : cat.category);

          return (
            <div key={idx} className="py-3 first:pt-1 last:pb-0 space-y-1.5">
              <div className="flex flex-col gap-1 text-xs">
                <div className="flex items-center justify-between gap-1 flex-wrap">
                  <span className="font-semibold text-foreground text-[11px]">
                    {displayName}
                  </span>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground border border-border">
                    {ruleTag}
                  </span>
                </div>

                <div className="flex items-center justify-between font-mono text-[11px]">
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.2 rounded border ${
                      illustrative
                        ? "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20"
                        : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                    }`}
                  >
                    {illustrative ? "Modeled Benchmark" : "Statutory Gazette"}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground text-[10px]">
                      {cat.transaction_count} txns
                    </span>
                    <span className="font-bold text-destructive dark:text-red-400 text-xs">
                      ₹{Number(cat.total_leaked).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>
              </div>

              {/* Visual Share Bar */}
              <div className="w-full bg-secondary h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-destructive dark:bg-red-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(Number(share), 2)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

