export default function TopOffenders({ offenders = [] }) {
  if (!offenders || offenders.length === 0) return null;

  return (
    <div className="bg-surface border border-surfaceBorder rounded-xl p-6 shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Top Leakage Offenders</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Highest-value fee discrepancies with deterministic deltas and LLM diagnostic remediation
          </p>
        </div>
        <span className="text-xs font-mono text-accentRed bg-red-950/40 border border-red-900/50 px-2.5 py-1 rounded">
          Priority Remediations
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {offenders.map((item, idx) => (
          <div
            key={idx}
            className="p-4 rounded-lg bg-gray-900/80 border border-gray-800 hover:border-gray-700 transition-colors flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between gap-2 border-b border-gray-800 pb-3 mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-white">{item.transaction_id}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                    Rule {item.rule_id}
                  </span>
                </div>
                <span className="text-xs font-mono font-bold text-accentRed">
                  +₹{Number(item.delta).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </span>
              </div>

              <p className="text-xs text-gray-300 leading-relaxed">
                {item.explanation || "Discrepancy detected between expected regulatory fee and amount deducted."}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-gray-800/60 flex items-center justify-between text-[11px] text-gray-500 font-mono">
              <span>Status: Leaked</span>
              <span>Action: Reclaim Delta</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}