import React, { useEffect, useState } from "react";
import { getFinalReport, getAuditTrailResults, getAgentCases, getControlEffectiveness, approveCase, rejectCase } from "./services/api";
import Navbar from "./components/Navbar";
import ControlCockpit from "./components/ControlCockpit";
import MetricCard from "./components/MetricCard";
import CategoryVisualizer from "./components/CategoryVisualizer";
import StructuralImpactCard from "./components/StructuralImpactCard";
import RemediationDeck from "./components/RemediationDeck";
import ExceptionsDrawer from "./components/ExceptionsDrawer";
import AuditTrailTable from "./components/AuditTrailTable";
import AgentControlStatus from "./components/AgentControlStatus";
import AgentRecommendationCard from "./components/AgentRecommendationCard";
import ControlEffectivenessCard from "./components/ControlEffectivenessCard";
import { TrendingDown, CheckCircle2, AlertTriangle, Layers } from "lucide-react";

export default function App() {
  const [report, setReport] = useState(null);
  const [auditRows, setAuditRows] = useState([]);
  const [agentData, setAgentData] = useState(null);
  const [effectivenessData, setEffectivenessData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadAllData = async () => {
    try {
      setLoading(true);
      const [reportData, auditData] = await Promise.all([
        getFinalReport(),
        getAuditTrailResults(),
      ]);
      setReport(reportData);
      setAuditRows(auditData.row_level_results || []);

      // Load agent cases
      try {
        const casesData = await getAgentCases();
        setAgentData(casesData);
      } catch {
        setAgentData(null);
      }

      // Load control effectiveness (Module 10)
      try {
        const effData = await getControlEffectiveness();
        setEffectivenessData(effData);
      } catch {
        setEffectivenessData(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (caseId) => {
    try {
      await approveCase(caseId);
      const casesData = await getAgentCases();
      setAgentData(casesData);
    } catch (err) {
      console.error("Approval failed:", err.message);
    }
  };

  const handleReject = async (caseId) => {
    try {
      await rejectCase(caseId);
      const casesData = await getAgentCases();
      setAgentData(casesData);
    } catch (err) {
      console.error("Rejection failed:", err.message);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 text-foreground">
        <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin mb-4" />
        <p className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
          Initializing InterDrift Audit Cockpit...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6 text-foreground">
        <div className="bg-card border border-destructive/30 p-6 rounded-xl max-w-md w-full shadow-lg">
          <h2 className="text-destructive font-bold text-base">Backend Connection Offline</h2>
          <p className="text-xs text-muted-foreground mt-2">{error}</p>
          <p className="text-[11px] text-muted-foreground font-mono mt-4">
            Ensure FastAPI backend is running on http://127.0.0.1:8000
          </p>
          <button
            onClick={loadAllData}
            className="mt-5 w-full py-2 rounded-lg bg-secondary hover:bg-muted text-xs font-medium cursor-pointer transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const { overview, leak_by_category, top_offenders, exceptions } = report;

  return (
    <div className="min-h-screen bg-background text-foreground relative selection:bg-primary selection:text-primary-foreground transition-colors duration-200">
      {/* Subtle Ambient Patterning */}
      <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] dark:bg-[radial-gradient(#27272a_1px,transparent_1px)] [background-size:16px_16px] pointer-events-none opacity-15 dark:opacity-20 z-0" />

      {/* Top Navbar */}
      <Navbar backendStatus="online" rowCount={overview.total_transactions} />

      {/* Main Container */}
      <main className="relative z-10 max-w-7xl mx-auto space-y-8 px-4 sm:px-6 lg:px-8 py-8">
        {/* Operations Cockpit */}
        <ControlCockpit onUploadSuccess={loadAllData} />

        {/* Agent Control Status (Module 9) */}
        {agentData && agentData.summary && (
          <section>
            <AgentControlStatus summary={agentData.summary} />
          </section>
        )}

        {/* Control Effectiveness & Multi-Batch Tracking (Module 10) */}
        {effectivenessData && effectivenessData.status === "computed" && (
          <section>
            <ControlEffectivenessCard effectiveness={effectivenessData} />
          </section>
        )}

        {/* Executive KPI Deck */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Total Direct Leakage"
            value={`₹${overview.total_leaked_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`}
            subtitle={`${overview.leaked_count} transactions (${overview.leaked_percent}%)`}
            variant="destructive"
            badge="Direct Loss"
            icon={TrendingDown}
            trendText={`${overview.leaked_percent}% batch loss`}
          />
          <MetricCard
            title="Statutory Match Rate"
            value={`${overview.matched_percent}%`}
            subtitle={`${overview.matched_count} compliant charges`}
            variant="success"
            badge="Compliant"
            icon={CheckCircle2}
          />
          <MetricCard
            title="Structural Spread (R11)"
            value={`₹${overview.structural_overcharge_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`}
            subtitle="Blended-MDR vs true IC+ spread"
            variant="warning"
            badge="Contract Audit"
            icon={AlertTriangle}
          />
          <MetricCard
            title="Exceptions & Flagged"
            value={`${overview.exception_count + overview.flagged_for_review_count}`}
            subtitle={`${overview.exception_count} unclassified · ${overview.flagged_for_review_count} flagged`}
            variant="primary"
            badge="Transparency"
            icon={Layers}
          />
        </section>

        {/* Regulatory Breakdown & Structural Impact */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <CategoryVisualizer categories={leak_by_category} />
          </div>
          <div className="lg:col-span-1">
            <StructuralImpactCard
              mccAmount={overview.mcc_misclassification_amount}
              structuralAmount={overview.structural_overcharge_amount}
            />
          </div>
        </section>

        {/* Agent Priority Queue (new — Module 12, replaces per-row view with group-level) */}
        {agentData && agentData.cases && agentData.cases.length > 0 && (
          <section>
            <AgentRecommendationCard
              cases={agentData.cases}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          </section>
        )}

        {/* Top Priority Remediation Deck (existing, relabeled) */}
        <section>
          <RemediationDeck offenders={top_offenders} />
        </section>

        {/* Human Review Queue (existing, relabeled from Exceptions & Ambiguities) */}
        <section>
          <ExceptionsDrawer exceptions={exceptions} />
        </section>

        {/* Full Ledger Audit Trail */}
        <section>
          <AuditTrailTable rows={auditRows} />
        </section>
      </main>
    </div>
  );
}