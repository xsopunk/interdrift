export default function ExceptionsList({ exceptions = [] }) {
  if (!exceptions || exceptions.length === 0) return null;

  return (
    <div className="bg-surface border border-surfaceBorder rounded-xl p-6 shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Unclassified Exceptions</h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Transactions with incomplete or ambiguous metadata, displayed transparently rather than forced into classification
          </p>
        </div>
        <span className="text-xs font-mono text-amber-400 bg-amber-950/40 border border-amber-900/50 px-2.5 py-1 rounded">
          {exceptions.length} Items
        </span>
      </div>

      <div className="max-h-64 overflow-y-auto divide-y divide-gray-800/60 rounded-lg border border-gray-800 bg-gray-900/40">
        {exceptions.map((item, idx) => (
          <div key={idx} className="p-3 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="font-mono text-gray-300 font-medium">{item.transaction_id}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 border border-gray-700">
                Exception
              </span>
            </div>
            <span className="text-gray-400 text-right sm:text-left">
              {item.note || "Missing sub-instrument or conflicting metadata tag"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
