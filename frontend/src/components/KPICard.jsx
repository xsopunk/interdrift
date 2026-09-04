export default function KPICard({ title, value, subtitle, highlightColor = "accentCyan", badge }) {
  const colorMap = {
    accentCyan: "border-cyan-500/20 text-cyan-400",
    accentRed: "border-red-500/20 text-red-400",
    accentAmber: "border-amber-500/20 text-amber-400",
    accentGreen: "border-emerald-500/20 text-emerald-400",
  };

  return (
    <div className="bg-surface border border-surfaceBorder rounded-xl p-5 shadow-lg relative overflow-hidden">
      <div className="flex justify-between items-start">
        <span className="text-xs uppercase font-semibold tracking-wider text-gray-400">{title}</span>
        {badge && (
          <span className="text-[11px] px-2 py-0.5 rounded-full font-medium bg-gray-800 text-gray-300 border border-gray-700">
            {badge}
          </span>
        )}
      </div>
      <div className={`mt-3 text-2xl lg:text-3xl font-bold tracking-tight ${colorMap[highlightColor] || "text-white"}`}>
        {value}
      </div>
      {subtitle && <p className="mt-1 text-xs text-gray-500">{subtitle}</p>}
    </div>
  );
}
