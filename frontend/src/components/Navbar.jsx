import React from "react";
import { ShieldCheck, Layers, FlaskConical } from "lucide-react";

export default function Navbar({ rowCount = 0, backendStatus = "online", onOpenTestData }) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-border bg-card/80 backdrop-blur-md transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand & Track Badge */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-primary text-primary-foreground shadow-sm">
            <ShieldCheck className="w-5 h-5"/>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold tracking-tight text-foreground text-lg">InterDrift</span>
              <span className="text-[10px] uppercase font-mono font-bold tracking-wider px-2 py-0.5 rounded bg-accent text-accent-foreground border border-border">
                Track 4: AI Finance Controller
              </span>
            </div>
            <p className="text-[11px] text-muted-foreground hidden sm:block">
              Autonomous Payment Fee Controller · Audit, Recover & Prevent Leakage
            </p>
          </div>
        </div>

        {/* Live State Badges & Actions */}
        <div className="flex items-center gap-3">
          {/* Test Data Trigger Button */}
          <button
            onClick={onOpenTestData}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-semibold shadow-sm transition-all cursor-pointer"
          >
            <FlaskConical className="w-3.5 h-3.5" />
            <span>Test Data</span>
          </button>

          {/* Engine Status Indicator */}
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-md border border-border bg-secondary/50 text-xs font-mono">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-muted-foreground text-[11px]">API:</span>
            <span className="text-foreground font-medium uppercase text-[11px]">{backendStatus}</span>
          </div>

          {/* Audited Volume */}
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-border bg-secondary/50 text-xs font-mono text-muted-foreground">
            <Layers className="w-3.5 h-3.5 text-primary"/>
            <span>{rowCount} txns</span>
          </div>
        </div>
      </div>
    </header>
  );
}
