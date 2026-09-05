import React, { useState } from "react";
import { UploadCloud, Play, CheckCircle2, AlertTriangle, BookmarkPlus } from "lucide-react";
import { uploadSettlementFile, captureBaselineSnapshot } from "../services/api";

export default function ControlCockpit({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAuditing, setIsAuditing] = useState(false);
  const [isSnapshotting, setIsSnapshotting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setFeedback(null);
    }
  };

  const handleRunAudit = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      setIsAuditing(true);
      setFeedback(null);
      await uploadSettlementFile(selectedFile);
      setFeedback({ type: "success", text: `Audit executed on ${selectedFile.name}` });
      if (onUploadSuccess) {
        setTimeout(() => {
          onUploadSuccess();
          setSelectedFile(null);
          setFeedback(null);
        }, 1200);
      }
    } catch (err) {
      setFeedback({ type: "error", text: err.message || "Failed to audit settlement file." });
    } finally {
      setIsAuditing(false);
    }
  };

  const handleCaptureBaseline = async () => {
    try {
      setIsSnapshotting(true);
      setFeedback(null);
      const res = await captureBaselineSnapshot("batch_1");
      setFeedback({ type: "success", text: `Baseline snapshot locked (${res.snapshot?.snapshot_id || "Active"}). Ready for Batch 2 comparison.` });
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err) {
      setFeedback({ type: "error", text: err.message || "Failed to lock baseline snapshot." });
    } finally {
      setIsSnapshotting(false);
    }
  };

  return (
    <div className="w-full rounded-xl border border-border bg-card p-3.5 px-4 shadow-sm transition-colors duration-200">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        {/* Cockpit Description */}
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <h2 className="text-xs font-bold uppercase tracking-wider text-foreground">
              Audit Operations Cockpit
            </h2>
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground border border-border">
              Layer 1-3 Active
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground leading-tight">
            Ingest payment settlement files to audit fee overcharges, detect margin leaks, and trigger autonomous remediation cases.
          </p>
        </div>

        {/* Upload & Action Trigger */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={handleCaptureBaseline}
            disabled={isSnapshotting}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-border bg-secondary hover:bg-muted text-secondary-foreground text-xs font-medium cursor-pointer transition-colors disabled:opacity-50"
            title="Lock current metrics as baseline for multi-batch improvement tracking"
          >
            <BookmarkPlus className="w-3.5 h-3.5 text-emerald-500" />
            <span>{isSnapshotting ? "Saving..." : "Lock Baseline"}</span>
          </button>

          <form onSubmit={handleRunAudit} className="flex items-center gap-2">
            <label className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border bg-secondary hover:bg-muted text-secondary-foreground text-xs font-medium cursor-pointer transition-colors">
              <UploadCloud className="w-4 h-4 text-primary"/>
              <span className="truncate max-w-[150px]">
                {selectedFile ? selectedFile.name : "Select CSV"}
              </span>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>

            <button
              type="submit"
              disabled={!selectedFile || isAuditing}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary hover:opacity-90 disabled:opacity-50 text-primary-foreground text-xs font-semibold tracking-wide transition-all shadow-sm cursor-pointer disabled:cursor-not-allowed"
            >
              <Play className={`w-3.5 h-3.5 ${isAuditing ? "animate-spin" : ""}`} />
              <span>{isAuditing ? "Auditing..." : "Execute Audit"}</span>
            </button>
          </form>
        </div>
      </div>


      {/* Feedback Banner */}
      {feedback && (
        <div
          className={`mt-4 p-3 rounded-lg border text-xs flex items-center gap-2 ${
            feedback.type === "success"
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400"
              : "bg-destructive/10 border-destructive/30 text-destructive dark:text-red-400"
          }`}
        >
          {feedback.type === "success" ? (
            <CheckCircle2 className="w-4 h-4 shrink-0"/>
          ) : (
            <AlertTriangle className="w-4 h-4 shrink-0"/>
          )}
          <span>{feedback.text}</span>
        </div>
      )}
    </div>
  );
}
