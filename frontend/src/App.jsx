import { useEffect, useState } from "react";
import { checkHealth, getFinalReport } from "./services/api";

export default function App() {
  const [status, setStatus] = useState("Checking backend...");
  const [reportData, setReportData] = useState(null);

  useEffect(() => {
    async function init() {
      try {
        await checkHealth();
        const report = await getFinalReport();
        setStatus("Connected to InterDrift API");
        setReportData(report);
      } catch (err) {
        setStatus(`Connection failed: ${err.message}`);
      }
    }
    init();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-xl font-bold text-accentCyan">InterDrift API Connectivity Test</h1>
      <p className="mt-2 text-sm text-gray-400">{status}</p>
      {reportData && (
        <pre className="mt-4 p-4 bg-surface rounded text-xs overflow-auto border border-surfaceBorder">
          {JSON.stringify(reportData.overview, null, 2)}
        </pre>
      )}
    </div>
  );
}