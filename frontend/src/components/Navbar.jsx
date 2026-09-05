import React from "react";
import { ShieldCheck, FlaskConical } from "lucide-react";

export default function Navbar({ rowCount = 0, backendStatus = "online", onOpenTestData }) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-xl transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between gap-4">
        {/* Brand & Track Badge */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-gradient-to-br from-zinc-100 to-zinc-300 text-zinc-950 shadow-md">
            <ShieldCheck className="w-4 h-4 text-zinc-950"/>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-tight text-base bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-400">
                InterDrift
              </span>
              <span className="text-[9px] uppercase font-mono font-bold tracking-wider px-1.5 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-xs">
                Track 4: AI Finance Controller
              </span>
            </div>
            <p className="text-[10px] text-zinc-400 hidden sm:block leading-tight font-sans">
              Autonomous Payment Fee Controller · Audit, Recover & Prevent Leakage
            </p>
          </div>
        </div>

        {/* Live State Badges & Actions */}
        <div className="flex items-center gap-2.5 ml-auto">
          {/* Test Data Trigger Button */}
          <button
            onClick={onOpenTestData}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-gradient-to-r from-zinc-100 to-zinc-300 hover:from-white hover:to-zinc-200 text-zinc-950 text-xs font-semibold shadow-[0_0_15px_rgba(255,255,255,0.1)] hover:shadow-[0_0_20px_rgba(255,255,255,0.25)] transition-all cursor-pointer"
          >
            <FlaskConical className="w-3.5 h-3.5" />
            <span>Test Data</span>
          </button>

          {/* Engine Status Indicator */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-zinc-800/80 bg-zinc-900/60 text-xs font-mono backdrop-blur-md">
            <span className="relative flex h-1.5 w-1.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
            </span>
            <span className="text-zinc-400 text-[10px]">API:</span>
            <span className="text-emerald-400 font-semibold uppercase text-[10px]">{backendStatus}</span>
          </div>
        </div>
      </div>
    </header>
  );
}


