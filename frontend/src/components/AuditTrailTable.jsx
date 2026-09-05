import React, { useState, useMemo } from "react";
import { 
  Download, 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  FileSpreadsheet 
} from "lucide-react";

const RULE_METADATA = {
  R1: "Bank UPI (0% Statutory Cap)",
  R2: "RuPay Debit (0% Statutory Cap)",
  R3: "RuPay Credit UPI ≤ ₹2k (0% Cap)",
  R4: "RuPay Credit UPI > ₹2k (1.5% Cap)",
  R5: "PPI Wallet UPI ≤ ₹2k (0% Cap)",
  R6b: "PPI Wallet UPI > ₹2k (0.5% Cap)",
  R8: "Non-RuPay Debit (RBI ₹1k Cap)",
  R9: "Credit Card Rate (Unverified Tier)",
  R10: "L2/L3 Downgrade Penalty",
  R11: "Blended Flat-Rate Spread",
  R12: "MCC Rate Misalignment",
};

const FILTER_TABS = [
  { id: "ALL", label: "All Records" },
  { id: "Leaked", label: "Fee Leaks" },
  { id: "Matched", label: "Compliant" },
  { id: "Flagged_For_Review", label: "Flagged for Review" },
  { id: "Exception", label: "Exceptions" },
];

const formatSubInstrument = (val) => {
  if (!val) return <span className="text-amber-600 dark:text-amber-400 italic">Missing Tag</span>;
  const mapping = {
    bank_UPI: "Bank UPI",
    RuPay_debit: "RuPay Debit",
    RuPay_credit_UPI: "RuPay Credit (UPI)",
    PPI_wallet_UPI: "PPI Wallet (UPI)",
    Visa_credit: "Visa Credit",
    Mastercard_credit: "Mastercard Credit",
    Debit_non_rupay: "Non-RuPay Debit",
  };
  return mapping[val] || val.replace(/_/g, " ");
};

