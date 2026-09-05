import React, { useState } from "react";
import { 
  X, 
  FlaskConical, 
  Database, 
  FileText, 
  UploadCloud, 
  Play, 
  AlertCircle, 
  CheckCircle2, 
  Info,
  ChevronLeft,
  ChevronRight,
  Sliders
} from "lucide-react";
import { 
  previewGeneratedDataset, 
  previewGeneratedMSA, 
  uploadCustomCSV, 
  uploadCustomMSA, 
  activateAuditData 
} from "../services/api";

export default function TestDataModal({ isOpen, onClose, onAuditSuccess }) {
  const [activeTab, setActiveTab] = useState("dataset"); // "dataset" | "msa"

  // Dataset Generator State
  const [datasetMode, setDatasetMode] = useState("generated"); // "generated" | "uploaded"
  const [numTransactions, setNumTransactions] = useState(500);
  const [minAmount, setMinAmount] = useState(50);
  const [maxAmount, setMaxAmount] = useState(100000);
  const [rupayCreditLeakRate, setRupayCreditLeakRate] = useState(15);
  const [l2l3DowngradeRate, setL2l3DowngradeRate] = useState(12);
  const [mccMisclassRate, setMccMisclassRate] = useState(10);
  const [exceptionRate, setExceptionRate] = useState(5);

  const [datasetPreview, setDatasetPreview] = useState(null);
  const [datasetLoading, setDatasetLoading] = useState(false);
  const [datasetError, setDatasetError] = useState(null);

  // Custom CSV Upload State
  const [uploadedCsvFile, setUploadedCsvFile] = useState(null);
  const [uploadedCsvInfo, setUploadedCsvInfo] = useState(null);
  const [csvUploadLoading, setCsvUploadLoading] = useState(false);

  // MSA Generator State
  const [msaMode, setMsaMode] = useState("generated"); // "generated" | "uploaded"
  const [businessCategory, setBusinessCategory] = useState("B2B wholesale");
  const [turnoverTier, setTurnoverTier] = useState("above_20L");
  const [contractedFlatRate, setContractedFlatRate] = useState(2.0);
  const [msaPreview, setMsaPreview] = useState(null);
  const [msaLoading, setMsaLoading] = useState(false);
  const [msaError, setMsaError] = useState(null);

  // Custom MSA Upload State
  const [uploadedMsaFile, setUploadedMsaFile] = useState(null);
  const [uploadedMsaData, setUploadedMsaData] = useState(null);
  const [msaUploadLoading, setMsaUploadLoading] = useState(false);

  // Activation State
  const [activating, setActivating] = useState(false);
  const [activationError, setActivationError] = useState(null);

  // Preview Pagination
  const [previewPage, setPreviewPage] = useState(1);
  const rowsPerPage = 5;

  if (!isOpen) return null;

  // Generate Dataset Preview
  const handleGenerateDatasetPreview = async () => {
    try {
      setDatasetLoading(true);
      setDatasetError(null);
      const config = {
        num_transactions: Number(numTransactions),
        min_amount: Number(minAmount),
        max_amount: Number(maxAmount),
        rupay_credit_leak_rate: rupayCreditLeakRate / 100,
        l2_l3_downgrade_rate: l2l3DowngradeRate / 100,
        mcc_misclass_rate: mccMisclassRate / 100,
        exception_rate: exceptionRate / 100,
        msa: msaPreview || (msaMode === "uploaded" ? uploadedMsaData : null),
      };
      const res = await previewGeneratedDataset(config);
      setDatasetPreview(res);
      setPreviewPage(1);
    } catch (err) {
      setDatasetError(err.message || "Failed to generate dataset preview");
    } finally {
      setDatasetLoading(false);
    }
  };

  // Upload Custom CSV
  const handleCsvFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setCsvUploadLoading(true);
      setDatasetError(null);
      const res = await uploadCustomCSV(file);
      setUploadedCsvFile(file);
      setUploadedCsvInfo(res);
      setDatasetMode("uploaded");
      setDatasetPreview(null);
    } catch (err) {
      setDatasetError(err.message || "CSV validation failed");
      setUploadedCsvFile(null);
      setUploadedCsvInfo(null);
    } finally {
      setCsvUploadLoading(false);
    }
  };

  // Generate MSA Preview
  const handleGenerateMSAPreview = async () => {
    try {
      setMsaLoading(true);
      setMsaError(null);
      const config = {
        business_category: businessCategory,
        annual_turnover_tier: turnoverTier,
        cards_flat_blended: contractedFlatRate / 100,
      };
      const res = await previewGeneratedMSA(config);
      setMsaPreview(res.msa);
    } catch (err) {
      setMsaError(err.message || "Failed to generate MSA preview");
    } finally {
      setMsaLoading(false);
    }
  };

  // Upload Custom MSA JSON
  const handleMsaFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setMsaUploadLoading(true);
      setMsaError(null);
      const res = await uploadCustomMSA(file);
      setUploadedMsaFile(file);
      setUploadedMsaData(res.msa);
      setMsaMode("uploaded");
      setMsaPreview(res.msa);
    } catch (err) {
      setMsaError(err.message || "MSA JSON validation failed");
      setUploadedMsaFile(null);
      setUploadedMsaData(null);
    } finally {
      setMsaUploadLoading(false);
    }
  };

  // Run Audit With Active Data
  const handleRunAudit = async () => {
    try {
      setActivating(true);
      setActivationError(null);

      const payload = {
        dataset_mode: datasetMode,
        dataset_config: datasetMode === "generated" ? {
          num_transactions: Number(numTransactions),
          min_amount: Number(minAmount),
          max_amount: Number(maxAmount),
          rupay_credit_leak_rate: rupayCreditLeakRate / 100,
          l2_l3_downgrade_rate: l2l3DowngradeRate / 100,
          mcc_misclass_rate: mccMisclassRate / 100,
          exception_rate: exceptionRate / 100,
        } : null,
        uploaded_csv_filename: datasetMode === "uploaded" && uploadedCsvInfo ? uploadedCsvInfo.filename : null,
        msa_mode: msaMode,
        msa_data: msaMode === "uploaded" ? uploadedMsaData : (msaPreview || null),
      };

      await activateAuditData(payload);
      if (onAuditSuccess) {
        await onAuditSuccess();
      }
      onClose();
    } catch (err) {
      setActivationError(err.message || "Audit activation failed");
    } finally {
      setActivating(false);
    }
  };

  // Fallback notices
  const hasCustomDataset = datasetMode === "uploaded" ? !!uploadedCsvFile : !!datasetPreview;
  const hasCustomMSA = msaMode === "uploaded" ? !!uploadedMsaData : !!msaPreview;

  // Pagination for dataset preview rows
  const previewRows = datasetPreview?.preview_rows || [];
  const totalPreviewPages = Math.ceil(previewRows.length / rowsPerPage) || 1;
  const paginatedPreviewRows = previewRows.slice((previewPage - 1) * rowsPerPage, previewPage * rowsPerPage);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-muted/40">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-primary/10 text-primary border border-primary/20">
              <FlaskConical className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-foreground">Synthetic Test Data & Contract Workbench</h2>
              <p className="text-xs text-muted-foreground">
                Configure synthetic payment streams, test regulatory edge-cases, or upload custom contracts
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/80 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-border px-6 pt-2 bg-muted/20">
          <button
            onClick={() => setActiveTab("dataset")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all ${
              activeTab === "dataset"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <Database className="w-4 h-4" />
            <span>Dataset Generator</span>
          </button>
          <button
            onClick={() => setActiveTab("msa")}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all ${
              activeTab === "msa"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Merchant Agreement (MSA)</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
          
          {/* TAB 1: DATASET GENERATOR */}
          {activeTab === "dataset" && (
            <div className="space-y-5">
              {/* Mode Toggle & Custom Upload */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-lg border border-border bg-muted/30">
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setDatasetMode("generated")}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                      datasetMode === "generated" 
                        ? "bg-primary text-primary-foreground shadow-sm" 
                        : "bg-background text-muted-foreground hover:text-foreground border border-border"
                    }`}
                  >
                    Generate Synthetic Data
                  </button>
                  <button
                    type="button"
                    onClick={() => setDatasetMode("uploaded")}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                      datasetMode === "uploaded" 
                        ? "bg-primary text-primary-foreground shadow-sm" 
                        : "bg-background text-muted-foreground hover:text-foreground border border-border"
                    }`}
                  >
                    Upload Own CSV
                  </button>
                </div>

                {datasetMode === "uploaded" ? (
                  <div className="flex items-center gap-2">
                    <input
                      type="file"
                      accept=".csv"
                      onChange={handleCsvFileChange}
                      className="text-[11px] text-muted-foreground file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-[11px] file:font-medium file:bg-primary/10 file:text-primary hover:file:bg-primary/20 cursor-pointer"
                    />
                    {csvUploadLoading && <span className="text-[11px] text-muted-foreground animate-pulse">Validating...</span>}
                  </div>
                ) : (
                  <span className="text-[11px] text-muted-foreground italic">
                    Configuring live generator parameters
                  </span>
                )}
              </div>

              {/* Uploaded CSV Success Banner */}
              {datasetMode === "uploaded" && uploadedCsvInfo && (
                <div className="flex items-center gap-2.5 p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  <span className="text-xs">
                    Validated <strong>{uploadedCsvInfo.filename}</strong> ({uploadedCsvInfo.total_rows} rows). Ready for audit.
                  </span>
                </div>
              )}

              {/* Generator Parameter Sliders */}
              {datasetMode === "generated" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {/* Transactions Count */}
                    <div className="p-3 rounded-lg border border-border bg-card space-y-1.5">
                      <div className="flex justify-between items-center text-xs font-medium">
                        <span>Transactions Count</span>
                        <span className="font-mono text-primary font-bold">{numTransactions}</span>
                      </div>
                      <input
                        type="range"
                        min="10"
                        max="1500"
                        step="10"
                        value={numTransactions}
                        onChange={(e) => setNumTransactions(Number(e.target.value))}
                        className="w-full accent-primary cursor-pointer"
                      />
                    </div>

                    {/* Min Amount */}
                    <div className="p-3 rounded-lg border border-border bg-card space-y-1.5">
                      <div className="flex justify-between items-center text-xs font-medium">
                        <span>Min Amount</span>
                        <span className="font-mono text-primary font-bold">₹{minAmount}</span>
                      </div>
                      <input
                        type="range"
                        min="10"
                        max="5000"
                        step="10"
                        value={minAmount}
                        onChange={(e) => setMinAmount(Number(e.target.value))}
                        className="w-full accent-primary cursor-pointer"
                      />
                    </div>

                    {/* Max Amount (Up to 100,000) */}
                    <div className="p-3 rounded-lg border border-border bg-card space-y-1.5">
                      <div className="flex justify-between items-center text-xs font-medium">
                        <span>Max Amount (Up to ₹1L)</span>
                        <span className="font-mono text-primary font-bold">₹{maxAmount.toLocaleString("en-IN")}</span>
                      </div>
                      <input
                        type="range"
                        min="5000"
                        max="100000"
                        step="1000"
                        value={maxAmount}
                        onChange={(e) => setMaxAmount(Number(e.target.value))}
                        className="w-full accent-primary cursor-pointer"
                      />
                    </div>
                  </div>

                  {/* Leak Injection Rates with Plain English Labels */}
                  <div className="p-4 rounded-lg border border-border bg-card space-y-3">
                    <div className="flex items-center gap-1.5 font-semibold text-xs text-foreground">
                      <Sliders className="w-3.5 h-3.5 text-primary" />
                      <span>Injected Leakage & Anomaly Rates</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                      {/* RuPay Credit Leak Rate */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-muted-foreground">RuPay Credit-on-UPI Leak Rate</span>
                          <span className="font-mono font-bold text-foreground">{rupayCreditLeakRate}%</span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="40"
                          value={rupayCreditLeakRate}
                          onChange={(e) => setRupayCreditLeakRate(Number(e.target.value))}
                          className="w-full accent-primary cursor-pointer"
                        />
                      </div>

                      {/* L2/L3 Downgrade Rate */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-muted-foreground">L2/L3 Corporate Card Downgrade Rate</span>
                          <span className="font-mono font-bold text-foreground">{l2l3DowngradeRate}%</span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="40"
                          value={l2l3DowngradeRate}
                          onChange={(e) => setL2l3DowngradeRate(Number(e.target.value))}
                          className="w-full accent-primary cursor-pointer"
                        />
                      </div>

                      {/* MCC Misclass Rate */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-muted-foreground">MCC Misclassification Rate</span>
                          <span className="font-mono font-bold text-foreground">{mccMisclassRate}%</span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="30"
                          value={mccMisclassRate}
                          onChange={(e) => setMccMisclassRate(Number(e.target.value))}
                          className="w-full accent-primary cursor-pointer"
                        />
                      </div>

                      {/* Exception Missing Sub-instrument Rate */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-muted-foreground">Unclassified Sub-Instrument Exception Rate</span>
                          <span className="font-mono font-bold text-foreground">{exceptionRate}%</span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="25"
                          value={exceptionRate}
                          onChange={(e) => setExceptionRate(Number(e.target.value))}
                          className="w-full accent-primary cursor-pointer"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Generate Preview Action */}
                  <div className="flex justify-end">
                    <button
                      type="button"
                      disabled={datasetLoading}
                      onClick={handleGenerateDatasetPreview}
                      className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-secondary hover:bg-muted text-foreground font-medium text-xs border border-border transition-colors cursor-pointer"
                    >
                      <FlaskConical className="w-3.5 h-3.5 text-primary" />
                      <span>{datasetLoading ? "Simulating Transactions..." : "Generate Preview Table"}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Dataset Error Alert */}
              {datasetError && (
                <div className="flex items-center gap-2 p-3 rounded-lg border border-destructive/40 bg-destructive/10 text-destructive">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span className="text-xs">{datasetError}</span>
                </div>
              )}

              {/* Tabulated Dataset Preview (Reusing AuditTrailTable styling) */}
              {datasetPreview && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>
                      Generated <strong>{datasetPreview.summary.total_records}</strong> transactions · Total Volume: <strong>₹{datasetPreview.summary.total_volume_inr.toLocaleString("en-IN")}</strong>
                    </span>
                    <span className="text-[11px]">
                      Avg Ticket: ₹{datasetPreview.summary.avg_amount}
                    </span>
                  </div>

                  <div className="border border-border rounded-xl bg-card overflow-hidden shadow-sm">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse text-xs">
                        <thead>
                          <tr className="bg-muted/50 border-b border-border text-[11px] font-mono uppercase text-muted-foreground">
                            <th className="py-2.5 px-3">Txn ID</th>
                            <th className="py-2.5 px-3">Sub-Instrument</th>
                            <th className="py-2.5 px-3 text-right">Amount</th>
                            <th className="py-2.5 px-3 text-right">Fee Charged</th>
                            <th className="py-2.5 px-3">MCC</th>
                            <th className="py-2.5 px-3">Simulated Issue</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border/50">
                          {paginatedPreviewRows.map((row) => (
                            <tr key={row.transaction_id} className="hover:bg-muted/30 transition-colors">
                              <td className="py-2 px-3 font-mono text-[11px] text-foreground">{row.transaction_id}</td>
                              <td className="py-2 px-3 font-mono text-[11px] text-muted-foreground">{row.sub_instrument || "(missing)"}</td>
                              <td className="py-2 px-3 font-mono text-[11px] text-right text-foreground font-semibold">
                                ₹{Number(row.amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                              </td>
                              <td className="py-2 px-3 font-mono text-[11px] text-right text-foreground">
                                ₹{Number(row.fee_charged).toFixed(2)}
                              </td>
                              <td className="py-2 px-3 font-mono text-[11px] text-muted-foreground">{row.mcc}</td>
                              <td className="py-2 px-3 font-mono text-[11px]">
                                <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                                  row.injected_issue === "clean" 
                                    ? "bg-emerald-500/10 text-emerald-500" 
                                    : "bg-amber-500/10 text-amber-500"
                                }`}>
                                  {row.injected_issue}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Preview Table Pagination */}
                    <div className="flex items-center justify-between px-4 py-2 border-t border-border text-xs text-muted-foreground bg-muted/10">
                      <span>Showing page {previewPage} of {totalPreviewPages}</span>
                      <div className="flex items-center gap-1">
                        <button
                          disabled={previewPage <= 1}
                          onClick={() => setPreviewPage(p => p - 1)}
                          className="p-1 rounded hover:bg-muted disabled:opacity-40 cursor-pointer"
                        >
                          <ChevronLeft className="w-4 h-4" />
                        </button>
                        <button
                          disabled={previewPage >= totalPreviewPages}
                          onClick={() => setPreviewPage(p => p + 1)}
                          className="p-1 rounded hover:bg-muted disabled:opacity-40 cursor-pointer"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: MSA GENERATOR */}
          {activeTab === "msa" && (
            <div className="space-y-5">
              {/* Mode Toggle & Custom Upload */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-lg border border-border bg-muted/30">
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setMsaMode("generated")}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                      msaMode === "generated" 
                        ? "bg-primary text-primary-foreground shadow-sm" 
                        : "bg-background text-muted-foreground hover:text-foreground border border-border"
                    }`}
                  >
                    Generate Synthetic MSA
                  </button>
                  <button
                    type="button"
                    onClick={() => setMsaMode("uploaded")}
                    className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                      msaMode === "uploaded" 
                        ? "bg-primary text-primary-foreground shadow-sm" 
                        : "bg-background text-muted-foreground hover:text-foreground border border-border"
                    }`}
                  >
                    Upload Own MSA JSON
                  </button>
                </div>

                {msaMode === "uploaded" ? (
                  <div className="flex items-center gap-2">
                    <input
                      type="file"
                      accept=".json"
                      onChange={handleMsaFileChange}
                      className="text-[11px] text-muted-foreground file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-[11px] file:font-medium file:bg-primary/10 file:text-primary hover:file:bg-primary/20 cursor-pointer"
                    />
                    {msaUploadLoading && <span className="text-[11px] text-muted-foreground animate-pulse">Validating...</span>}
                  </div>
                ) : (
                  <span className="text-[11px] text-muted-foreground italic">
                    Configuring merchant contract parameters
                  </span>
                )}
              </div>

              {/* Uploaded MSA Success Banner */}
              {msaMode === "uploaded" && uploadedMsaData && (
                <div className="flex items-center gap-2.5 p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                  <span className="text-xs">
                    Validated MSA for <strong>{uploadedMsaData.merchant_name || uploadedMsaData.merchant_id}</strong>. Ready for audit.
                  </span>
                </div>
              )}

              {/* Generator Fields */}
              {msaMode === "generated" && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {/* Business Category */}
                  <div className="p-3 rounded-lg border border-border bg-card space-y-1.5">
                    <label className="block text-xs font-medium text-foreground">Business Category</label>
                    <select
                      value={businessCategory}
                      onChange={(e) => setBusinessCategory(e.target.value)}
                      className="w-full py-1.5 px-2.5 rounded-md border border-border bg-background text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    >
                      <option value="B2B wholesale">B2B Wholesale (MCC 5045)</option>
                      <option value="retail">Retail Supermarket (MCC 5411)</option>
                      <option value="education">Higher Education (MCC 8220)</option>
                      <option value="restaurant">Restaurant (MCC 5812)</option>
                    </select>
                  </div>

                  {/* Turnover Tier */}
                  <div className="p-3 rounded-lg border border-border bg-card space-y-1.5">
                    <label className="block text-xs font-medium text-foreground">Annual Turnover Tier</label>
                    <select
                      value={turnoverTier}
                      onChange={(e) => setTurnoverTier(e.target.value)}
                      className="w-full py-1.5 px-2.5 rounded-md border border-border bg-background text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                    >
                      <option value="above_20L">Large Merchant (&gt; ₹20 Lakhs)</option>
                      <option value="below_20L">Small Merchant (≤ ₹20 Lakhs)</option>
                    </select>
                  </div>

                  {/* Contracted Flat Blended Rate */}
                  <div className="p-3 rounded-lg border border-border bg-card space-y-1.5">
                    <div className="flex justify-between items-center text-xs font-medium">
                      <span>Cards Blended Rate</span>
                      <span className="font-mono text-primary font-bold">{contractedFlatRate}%</span>
                    </div>
                    <input
                      type="range"
                      min="1.0"
                      max="3.5"
                      step="0.1"
                      value={contractedFlatRate}
                      onChange={(e) => setContractedFlatRate(Number(e.target.value))}
                      className="w-full accent-primary cursor-pointer"
                    />
                  </div>
                </div>
              )}

              {/* Generate MSA Preview Action */}
              {msaMode === "generated" && (
                <div className="flex justify-end">
                  <button
                    type="button"
                    disabled={msaLoading}
                    onClick={handleGenerateMSAPreview}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-secondary hover:bg-muted text-foreground font-medium text-xs border border-border transition-colors cursor-pointer"
                  >
                    <FileText className="w-3.5 h-3.5 text-primary" />
                    <span>{msaLoading ? "Generating MSA..." : "Preview Contract Terms"}</span>
                  </button>
                </div>
              )}

              {/* MSA Error Alert */}
              {msaError && (
                <div className="flex items-center gap-2 p-3 rounded-lg border border-destructive/40 bg-destructive/10 text-destructive">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span className="text-xs">{msaError}</span>
                </div>
              )}

              {/* MSA Preview Card */}
              {(msaPreview || uploadedMsaData) && (
                <div className="p-4 rounded-xl border border-border bg-card space-y-3 shadow-sm">
                  <div className="flex items-center justify-between border-b border-border pb-2.5">
                    <span className="font-semibold text-foreground text-xs">Active Contract Terms Specification</span>
                    <span className="px-2 py-0.5 rounded bg-primary/10 text-primary font-mono text-[10px] uppercase font-bold">
                      {(msaPreview || uploadedMsaData).pricing_model || "blended_mdr"}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px]">
                    <div>
                      <span className="text-muted-foreground block text-[10px]">Merchant ID</span>
                      <span className="font-mono font-medium text-foreground">{(msaPreview || uploadedMsaData).merchant_id}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[10px]">Category & Expected MCC</span>
                      <span className="font-medium text-foreground">
                        {(msaPreview || uploadedMsaData).registered_business_type} ({(msaPreview || uploadedMsaData).expected_mcc})
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[10px]">Turnover Tier</span>
                      <span className="font-medium text-foreground">{(msaPreview || uploadedMsaData).annual_turnover_tier}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[10px]">Contracted Card MDR</span>
                      <span className="font-mono font-bold text-primary">
                        {(((msaPreview || uploadedMsaData).contracted_rates?.cards_flat_blended || 0.02) * 100).toFixed(1)}% + GST
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer & Audit Trigger */}
        <div className="p-4 border-t border-border bg-muted/30 flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Default Fallback Notice Banner */}
          <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
            <Info className="w-3.5 h-3.5 text-primary flex-shrink-0" />
            <span>
              {!hasCustomDataset && !hasCustomMSA
                ? "Notice: Using default benchmark dataset and default MSA specification."
                : !hasCustomDataset
                ? "Notice: Custom MSA active. Using default benchmark dataset."
                : !hasCustomMSA
                ? "Notice: Custom dataset active. Using default MSA specification."
                : "Active: Both custom dataset and custom MSA configured."}
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
            <button
              type="button"
              onClick={onClose}
              disabled={activating}
              className="px-3.5 py-1.5 rounded-lg border border-border bg-background hover:bg-muted text-xs font-medium transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              disabled={activating}
              onClick={handleRunAudit}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-semibold shadow-sm transition-all cursor-pointer disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{activating ? "Auditing Pipeline..." : "Run Audit with This Data"}</span>
            </button>
          </div>
        </div>

        {/* Activation Error Alert */}
        {activationError && (
          <div className="px-6 py-2 bg-destructive/10 border-t border-destructive/20 text-destructive text-[11px] flex items-center gap-2">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>{activationError}</span>
          </div>
        )}

      </div>
    </div>
  );
}
