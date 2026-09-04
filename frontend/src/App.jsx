import { useEffect, useState } from "react";
import { getFinalReport, getAuditTrailResults } from "./services/api";
import KPICard from "./components/KPICard";
import CategoryBreakdown from "./components/CategoryBreakdown";
import TopOffenders from "./components/TopOffenders";
import ExceptionsList from "./components/ExceptionsList";
import AuditTrailTable from "./components/AuditTrailTable";
import UploadModal from "./components/UploadModal";

export default function App() {
  const [report, setReport] = useState(null);
  const [auditRows, setAuditRows] = useState([]);
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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-gray-400 animate-pulse text-sm">Loading InterDrift audit intelligence...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="bg-surface border border-red-500/30 p-6 rounded-xl max-w-md w-full">
          <h2 className="text-red-400 font-bold text-base">Unable to connect to backend</h2>
          <p className="text-xs text-gray-400 mt-2">{error}</p>
          <p className="text-[11px] text-gray-500 mt-4">Verify FastAPI is running on http://127.0.0.1:8000</p>
        </div>
      </div>
    );
  }

  const { overview, leak_by_category } = report;

  return (
    <div className="min-h-screen bg-background text-gray-100 p-6 lg:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-surfaceBorder pb-6 gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold tracking-tight text-white">InterDrift</h1>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                Track 4: AI Finance Controller
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Autonomous interchange & MDR reconciliation engine with deterministic grounding
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            Audited Batch: {overview.total_transactions} Rows
          </div>
        </header>

        {/* Upload Settlement Trigger */}
        <UploadModal onUploadSuccess={loadAllData} />

        {/* Top-Line KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Total Direct Leakage"
            value={`₹${overview.total_leaked_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`}
            subtitle={`${overview.leaked_count} transactions (${overview.leaked_percent}%)`}
            highlightColor="accentRed"
            badge="Action Required"
          />
          <KPICard
            title="Compliance Match Rate"
            value={`${overview.matched_percent}%`}
            subtitle={`${overview.matched_count} compliant charges`}
            highlightColor="accentGreen"
            badge="Healthy"
          />
          <KPICard
            title="Structural Overcharge"
            value={`₹${overview.structural_overcharge_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`}
            subtitle="Blended-MDR vs IC+ baseline spread"
            highlightColor="accentAmber"
            badge="Aggregate R11"
          />
          <KPICard
            title="Exceptions & Flagged"
            value={`${overview.exception_count + overview.flagged_for_review_count}`}
            subtitle={`${overview.exception_count} unclassified · ${overview.flagged_for_review_count} review`}
            highlightColor="accentCyan"
            badge="Honest Audit"
          />
        </div>

        {/* Category Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <CategoryBreakdown categories={leak_by_category} />
          </div>
          <div className="bg-surface border border-surfaceBorder rounded-xl p-6 flex flex-col justify-between">
            <div>
              <h3 className="text-base font-bold text-white mb-2">MCC Misclassification Cost</h3>
              <p className="text-xs text-gray-400 leading-relaxed">
                Transactions routed under generic retail MCC rather than specialized enterprise merchant categories generate structural fee slippage.
              </p>
              <div className="mt-6 p-4 rounded-lg bg-gray-900 border border-gray-800">
                <span className="text-xs text-gray-500 uppercase font-medium">Quantified R12 Impact</span>
                <p className="text-2xl font-bold text-amber-400 mt-1">
                  ₹{overview.mcc_misclassification_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>
            <div className="text-[11px] text-gray-500 border-t border-gray-800 pt-4 mt-6">
              Derived deterministically via Layer 1 batch auditing.
            </div>
          </div>
        </div>

        {/* Top Offenders & Remediation Stories */}
        <TopOffenders offenders={report.top_offenders} />

        {/* Honest Exceptions Section */}
        <ExceptionsList exceptions={report.exceptions} />

        {/* Full Audit Trail Data Table & CSV Export */}
        <AuditTrailTable rows={auditRows} />
      </div>
    </div>
  );
}