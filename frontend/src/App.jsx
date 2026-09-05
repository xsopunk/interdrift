import React, { useEffect, useState } from "react";
import { getFinalReport, getAuditTrailResults, getAgentCases, getControlEffectiveness, approveCase, rejectCase } from "./services/api";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
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
import AgentWorkflowTracker from "./components/AgentWorkflowTracker";
import TestDataModal from "./components/TestDataModal";
import { TrendingDown, CheckCircle2, AlertTriangle, Layers } from "lucide-react";

export default function App() {
  const [report, setReport] = useState(null);
  const [auditRows, setAuditRows] = useState([]);
  const [agentData, setAgentData] = useState(null);
  const [effectivenessData, setEffectivenessData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isTestDataModalOpen, setIsTestDataModalOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("overview");
  const [caseStatusFilter, setCaseStatusFilter] = useState("ALL");
  const [selectedCaseId, setSelectedCaseId] = useState(null);

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
    <div className="min-h-screen bg-background text-foreground relative selection:bg-primary selection:text-primary-foreground transition-colors duration-200 flex flex-col">
      {/* Aceternity Ambient Dot Patterning */}
      <div className="absolute inset-0 bg-dot-pattern opacity-35 pointer-events-none z-0" />

      {/* Top Navbar */}
      <Navbar 
        backendStatus="online" 
        rowCount={overview.total_transactions} 
        onOpenTestData={() => setIsTestDataModalOpen(true)}
      />

      {/* Main Container with Left Icon Sidebar */}
      <div className="flex flex-1 relative z-10">
        <Sidebar activeSection={activeSection} setActiveSection={setActiveSection} />

        <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 w-full overflow-x-hidden flex flex-col justify-center min-h-[calc(100vh-3.5rem)]">
          {/* Executive Overview & Operations Section */}
          {activeSection === "overview" && (
            <div className="space-y-4 animate-in fade-in duration-200 my-auto">
              {/* Top Operations Toolbar */}
              <section>
                <ControlCockpit onUploadSuccess={loadAllData} />
              </section>

              {/* Asymmetric 2-Column Dashboard Grid with Equal Height Alignment */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
                {/* Left Main Telemetry Stream (8 Columns - Flex Column for Perfect Bottom Alignment) */}
                <div className="lg:col-span-8 flex flex-col justify-between h-full gap-3.5">
                  {/* Compact Horizontal KPI Deck */}
                  <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
                    <MetricCard
                      title="Total Direct Leakage"
                      value={`₹${overview.total_leaked_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`}
                      subtitle={`${overview.leaked_count} txns (${overview.leaked_percent}%)`}
                      variant="destructive"
                      badge="Direct Loss"
                      icon={TrendingDown}
                      trendText={`${overview.leaked_percent}% batch loss`}
                    />
                    <MetricCard
                      title="Statutory Match Rate"
                      value={`${overview.matched_percent}%`}
                      subtitle={`${overview.matched_count} compliant`}
                      variant="success"
                      badge="Compliant"
                      icon={CheckCircle2}
                    />
                    <MetricCard
                      title="Contract Pricing Spread"
                      value={`₹${overview.structural_overcharge_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`}
                      subtitle="Flat vs true cost"
                      variant="warning"
                      badge="Pricing Audit"
                      icon={AlertTriangle}
                    />
                    <MetricCard
                      title="Exceptions & Flagged"
                      value={`${overview.exception_count + overview.flagged_for_review_count}`}
                      subtitle={`${overview.exception_count} unclassified`}
                      variant="primary"
                      badge="Transparency"
                      icon={Layers}
                    />
                  </section>

                  {/* Live Agent Workflow Tracker (Module 13 Orchestrator Stream) */}
                  <AgentWorkflowTracker agentData={agentData} report={report} />

                  {/* Batch Structural Audits (Horizontal in Main Stream - Aligned to Bottom) */}
                  <section>
                    <StructuralImpactCard
                      audits={report?.batch_structural_audits}
                      mccAmount={overview.mcc_misclassification_amount}
                      structuralAmount={overview.structural_overcharge_amount}
                    />
                  </section>
                </div>

                {/* Right Focus Side-Panel (4 Columns): Fee Leakage Vertical Breakdown */}
                <div className="lg:col-span-4 h-full">
                  <CategoryVisualizer categories={leak_by_category} />
                </div>
              </div>
            </div>
          )}

          {/* Agent & Governance Section */}
          {activeSection === "governance" && (
            <div className="space-y-8 animate-in fade-in duration-200">
              {agentData && agentData.summary && (
                <section>
                  <AgentControlStatus
                    summary={agentData.summary}
                    selectedStatus={caseStatusFilter}
                    onSelectStatus={setCaseStatusFilter}
                  />
                </section>
              )}

              {effectivenessData && effectivenessData.status === "computed" && (
                <section>
                  <ControlEffectivenessCard effectiveness={effectivenessData} />
                </section>
              )}

              {agentData && agentData.cases && agentData.cases.length > 0 && (
                <section>
                  <AgentRecommendationCard
                    cases={agentData.cases}
                    selectedStatusFilter={caseStatusFilter}
                    selectedCaseId={selectedCaseId}
                    onViewTransactions={(caseId) => {
                      setSelectedCaseId(caseId);
                      setActiveSection("remediation");
                    }}
                    onClearFilter={() => setCaseStatusFilter("ALL")}
                    onApprove={handleApprove}
                    onReject={handleReject}
                  />
                </section>
              )}
            </div>
          )}

          {/* Remediation & Review Section */}
          {activeSection === "remediation" && (
            <div className="space-y-8 animate-in fade-in duration-200">
              <section>
                <RemediationDeck
                  offenders={top_offenders}
                  cases={agentData?.cases || []}
                  selectedCaseId={selectedCaseId}
                  onClearCaseFilter={() => setSelectedCaseId(null)}
                  onGoToCase={(caseId) => {
                    setSelectedCaseId(caseId);
                    setActiveSection("governance");
                  }}
                />
              </section>

              <section>
                <ExceptionsDrawer exceptions={exceptions} />
              </section>
            </div>
          )}

          {/* Audit Ledger Section */}
          {activeSection === "audit" && (
            <div className="space-y-8 animate-in fade-in duration-200">
              <section>
                <AuditTrailTable rows={auditRows} />
              </section>
            </div>
          )}
        </main>
      </div>

      {/* Synthetic Test Data & Contract Modal */}
      <TestDataModal
        isOpen={isTestDataModalOpen}
        onClose={() => setIsTestDataModalOpen(false)}
        onAuditSuccess={loadAllData}
      />
    </div>
  );
}