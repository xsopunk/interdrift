import React from "react";
import { Layers } from "lucide-react";

export default function CategoryVisualizer({ categories = [] }) {
  const totalLeakage = categories.reduce((sum, item) => sum + Math.abs(item.total_leaked || 0), 0);

  const isIllustrative = (categoryName) => {
    const lower = categoryName.toLowerCase();
    return (
      lower.includes("blended") ||
      lower.includes("mcc") ||
      lower.includes("lcr") ||
      lower.includes("downgrade")
    );
  };

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm transition-colors">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b border-border gap-2">
        <div>
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-primary"/>
            <h3 className="text-base font-bold text-foreground tracking-tight">
              Leakage Distribution by Regulatory Rail
            </h3>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Breakdown of detected fee slippage across statutory UPI/RuPay caps and structural contract spreads
          </p>
        </div>
        <div className="flex items-center gap-2 self-start sm:self-auto font-mono text-xs">
          <span className="px-2 py-0.5 rounded bg-secondary text-secondary-foreground border border-border text-[11px]">
            {categories.length} Rails Flagged
          </span>
        </div>
      </div>

      <div className="divide-y divide-border/60 mt-2">
        {categories.map((cat, idx) => {
          const share = totalLeakage > 0 ? ((Math.abs(cat.total_leaked || 0) / totalLeakage) * 100).toFixed(1) : "0.0";
          const illustrative = isIllustrative(cat.category);

          return (
            <div key={idx} className="py-4 first:pt-3 last:pb-0 space-y-2">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-foreground">
                    {cat.category.replace(/_/g, " ")}
                  </span>
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.2 rounded border ${
                      illustrative
                        ? "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20"
                        : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                    }`}
                  >
                    {illustrative ? "Modeled" : "Sourced"}
                  </span>
                </div>
                <div className="flex items-center gap-3 font-mono">
                  <span className="text-muted-foreground text-[11px]">
                    {cat.transaction_count} txns
                  </span>
                  <span className="font-bold text-destructive dark:text-red-400">
                    ₹{Number(cat.total_leaked).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-muted-foreground text-[11px] w-12 text-right">
                    {share}%
                  </span>
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
