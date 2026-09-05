import React, { useState, useRef, useEffect } from "react";
import { 
  Bot, 
  X, 
  Send, 
  Sparkles, 
  Trash2, 
  ChevronRight, 
  MessageSquare,
  ShieldCheck,
  Zap,
  CornerDownLeft
} from "lucide-react";
import { sendCopilotMessage } from "../../services/api";

const SUGGESTED_QUERIES = [
  "What is our total direct fee leakage?",
  "Explain Rule R10 commercial downgrade",
  "Why was TXN_000012 flagged as a leak?",
  "Which case has the highest recoverable exposure?"
];

export default function CopilotSidePanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I am your **InterDrift AI Finance Controller Copilot**. I have full access to your settlement audit results, statutory rule circulars, and prioritized remediation cases. What can I analyze for you today?",
      sources: []
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      inputRef.current?.focus();
    }
  }, [isOpen, messages]);

  const handleSend = async (textToSend) => {
    const query = (textToSend || input).trim();
    if (!query || loading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: "user",
      content: query
    };

    const newHistory = [...messages, userMessage];
    setMessages(newHistory);
    setInput("");
    setLoading(true);

    try {
      // Build conversation history format for backend
      const apiHistory = newHistory.slice(-6).map((m) => ({
        role: m.role,
        content: m.content
      }));

      const res = await sendCopilotMessage(query, apiHistory);

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.reply || "No response received.",
        sources: res.sources || []
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: `Unable to connect to Copilot: ${err.message}. Please verify the backend is running.`,
          sources: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: "Chat history cleared. Grounded in live audit data. How can I assist?",
        sources: []
      }
    ]);
  };

  return (
    <>
      {/* Persistent Floating Tab (When Closed) */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed top-20 right-0 z-40 flex items-center gap-2 px-3.5 py-2.5 rounded-l-xl bg-primary text-primary-foreground shadow-lg hover:shadow-xl hover:translate-x-[-2px] transition-all cursor-pointer border border-r-0 border-primary-foreground/20 group"
          title="Open AI Finance Copilot"
        >
          <div className="relative">
            <Bot className="w-4 h-4 group-hover:scale-110 transition-transform" />
            <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          </div>
          <span className="text-xs font-semibold tracking-wide font-sans">Copilot</span>
        </button>
      )}

      {/* Slide-Over Side Panel (Below Top Nav) */}
      <div
        className={`fixed top-14 right-0 z-40 w-full sm:w-[420px] h-[calc(100vh-3.5rem)] bg-card border-l border-border shadow-2xl flex flex-col transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="px-4 py-3 border-b border-border bg-muted/40 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xs font-bold text-foreground">InterDrift Copilot</h3>
                <span className="inline-flex items-center gap-1 text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                  <Zap className="w-2.5 h-2.5" /> Groq Grounded
                </span>
              </div>
              <p className="text-[10px] text-muted-foreground">Deterministic audit context</p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={handleClear}
              className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors cursor-pointer"
              title="Clear conversation"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors cursor-pointer"
              title="Close panel"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex flex-col ${m.role === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-[88%] rounded-xl px-3.5 py-2.5 text-xs leading-relaxed ${
                  m.role === "user"
                    ? "bg-primary text-primary-foreground font-medium rounded-br-xs"
                    : "bg-secondary/70 border border-border text-foreground rounded-bl-xs shadow-xs"
                }`}
              >
                <div className="whitespace-pre-wrap space-y-1 font-sans">
                  {m.content}
                </div>

                {/* Source chips */}
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-border/50 flex items-center gap-1.5 flex-wrap">
                    <span className="text-[9px] font-mono text-muted-foreground uppercase">Citations:</span>
                    {m.sources.map((src, idx) => (
                      <span
                        key={idx}
                        className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-background border border-border text-foreground font-semibold"
                      >
                        {src}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground p-3 rounded-xl bg-secondary/40 border border-border/50 w-fit">
              <div className="w-2 h-2 rounded-full bg-primary animate-ping" />
              <span className="font-mono text-[11px]">Analyzing deterministic audit context...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestion Chips */}
        <div className="px-3 pt-2 pb-1 border-t border-border/50 bg-muted/20 shrink-0">
          <div className="flex items-center gap-1 overflow-x-auto pb-1.5 scrollbar-none">
            <Sparkles className="w-3 h-3 text-primary shrink-0 ml-1" />
            {SUGGESTED_QUERIES.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                disabled={loading}
                className="shrink-0 text-[10px] px-2 py-1 rounded-md bg-secondary hover:bg-secondary/80 border border-border text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <div className="p-3 border-t border-border bg-card shrink-0">
          <div className="flex items-center gap-2 bg-secondary/50 rounded-xl border border-border px-3 py-2 focus-within:ring-2 focus-within:ring-primary/40 focus-within:border-primary transition-all">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about fees, rules, or TXN_..."
              disabled={loading}
              className="flex-1 bg-transparent text-xs text-foreground placeholder:text-muted-foreground focus:outline-hidden"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              className="p-1 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-30 transition-opacity cursor-pointer shrink-0"
              title="Send message (Enter)"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="flex items-center justify-between text-[9px] text-muted-foreground mt-1.5 px-1 font-mono">
            <span>Press Enter to send</span>
            <span>Zero Hallucination Grounding</span>
          </div>
        </div>
      </div>
    </>
  );
}
