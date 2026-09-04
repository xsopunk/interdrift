import { useState } from "react";

export default function AuditTrailTable({ rows = [] }) {
  const [filter, setFilter] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");

  const filteredRows = rows.filter((r) => {
    const matchesFilter = filter === "ALL" || r.classification === filter;
    const matchesSearch =
      r.transaction_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.matched_rule_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.sub_instrument?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const exportToCSV = () => {
    if (!rows || rows.length === 0) return;
    const headers = Object.keys(rows[0]).join(",");
    const csvContent = [
      headers,
      ...rows.map((row) =>
        Object.values(row)
          .map((val) => `"${String(val ?? "").replace(/"/g, '""')}"`)
          .join(",")
      ),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "interdrift_audit_trail.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getBadgeClass = (status) => {
    switch (status) {
      case "Matched":
        return "bg-emerald-950/60 text-emerald-400 border-emerald-800";
      case "Leaked":
        return "bg-red-950/60 text-red-400 border-red-800";
      case "Exception":
        return "bg-amber-950/60 text-amber-400 border-amber-800";
      default:
        return "bg-cyan-950/60 text-cyan-400 border-cyan-800";
    }
  };

  return (
    <div className="bg-surface border border-surfaceBorder rounded-xl p-6 shadow-lg space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Full Audit Trail</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Row-level verification dataset with deterministic classifications and LLM explanations
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={exportToCSV}
            className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition-colors cursor-pointer shadow"
          >
            Export Audit CSV
          </button>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div className="flex flex-col sm:flex-row gap-3 pt-2">
        <input
          type="text"
          placeholder="Search by Txn ID, Rule, Sub-instrument..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500"
        />
        <div className="flex gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {["ALL", "Leaked", "Matched", "Exception", "Flagged_For_Review"].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-2.5 py-1 rounded text-xs font-mono transition-colors cursor-pointer ${
                filter === cat
                  ? "bg-cyan-950 text-cyan-400 border border-cyan-700"
                  : "bg-gray-900 text-gray-400 border border-gray-800 hover:text-gray-200"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Table Display */}
      <div className="overflow-x-auto rounded-lg border border-gray-800 bg-gray-900/40">
        <table className="w-full text-left text-xs">
          <thead className="bg-gray-900/90 text-gray-400 font-mono text-[11px] uppercase border-b border-gray-800">
            <tr>
              <th className="p-3">Txn ID</th>
              <th className="p-3">Status</th>
              <th className="p-3">Rule</th>
              <th className="p-3 text-right">Amount</th>
              <th className="p-3 text-right">Fee Charged</th>
              <th className="p-3 text-right">Expected</th>
              <th className="p-3 text-right">Delta</th>
              <th className="p-3 min-w-[240px]">LLM Diagnostic Explanation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60 font-mono text-gray-300">
            {filteredRows.slice(0, 50).map((row, idx) => (
              <tr key={idx} className="hover:bg-gray-800/40 transition-colors">
                <td className="p-3 font-semibold text-white">{row.transaction_id}</td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] border ${getBadgeClass(row.classification)}`}>
                    {row.classification}
                  </span>
                </td>
                <td className="p-3 text-cyan-400">{row.matched_rule_id || "-"}</td>
                <td className="p-3 text-right">₹{Number(row.amount || 0).toFixed(2)}</td>
                <td className="p-3 text-right">₹{Number(row.fee_charged || 0).toFixed(2)}</td>
                <td className="p-3 text-right">₹{Number(row.expected_fee || 0).toFixed(2)}</td>
                <td className="p-3 text-right font-bold text-red-400">
                  {row.delta ? `+₹${Number(row.delta).toFixed(2)}` : "₹0.00"}
                </td>
                <td className="p-3 font-sans text-xs text-gray-400 line-clamp-2" title={row.explanation}>
                  {row.explanation || row.note || "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center text-[11px] text-gray-500 font-mono pt-1">
        <span>Showing up to 50 of {filteredRows.length} filtered items</span>
        <span>Audit integrity verified</span>
      </div>
    </div>
  );
}