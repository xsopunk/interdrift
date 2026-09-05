import React from "react";
import { Scale, ShieldAlert } from "lucide-react";

export default function StructuralImpactCard({ audits = null, mccAmount = 0, structuralAmount = 0 }) {
  // Derive cards from audits payload if provided, or fallback to default props
  const cards = React.useMemo(() => {
    if (audits && typeof audits === "object" && Object.keys(audits).length > 0) {
      return Object.entries(audits).map(([key, data]) => {
        const delta = data.financial_impact_delta ?? data.structural_overcharge_delta ?? 0;
        const isMcc = key.toLowerCase().includes("mcc");
        const title = key
          .replace(/^R\d+_/, "")
          .replace(/_/g, " ")
          .replace(/\b\w/g, (l) => l.toUpperCase());
        const ruleIdMatch = key.match(/^R\d+/);
        const ruleTag = ruleIdMatch ? ruleIdMatch[0] : "";
        const tag = isMcc ? "Illustrative" : "IC+ Spread";
        const desc = data.recommendation || (isMcc ? "Slippage from misassigned high-rate retail MCC." : "Contracted flat-rate cost above true BIN-tier costs.");

        return {
          id: key,
          title: `${title} ${ruleTag ? `(${ruleTag})` : ""}`,
          amount: delta,
          tag,
          desc,
        };
      });
    }

    // Fallback if audits is not present
    return [
      {
        id: "mcc",
        title: "MCC Drift Impact (R12)",
        amount: mccAmount,
        tag: "Illustrative",
        desc: "Slippage from misassigned high-rate retail MCC instead of enterprise B2B profile.",
      },
      {
        id: "structural",
        title: "Blended-MDR Spread (R11)",
        amount: structuralAmount,
        tag: "IC+ Spread",
        desc: "Contracted flat-rate cost above true BIN-tier interchange costs.",
      },
    ];
  }, [audits, mccAmount, structuralAmount]);

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

      {/* Dynamic Grid Rendering */}
      <div className={`grid grid-cols-1 sm:grid-cols-${Math.min(cards.length, 3)} gap-4`}>
        {cards.map((card) => (
          <div key={card.id} className="p-3.5 rounded-lg bg-secondary/50 border border-border space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-foreground">{card.title}</span>
              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                {card.tag}
              </span>
            </div>
            <div className="text-lg font-bold font-mono text-amber-600 dark:text-amber-400">
              ₹{Number(card.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </div>
            <p className="text-[10px] text-muted-foreground leading-tight">
              {card.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

