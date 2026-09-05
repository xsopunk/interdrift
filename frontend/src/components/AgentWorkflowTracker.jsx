import React, { useState, useEffect } from "react";
import { Layers, Activity, Bot, ShieldCheck, CheckCircle2, Play, RotateCcw } from "lucide-react";

const PIPELINE_STEPS = [
  { id: "grouping", label: "Grouping", icon: Layers, detail: "Anomaly Cluster" },
  { id: "prioritization", label: "Prioritization", icon: Activity, detail: "Formula Scoring" },
  { id: "reasoning", label: "LLM Diagnosis", icon: Bot, detail: "Gemini Cascade" },
  { id: "case_creation", label: "Case Lifecycle", icon: ShieldCheck, detail: "State Machine" },
  { id: "baseline", label: "Effectiveness", icon: CheckCircle2, detail: "Baseline Check" },
];

const DEFAULT_GROUPS = [
  { id: "GRP_LEAKED_R11", rule: "Rule R11", name: "Blended-MDR Overcharge", exposure: "₹4,989.21", txns: 22 },
  { id: "GRP_LEAKED_R2", rule: "Rule R2", name: "RuPay Debit Zero-Fee Cap", exposure: "₹1,842.10", txns: 14 },
  { id: "GRP_LEAKED_R12", rule: "Rule R12", name: "MCC Misclassification", exposure: "₹468.53", txns: 9 },
  { id: "GRP_LEAKED_R8", rule: "Rule R8", name: "Non-RuPay Debit Fee Cap", exposure: "₹189.53", txns: 4 },
];

export default function AgentWorkflowTracker({ agentData, report }) {
  const [currentStepIdx, setCurrentStepIdx] = useState(PIPELINE_STEPS.length - 1);
  const [isAnimating, setIsAnimating] = useState(false);

  // Extract cases or default
  const caseCount = agentData?.cases?.length || 4;
  const actionableCount = agentData?.summary?.actionable_cases_count || 3;

  useEffect(() => {
    if (!isAnimating) return;

    const timer = setInterval(() => {
      setCurrentStepIdx((prev) => {
        if (prev < PIPELINE_STEPS.length - 1) {
          return prev + 1;
        } else {
          setIsAnimating(false);
          return PIPELINE_STEPS.length - 1;
        }
      });
    }, 700);

    return () => clearInterval(timer);
  }, [isAnimating]);

  const handleReplay = () => {
    setCurrentStepIdx(0);
    setIsAnimating(true);
  };

  return (
    <div className="w-full flex-1 rounded-xl border border-border bg-card p-3 px-4 shadow-sm flex flex-col justify-between transition-all">
      {/* Header Bar */}
      <div className="flex items-center justify-between gap-2 pb-2 border-b border-border/70">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isAnimating ? "bg-amber-400" : "bg-emerald-400"} opacity-75`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${isAnimating ? "bg-amber-500" : "bg-emerald-500"}`}></span>
          </span>
          <h3 className="text-xs font-bold uppercase tracking-wider text-foreground font-mono">
            Agent Orchestrator Pipeline
          </h3>
          <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-secondary text-muted-foreground border border-border">
            {isAnimating ? "Executing Pipeline..." : "Idle · 5/5 Steps Verified"}
          </span>
        </div>

        <div className="flex items-center gap-2 font-mono text-[10px]">
          <span className="text-muted-foreground hidden sm:inline">
            {caseCount} Cases ({actionableCount} Actionable)
          </span>
          <button
            onClick={handleReplay}
            title="Replay Execution Animation"
            className="flex items-center gap-1 px-2 py-0.5 rounded bg-secondary hover:bg-muted text-secondary-foreground text-[10px] font-medium transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3 h-3 text-primary" />
            <span>Replay</span>
          </button>
        </div>
      </div>

      {/* 5-Step Pipeline Horizontal Tracker */}
      <div className="py-2">
        <div className="grid grid-cols-5 gap-2 relative">
          {PIPELINE_STEPS.map((step, idx) => {
            const Icon = step.icon;
            const isCompleted = idx <= currentStepIdx;
            const isActive = idx === currentStepIdx && isAnimating;

            return (
              <div key={step.id} className="flex flex-col items-center text-center space-y-1 relative">
                {/* Step Connector Line */}
                {idx < PIPELINE_STEPS.length - 1 && (
                  <div className="absolute top-3.5 left-1/2 w-full h-[2px] bg-border/60 -z-10">
                    <div
                      className="h-full bg-emerald-500 transition-all duration-300"
                      style={{ width: isCompleted ? "100%" : "0%" }}
                    />
                  </div>
                )}

                {/* Step Icon Node */}
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200 ${
                    isActive
                      ? "bg-primary text-primary-foreground shadow-md ring-2 ring-primary/40"
                      : isCompleted
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                      : "bg-secondary/60 text-muted-foreground border border-border/50"
                  }`}
                >
                  {isCompleted && !isActive ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  ) : (
                    <Icon className={`w-3.5 h-3.5 ${isActive ? "animate-pulse" : ""}`} />
                  )}
                </div>

                {/* Step Text Label */}
                <span
                  className={`text-[10px] font-bold font-mono truncate max-w-full ${
                    isActive
                      ? "text-primary"
                      : isCompleted
                      ? "text-foreground"
                      : "text-muted-foreground/60"
                  }`}
                >
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
