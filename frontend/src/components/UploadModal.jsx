import { useState } from "react";
import { uploadSettlementFile } from "../services/api";

export default function UploadModal({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    try {
      setUploading(true);
      setMessage(null);
      await uploadSettlementFile(file);
      setMessage({ type: "success", text: "Settlement audited successfully." });
      if (onUploadSuccess) {
        setTimeout(() => {
          onUploadSuccess();
          setMessage(null);
          setFile(null);
        }, 1000);
      }
    } catch (err) {
      setMessage({ type: "error", text: err.message || "Failed to process settlement file." });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-surface border border-surfaceBorder rounded-xl p-5 shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <h3 className="text-sm font-bold text-white">Audit New Settlement Batch</h3>
        <p className="text-xs text-gray-400 mt-0.5">
          Upload settlement CSV to execute deterministic rules and LLM diagnostic pipeline
        </p>
      </div>

      <form onSubmit={handleUpload} className="flex flex-wrap items-center gap-3 w-full md:w-auto">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
          className="text-xs text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-gray-800 file:text-cyan-400 hover:file:bg-gray-700 cursor-pointer"
        />
        <button
          type="submit"
          disabled={!file || uploading}
          className="px-4 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-800 disabled:text-gray-500 text-white text-xs font-medium transition-colors cursor-pointer"
        >
          {uploading ? "Auditing..." : "Run Analysis"}
        </button>
      </form>

      {message && (
        <div
          className={`w-full text-xs p-2 rounded border ${
            message.type === "success"
              ? "bg-emerald-950/40 text-emerald-400 border-emerald-900/50"
              : "bg-red-950/40 text-red-400 border-red-900/50"
          }`}
        >
          {message.text}
        </div>
      )}
    </div>
  );
}
