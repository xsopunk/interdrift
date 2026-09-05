import React, { useState } from "react";
import { X, BookOpen, Search, ShieldCheck, Scale, ExternalLink, Sparkles } from "lucide-react";

const RULES_DATA = [
  {
    id: "R1",
    name: "Bank Account UPI",
    category: "Zero-MDR Mandate",
    type: "sourced",
    citation: "Finance Act 2019 / Sec 10A PSS Act 2007",
    fee: "0.0% MDR (Strict Zero)",
    summary: "All standard bank-to-bank UPI peer-to-merchant payments must carry zero merchant fee. Any fee charged is an illegal statutory breach."
  },
  {
    id: "R2",
    name: "RuPay Domestic Debit",
    category: "Zero-MDR Mandate",
    type: "sourced",
    citation: "Ministry of Finance Gazette / Sec 10A PSS Act",
    fee: "0.0% MDR (Strict Zero)",
    summary: "Indian government gazette mandates zero MDR for all domestic RuPay debit card transactions, regardless of transaction amount or merchant size."
  },
  {
    id: "R3",
    name: "RuPay Credit on UPI (≤ ₹2,000)",
    category: "Zero-MDR Mandate",
    type: "sourced",
    citation: "NPCI Circular NPCI/UPI/OC-154/2022-23",
    fee: "0.0% MDR (Strict Zero)",
    summary: "RuPay credit cards linked to UPI apps (GPay, PhonePe, Paytm) carry zero merchant interchange on tickets up to ₹2,000 to promote credit inclusion."
  },
  {
    id: "R4",
    name: "RuPay Credit on UPI (> ₹2,000)",
    category: "UPI Interchange Slab",
    type: "illustrative",
    citation: "NPCI Framework / Bank Merchant Circulars",
    fee: "1.50% Interchange Benchmark",
    summary: "RuPay credit card UPI transactions above ₹2,000 are subject to standard tiered interchange. The benchmark modeled rate is 1.50%."
  },
  {
    id: "R5",
    name: "PPI Wallet on UPI (≤ ₹2,000)",
    category: "Zero-MDR Mandate",
    type: "sourced",
    citation: "NPCI Circular NPCI/2022-23/PPI-Interchange",
    fee: "0.0% Interchange",
    summary: "Prepaid payment instruments (wallets like Paytm, Mobikwik, Amazon Pay) on UPI carry zero merchant interchange for transactions up to ₹2,000."
  },
  {
    id: "R6a",
    name: "PPI Wallet on UPI: Education & Utilities (> ₹2,000)",
    category: "UPI Interchange Slab",
    type: "sourced",
    citation: "NPCI Circular NPCI/2022-23/PPI-Interchange",
    fee: "0.70% Maximum Cap",
    summary: "Concessionary interchange ceiling of 0.70% applies to utility billers, schools, colleges, and government payments over ₹2,000."
  },
  {
    id: "R6b",
    name: "PPI Wallet on UPI: Supermarkets (> ₹2,000)",
    category: "UPI Interchange Slab",
    type: "sourced",
    citation: "NPCI Circular NPCI/2022-23/PPI-Interchange",
    fee: "0.90% Maximum Cap",
    summary: "Supermarkets and retail grocery stores (MCC 5411) have an official NPCI fee cap of 0.90% for wallet transactions exceeding ₹2,000."
  },
  {
    id: "R6c",
    name: "PPI Wallet on UPI: General Commercial (> ₹2,000)",
    category: "UPI Interchange Slab",
    type: "sourced",
    citation: "NPCI Circular NPCI/2022-23/PPI-Interchange",
    fee: "1.10% Maximum Cap",
    summary: "Standard commercial merchants have an interchange ceiling capped at 1.10% for large ticket wallet-on-UPI payments."
  },
  {
    id: "R7",
    name: "Visa / Mastercard Debit (Turnover ≤ ₹20 Lakh)",
    category: "RBI Debit Cap",
    type: "sourced",
    citation: "RBI Circular DPSS.CO.PD No.1633/02.14.003/2017-18",
    fee: "0.40% capped at max ₹200",
    summary: "Small merchants with annual turnover up to ₹20L are legally protected by RBI: fees cannot exceed 0.40% or an absolute cap of ₹200 per transaction."
  },
  {
    id: "R8",
    name: "Visa / Mastercard Debit (Turnover > ₹20 Lakh)",
    category: "RBI Debit Cap",
    type: "sourced",
    citation: "RBI Circular DPSS.CO.PD No.1633/02.14.003/2017-18",
    fee: "0.90% capped at max ₹1,000",
    summary: "Large merchants pay a maximum of 0.90% with an absolute statutory ceiling of ₹1,000. For transactions above ₹1,11,111, the fee cannot exceed ₹1,000."
  },
  {
    id: "R9",
    name: "Retail & Commercial Credit Cards",
    category: "Contract Benchmark",
    type: "illustrative",
    citation: "Merchant Service Agreement (MSA) Terms",
    fee: "2.0% Contracted Baseline",
    summary: "Credit card interchange is unregulated in India; fees are reviewed against the merchant's bilateral contracted flat rate (typically ~2.0%)."
  },
  {
    id: "R10",
    name: "Commercial Card L2/L3 Downgrade",
    category: "Interchange Qualification",
    type: "illustrative",
    citation: "B2B Payment Gateway Data Standards",
    fee: "+0.80% Penalty Surcharge",
    summary: "Corporate cards incur an 80 bps penalty if required Level 2/Level 3 data fields (Tax ID, PO code, line items) are omitted by the gateway checkout."
  },
  {
    id: "R11",
    name: "Blended MDR vs. Interchange-Plus (IC+)",
    category: "Structural Pricing Model",
    type: "illustrative",
    citation: "Enterprise Acceptance Optimization Heuristic",
    fee: "Portfolio Spread Variance",
    summary: "Quantifies the margin spread absorbed by aggregators billing a flat 2.0% rate over lower underlying network costs (1.2% - 1.8%)."
  },
  {
    id: "R12",
    name: "Merchant Category Code (MCC) Misclassification",
    category: "Gateway Configuration",
    type: "illustrative",
    citation: "ISO 18245 Merchant Category Standards",
    fee: "Rate Disparity Spread",
    summary: "Flags transactions routed under an incorrect merchant category code (e.g. grocery 5411 vs B2B 5045), causing interchange downgrades."
  },
  {
    id: "R13",
    name: "Least-Cost Routing Optimization",
    category: "Smart Routing Opportunity",
    type: "illustrative",
    citation: "Advisory Payment Routing Heuristic",
    fee: "Cost-Saving Differential",
    summary: "Advisory diagnostic highlighting transactions where high-cost credit cards were chosen when zero-MDR bank/UPI rails were available."
  }
];