export default function AuditTrailTable({ rows = [] }) {
  const [filter, setFilter] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 25;

  // Filter and search logic
  const filteredRows = useMemo(() => {
    return rows.filter((r) => {
      const matchesFilter = filter === "ALL" || r.classification === filter;
      const term = searchTerm.toLowerCase();
      const matchesSearch =
        !searchTerm ||
        r.transaction_id?.toLowerCase().includes(term) ||
        r.matched_rule_id?.toLowerCase().includes(term) ||
        r.sub_instrument?.toLowerCase().includes(term) ||
        r.explanation?.toLowerCase().includes(term);

      return matchesFilter && matchesSearch;
    });
  }, [rows, filter, searchTerm]);

  // Pagination calculation
  const totalPages = Math.ceil(filteredRows.length / rowsPerPage) || 1;
  const paginatedRows = useMemo(() => {
    const start = (currentPage - 1) * rowsPerPage;
    return filteredRows.slice(start, start + rowsPerPage);
  }, [filteredRows, currentPage]);

  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
    setCurrentPage(1);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  // CSV Export Utility
  const exportToCSV = () => {
    if (!filteredRows || filteredRows.length === 0) return;

    const headers = Object.keys(filteredRows[0]);
    const csvRows = [
      headers.join(","),
      ...filteredRows.map((row) =>
        headers
          .map((header) => `"${String(row[header] ?? "").replace(/"/g, '""')}"`)
          .join(",")
      ),
    ];

    const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const timestamp = new Date().toISOString().split("T")[0];
    link.setAttribute("href", url);
    link.setAttribute("download", `interdrift_audit_trail_${timestamp}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getBadgeStyle = (status) => {
    switch (status) {
      case "Matched":
        return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";
      case "Leaked":
        return "bg-destructive/10 text-destructive dark:text-red-400 border-destructive/20";
      case "Exception":
        return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20";
      default:
        return "bg-primary/10 text-primary dark:text-primary-foreground border-primary/20";
    }
  };

  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-5">
      {/* Header & Export Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-border">
        <div>
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-primary"/>
            <h3 className="text-base font-bold text-foreground tracking-tight">
              Row-Level Audit Trail & Verification Ledger
            </h3>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Deterministic rule verifications accompanied by grounded diagnostic explanations
          </p>
        </div>

        <button
          onClick={exportToCSV}
          disabled={filteredRows.length === 0}
          className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-secondary hover:bg-muted border border-border text-foreground text-xs font-semibold tracking-wide transition-colors cursor-pointer shadow-sm self-start md:self-auto disabled:opacity-50"
        >
          <Download className="w-3.5 h-3.5 text-primary"/>
          <span>Export Filtered CSV ({filteredRows.length})</span>
        </button>
      </div>

      {/* Filter and Search Controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-muted-foreground"/>
          <input
            type="text"
            placeholder="Search by Txn ID, Rule, Rail, or Explanation..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-border bg-secondary/40 text-foreground text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        {/* Classification Filter Tabs */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {FILTER_TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleFilterChange(tab.id)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer shrink-0 border ${
                filter === tab.id
                  ? "bg-primary text-primary-foreground border-primary font-semibold"
                  : "bg-secondary text-muted-foreground border-border hover:text-foreground"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Ledger Table */}
      <div className="overflow-x-auto rounded-lg border border-border bg-card">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-secondary text-foreground/70 font-mono text-xs font-semibold uppercase border-b border-border">
            <tr>
              <th className="py-3 px-4">Txn ID</th>
              <th className="py-3 px-3">Classification</th>
              <th className="py-3 px-3">Rule & Citation</th>
              <th className="py-3 px-3">Payment Instrument</th>
              <th className="py-3 px-3 text-right">Amount</th>
              <th className="py-3 px-3 text-right">Fee Charged</th>
              <th className="py-3 px-3 text-right">Expected</th>
              <th className="py-3 px-3 text-right">Delta</th>
              <th className="py-3 px-4 min-w-[280px]">Diagnostic Explanation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60 font-mono text-foreground">
            {paginatedRows.length === 0 ? (
              <tr>
                <td colSpan={9} className="py-8 text-center text-muted-foreground font-sans text-sm">
                  No matching audit records found.
                </td>
              </tr>
            ) : (
              paginatedRows.map((row, idx) => {
                const ruleDesc = RULE_METADATA[row.matched_rule_id];

                return (
                  <tr key={idx} className="hover:bg-secondary/40 transition-colors">
                    <td className="py-3 px-4 font-bold text-foreground text-sm">
                      {row.transaction_id}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getBadgeStyle(row.classification)}`}>
                        {row.classification ? row.classification.replace(/_/g, " ") : "-"}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <div className="flex flex-col">
                        <span 
                          className="font-mono text-xs font-bold text-primary cursor-help"
                          title={ruleDesc ? `Rule ${row.matched_rule_id}: ${ruleDesc}` : `Rule ${row.matched_rule_id}`}
                        >
                          {row.matched_rule_id && row.matched_rule_id !== "NONE" ? `Rule ${row.matched_rule_id}` : "Unclassified"}
                        </span>
                        {ruleDesc && (
                          <span className="text-[10px] font-sans text-muted-foreground truncate max-w-[130px]">
                            {ruleDesc}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-3 text-foreground font-sans text-xs">
                      {formatSubInstrument(row.sub_instrument)}
                    </td>
                    <td className="py-3 px-3 text-right text-sm">
                      ₹{Number(row.amount || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-3 text-right text-sm">
                      ₹{Number(row.fee_charged || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-3 text-right text-muted-foreground text-sm">
                      ₹{Number(row.expected_fee || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 px-3 text-right font-bold text-destructive dark:text-red-400 text-sm">
                      {row.delta ? `+₹${Number(row.delta).toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "₹0.00"}
                    </td>
                    <td className="py-3 px-4 font-sans text-sm leading-relaxed text-foreground/90">
                      {row.explanation || row.note || "-"}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 text-xs text-muted-foreground font-mono">
        <div>
          Showing {filteredRows.length === 0 ? 0 : (currentPage - 1) * rowsPerPage + 1} to{" "}
          {Math.min(currentPage * rowsPerPage, filteredRows.length)} of {filteredRows.length} filtered items
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
            disabled={currentPage === 1}
            className="p-1.5 rounded-md border border-border bg-secondary hover:bg-muted disabled:opacity-40 cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4"/>
          </button>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
            disabled={currentPage === totalPages}
            className="p-1.5 rounded-md border border-border bg-secondary hover:bg-muted disabled:opacity-40 cursor-pointer"
          >
            <ChevronRight className="w-4 h-4"/>
          </button>
        </div>
      </div>
    </div>
  );
}
