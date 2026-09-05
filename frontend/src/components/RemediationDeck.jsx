import React, { useState } from "react";
import { AlertOctagon, ArrowUpRight, Check, Sparkles } from "lucide-react";

const RULE_NAMES = {
  R1: "Bank UPI Zero-Fee",
  R2: "RuPay Debit Zero-Fee",
  R3: "RuPay Credit UPI (≤ ₹2k)",
  R4: "RuPay Credit UPI (> ₹2k)",
  R5: "PPI Wallet UPI (≤ ₹2k)",
  R6b: "PPI Wallet UPI (> ₹2k)",
  R8: "Non-RuPay Debit Fee Cap",
  R10: "L2/L3 Downgrade Penalty",
  R11: "Blended Pricing Spread",
  R12: "MCC Rate Misalignment",
};

export default function RemediationDeck({
  offenders = [],
  cases = [],
  selectedCaseId = null,
  onClearCaseFilter,
  onGoToCase
}) {
  if (!offenders || offenders.length === 0) return null;

  // Find active case if filtered by case_id
  const activeCase = cases.find((c) => c.case_id === selectedCaseId);

  // Filter offenders by selected case if applicable
  const displayOffenders = selectedCaseId
    ? offenders.filter((item) =>
        activeCase
          ? (activeCase.affected_transactions && activeCase.affected_transactions.includes(item.transaction_id)) ||
            (activeCase.rule_ids && activeCase.rule_ids.includes(item.rule_id)) ||
            (activeCase.group_id && activeCase.group_id.includes(item.rule_id))
          : true
      )
    : offenders;

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
        <div className="flex items-center gap-2">
          {selectedCaseId && (
            <button
              onClick={onClearCaseFilter}
              className="text-xs px-2.5 py-1 rounded bg-secondary hover:bg-muted text-foreground border border-border font-mono font-medium cursor-pointer"
            >
              Clear Case Filter
            </button>
          )}
          <span className="text-[11px] font-mono px-2.5 py-1 rounded bg-destructive/10 text-destructive dark:text-red-400 border border-destructive/20 font-medium self-start sm:self-auto">
            {displayOffenders.length} Transaction Highlights
          </span>
        </div>
      </div>

      {selectedCaseId && activeCase && (
        <div className="flex items-center justify-between p-3 rounded-lg bg-primary/10 border border-primary/20 text-xs font-mono">
          <span className="text-foreground">
            Filtered by Priority Case: <strong>#{activeCase.priority_rank || activeCase.case_id}</strong> (Rule {(activeCase.rule_ids || []).join(", ")})
          </span>
          <button
            onClick={onClearCaseFilter}
            className="text-[11px] text-primary hover:underline font-bold cursor-pointer"
          >
            Show All ({offenders.length})
          </button>
        </div>
      )}

      {displayOffenders.length === 0 ? (
        <div className="p-8 text-center text-xs text-muted-foreground bg-secondary/30 rounded-lg border border-border">
          No transaction spotlights found for the selected case.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {displayOffenders.map((item, idx) => {
            const ruleLabel = RULE_NAMES[item.rule_id] || `Rule ${item.rule_id}`;
            // Match to parent case
            const parentCase = cases.find((c) =>
              (c.affected_transactions && c.affected_transactions.includes(item.transaction_id)) ||
              (c.rule_ids && c.rule_ids.includes(item.rule_id)) ||
              (c.group_id && c.group_id.includes(item.rule_id))
            );

            return (
              <div
                key={idx}
                className="rounded-lg border border-border bg-card hover:border-border/80 transition-all p-4 flex flex-col justify-between space-y-4 shadow-xs"
              >
                <div className="space-y-3">
                  {/* Header row: Transaction & Delta */}
                  <div className="flex items-center justify-between gap-2 border-b border-border/60 pb-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-xs font-bold text-foreground">
                        {item.transaction_id}
                      </span>
                      <span 
                        className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground border border-border cursor-help"
                        title={`Statutory Rule ${item.rule_id}: ${ruleLabel}`}
                      >
                        Rule {item.rule_id} · {ruleLabel}
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
                      <span>Rule Engine Verdict</span>
                    </div>
                    <p className="text-sm leading-relaxed text-foreground/90 font-sans">
                      {item.explanation || "Statutory fee discrepancy flagged by deterministic engine."}
                    </p>
                  </div>
                </div>

                {/* Action Bar */}
                <div className="pt-3 border-t border-border/60 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] font-mono text-muted-foreground">
                      Parent Case:
                    </span>
                    {parentCase ? (
                      <span className="text-[10px] font-mono font-bold text-primary px-1.5 py-0.5 rounded bg-primary/10 border border-primary/20">
                        #{parentCase.priority_rank || parentCase.case_id} ({parentCase.status})
                      </span>
                    ) : (
                      <span className="text-[10px] font-mono text-muted-foreground">Unassigned</span>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      const targetCaseId = parentCase?.case_id || selectedCaseId;
                      if (onGoToCase && targetCaseId) {
                        onGoToCase(targetCaseId);
                      }
                    }}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-primary text-primary-foreground hover:opacity-90 transition-colors cursor-pointer"
                  >
                    <ArrowUpRight className="w-3.5 h-3.5"/>
                    <span>Go to Parent Case →</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
