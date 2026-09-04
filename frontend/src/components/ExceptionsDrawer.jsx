import React, { useState } from "react";
import { HelpCircle, ChevronDown, ChevronUp, AlertCircle } from "lucide-react";

export default function ExceptionsDrawer({ exceptions = [] }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!exceptions || exceptions.length === 0) return null;

  return (
    <div className="rounded-xl border border-border bg-card shadow-sm overflow-hidden transition-all">
      {/* Clickable Header Bar */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-5 flex items-center justify-between text-left hover:bg-secondary/50 transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            <HelpCircle className="w-4 h-4"/>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-foreground">
                Unclassified Exceptions & Ambiguities
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                {exceptions.length} Items
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Transactions with missing sub-instrument tags or conflicting metadata, presented transparently
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground font-mono">
          <span>{isOpen ? "Collapse" : "Inspect"}</span>
          {isOpen ? <ChevronUp className="w-4 h-4"/> : <ChevronDown className="w-4 h-4"/>}
        </div>
      </button>

      {/* Expanded Table */}
      {isOpen && (
        <div className="border-t border-border p-5 bg-card space-y-3">
          <div className="flex items-center gap-2 text-xs text-amber-600 dark:text-amber-400 font-mono">
            <AlertCircle className="w-3.5 h-3.5"/>
            <span>Honesty Constraint: Zero ambiguous transactions are artificially forced into classifications.</span>
          </div>

          <div className="max-h-72 overflow-y-auto divide-y divide-border/60 rounded-lg border border-border bg-card">
            {exceptions.map((item, idx) => (
              <div
                key={idx}
                className="p-3 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2"
              >
                <div className="flex items-center gap-2 font-mono">
                  <span className="font-semibold text-foreground text-sm">{item.transaction_id}</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-secondary text-secondary-foreground border border-border">
                    Exception
                  </span>
                </div>
                <span className="text-foreground/90 text-right sm:text-left font-sans text-xs">
                  {item.note || "Missing or incomplete sub_instrument metadata."}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
