export default function CategoryBreakdown({ categories = [] }) {
  const totalLeakage = categories.reduce((sum, item) => sum + (item.total_leaked || 0), 0);

  return (
    <div className="bg-surface border border-surfaceBorder rounded-xl p-6 shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Leakage by Rule Category</h2>
          <p className="text-xs text-gray-400 mt-0.5">Identified fee discrepancies grouped by regulatory and commercial rail</p>
        </div>
        <span className="text-xs font-mono text-gray-400 bg-gray-900 border border-gray-800 px-2.5 py-1 rounded">
          {categories.length} Categories
        </span>
      </div>

      <div className="space-y-4">
        {categories.map((cat, idx) => {
          const percentage = totalLeakage > 0 ? ((cat.total_leaked / totalLeakage) * 100).toFixed(1) : 0;

          return (
            <div key={idx} className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-medium text-gray-200">{cat.category.replace(/_/g, " ")}</span>
                <span className="text-gray-400 font-mono">
                  ₹{Number(cat.total_leaked).toLocaleString("en-IN", { minimumFractionDigits: 2 })} ({percentage}%)
                </span>
              </div>
              
              <div className="w-full bg-gray-900 h-2 rounded-full overflow-hidden border border-gray-800">
                <div
                  className="bg-accentRed h-full rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${Math.max(percentage, 3)}%` }}
                />
              </div>

              <div className="flex justify-end text-[11px] text-gray-500">
                <span>{cat.transaction_count} transactions impacted</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}