export default function RulesModal({ isOpen, onClose }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("all");

  if (!isOpen) return null;

  const filteredRules = RULES_DATA.filter((r) => {
    const matchesSearch = 
      r.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.citation.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return false;

    if (activeTab === "zero") return r.category === "Zero-MDR Mandate";
    if (activeTab === "upi") return r.category.includes("UPI");
    if (activeTab === "debit") return r.category.includes("Debit");
    if (activeTab === "commercial") return r.category.includes("Commercial") || r.category.includes("Structural");

    return true;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-muted/40">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10 text-primary border border-primary/20">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-foreground">Audit Rules & Statutory Codex</h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 font-semibold">
                  13 Active Rules
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                Statutory RBI & NPCI gazettes, interchange fee slabs, and enterprise benchmarks enforced by InterDrift
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Toolbar: Search + Category Filters */}
        <div className="px-6 py-3 border-b border-border bg-card flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Search Box */}
          <div className="relative w-full sm:w-72">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search rules, circulars, caps..."
              className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-secondary/50 border border-border text-xs text-foreground placeholder:text-muted-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            />
          </div>

          {/* Quick Filter Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0">
            {[
              { id: "all", label: "All (13)" },
              { id: "zero", label: "Zero MDR" },
              { id: "upi", label: "UPI & Wallets" },
              { id: "debit", label: "Debit Caps" },
              { id: "commercial", label: "Commercial / Structural" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`text-[11px] px-2.5 py-1 rounded-md transition-colors whitespace-nowrap cursor-pointer ${
                  activeTab === tab.id
                    ? "bg-primary text-primary-foreground font-semibold"
                    : "bg-secondary/50 text-muted-foreground hover:text-foreground hover:bg-secondary"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Rules Grid List */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {filteredRules.map((rule) => (
            <div
              key={rule.id}
              className="p-4 rounded-xl border border-border bg-secondary/30 hover:bg-secondary/50 transition-colors flex flex-col justify-between space-y-2.5"
            >
              <div>
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
                      {rule.id}
                    </span>
                    <h4 className="text-xs font-bold text-foreground leading-snug">{rule.name}</h4>
                  </div>
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.5 rounded border shrink-0 ${
                      rule.type === "sourced"
                        ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                        : "bg-amber-500/10 text-amber-500 border-amber-500/20"
                    }`}
                  >
                    {rule.type === "sourced" ? "Statutory Gazette" : "Modeled Benchmark"}
                  </span>
                </div>

                <p className="text-xs text-muted-foreground mt-2 leading-relaxed">
                  {rule.summary}
                </p>
              </div>

              <div className="pt-2 border-t border-border/50 flex flex-col gap-1 text-[11px]">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-muted-foreground font-mono uppercase">Statutory Fee:</span>
                  <span className="font-bold font-mono text-emerald-500 dark:text-emerald-400">{rule.fee}</span>
                </div>
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[10px] text-muted-foreground font-mono uppercase shrink-0">Authority:</span>
                  <span className="text-[10px] text-muted-foreground text-right truncate" title={rule.citation}>
                    {rule.citation}
                  </span>
                </div>
              </div>
            </div>
          ))}

          {filteredRules.length === 0 && (
            <div className="col-span-2 py-12 text-center text-xs text-muted-foreground">
              No rules found matching "{searchTerm}".
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-border bg-muted/20 flex items-center justify-between text-xs text-muted-foreground">
          <span className="text-[11px] font-mono">Governed under Section 10A PSS Act 2007 & NPCI Rules</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-secondary hover:bg-muted text-foreground font-medium text-xs transition-colors cursor-pointer"
          >
            Close Codex
          </button>
        </div>
      </div>
    </div>
  );
}
