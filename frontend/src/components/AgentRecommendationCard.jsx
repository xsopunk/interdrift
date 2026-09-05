import React, { useState } from "react";
import { Bot, ShieldCheck, ShieldAlert, CheckCircle2, XCircle, ChevronDown, ChevronUp } from "lucide-react";

const ACTION_LABELS = {
  request_mdr_refund: "Request MDR Refund",
  file_regulatory_dispute: "File Regulatory Dispute",
  audit_gateway_fee_config: "Audit Gateway Configuration",
  migrate_to_ic_plus_pricing: "Migrate to IC+ Pricing",
  correct_mcc_mapping: "Correct MCC Mapping",
  supply_l2_l3_data: "Supply L2/L3 Data",
  renegotiate_contract_rate: "Renegotiate Contract Rate",
  enable_least_cost_routing: "Enable Least-Cost Routing",
  escalate_to_acquirer: "Escalate to Acquirer",
  request_manual_review: "Manual Review Required",
  no_action_required: "No Action Required",
};

const STATUS_BADGE = {
  AWAITING_HUMAN_APPROVAL: { label: "Awaiting Your Approval", color: "text-purple-500 bg-purple-500/10 border-purple-500/20" },
  INVESTIGATING: { label: "Investigating", color: "text-amber-500 bg-amber-500/10 border-amber-500/20" },
  ACTION_RECOMMENDED: { label: "Action Recommended", color: "text-orange-500 bg-orange-500/10 border-orange-500/20" },
  MONITORING: { label: "Monitoring", color: "text-cyan-500 bg-cyan-500/10 border-cyan-500/20" },
  IMPROVED: { label: "Improved", color: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20" },
  ESCALATED: { label: "Escalated", color: "text-red-500 bg-red-500/10 border-red-500/20" },
};

const CATEGORY_TITLES = {
  MCC_Misclassification: "Merchant Category (MCC) Misclassification",
  Blended_vs_IC_Plus: "Blended Flat-Rate vs. Interchange-Plus Cost Spread",
  RuPay_Credit_UPI: "RuPay Credit on UPI Statutory Fee Cap Breach",
  PPI_Wallet_UPI: "Prepaid Wallet (PPI) on UPI Statutory Fee Cap Breach",
  Credit_Cards_Market: "Commercial & Consumer Card Interchange Tier Review",
  RuPay_Debit: "RuPay Debit Mandatory Zero-Fee Violation",
  Debit_Non_RuPay: "Non-RuPay Debit Card Cap Violation",
  Unclassified: "Unclassified Routing Exceptions (Missing Metadata)",
};

export default function AgentRecommendationCard({ cases = [], onApprove, onReject }) {
  const [expandedId, setExpandedId] = useState(null);

  // Show top 5 actionable cases sorted by priority
  const topCases = cases
    .filter((c) => c.status !== "CLOSED")
    .sort((a, b) => (a.priority_rank || 99) - (b.priority_rank || 99))
    .slice(0, 5);

  if (topCases.length === 0) return null;

  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm space-y-4">
      <div className="flex items-center gap-2 pb-3 border-b border-border">
        <div className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
          <Bot className="w-4 h-4" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-foreground">Agent Priority Queue</h3>
          <p className="text-[11px] text-muted-foreground">
            Root-cause clusters ranked by recoverable exposure, regulatory confidence, recurrence & controllability
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {topCases.map((c) => {
          const isExpanded = expandedId === c.case_id;
          const badge = STATUS_BADGE[c.status] || STATUS_BADGE.INVESTIGATING;
          const actionLabel = ACTION_LABELS[c.recommended_action] || c.recommended_action;
          const isAwaiting = c.status === "AWAITING_HUMAN_APPROVAL";
          const title = CATEGORY_TITLES[c.category] || (c.category ? c.category.replace(/_/g, " ") : c.group_id.replace(/_/g, " "));

          return (
            <div
              key={c.case_id}
              className={`rounded-lg border transition-all ${
                isAwaiting
                  ? "border-purple-500/30 bg-purple-500/5"
                  : "border-border bg-card"
              }`}
            >
              {/* Case Header */}
              <button
                type="button"
                onClick={() => setExpandedId(isExpanded ? null : c.case_id)}
                className="w-full p-4 flex items-center justify-between text-left cursor-pointer"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xs font-bold text-primary font-mono shrink-0">
                    #{c.priority_rank || "—"}
                  </span>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-semibold text-foreground truncate">
                        {title}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground border border-border shrink-0">
                        Rule {(c.rule_ids || []).join(", ")}
                      </span>
                      {c.source_status === "illustrative" && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-500 border border-amber-500/20 shrink-0">
                          Modeled Benchmark
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-muted-foreground mt-0.5 truncate">
                      {c.root_cause || "Pending investigation..."}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0 ml-3">
                  <span className={`text-sm font-bold font-mono ${c.financial_exposure > 0 ? "text-destructive" : "text-muted-foreground"}`}>
                    ₹{(c.financial_exposure || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-medium ${badge.color}`}>
                    {badge.label}
                  </span>
                  {isExpanded ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
                </div>
              </button>

              {/* Expanded Details */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-0 space-y-3 border-t border-border/60">
                  {/* Agent Diagnosis */}
                  <div className="mt-3 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-[10px] font-mono text-primary uppercase font-semibold">
                      <Bot className="w-3 h-3" />
                      <span>Agent Diagnosis & Reasoning</span>
                    </div>
                    <p className="text-xs leading-relaxed text-foreground/90">
                      {c.agent_reasoning || "Awaiting agent analysis..."}
                    </p>
                  </div>

                  {/* Recommended Action */}
                  <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 border border-border">
                    <div>
                      <span className="text-[10px] font-mono text-muted-foreground uppercase">Recommended Action</span>
                      <p className="text-xs font-semibold text-foreground mt-0.5">{actionLabel}</p>
                      <p className="text-[11px] text-muted-foreground mt-0.5">
                        {c.transaction_count || 0} transactions · Confidence: {c.confidence || "—"}
                      </p>
                    </div>
                    {c.human_approval_required && (
                      <div className="flex items-center gap-1 text-[10px] text-purple-500 font-mono">
                        <ShieldAlert className="w-3 h-3" />
                        <span>Requires Approval</span>
                      </div>
                    )}
                  </div>

                  {/* Approval Buttons (only for AWAITING_HUMAN_APPROVAL) */}
                  {isAwaiting && (
                    <div className="flex items-center gap-2 pt-2">
                      <button
                        type="button"
                        onClick={() => onApprove && onApprove(c.case_id)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium transition-colors cursor-pointer"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Approve & Monitor</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => onReject && onReject(c.case_id)}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-secondary hover:bg-muted text-foreground text-xs font-medium border border-border transition-colors cursor-pointer"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Reject & Escalate</span>
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
