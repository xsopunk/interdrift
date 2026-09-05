import React from "react";
import { cn } from "../lib/utils";

export default function MetricCard({
  title,
  value,
  subtitle,
  badge,
  icon: Icon,
  variant = "default",
  trendText,
}) {
  const variantStyles = {
    default: {
      card: "bg-card border-border",
      title: "text-muted-foreground",
      value: "text-foreground",
      subtitle: "text-foreground/80",
      badge: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
      icon: "text-muted-foreground",
    },
    destructive: {
      card: "bg-red-950/80 border-red-900/60",
      title: "text-red-300/80",
      value: "text-red-300 font-bold",
      subtitle: "text-red-300/80",
      badge: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
      icon: "text-red-400",
    },
    success: {
      card: "bg-emerald-950/80 border-emerald-900/60",
      title: "text-emerald-300/80",
      value: "text-emerald-300 font-bold",
      subtitle: "text-emerald-300/80",
      badge: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
      icon: "text-emerald-400",
    },
    warning: {
      card: "bg-amber-950/80 border-amber-900/60",
      title: "text-amber-300/80",
      value: "text-amber-300 font-bold",
      subtitle: "text-amber-300/80",
      badge: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
      icon: "text-amber-400",
    },
    primary: {
      card: "bg-purple-950/80 border-purple-900/60",
      title: "text-purple-300/80",
      value: "text-purple-300 font-bold",
      subtitle: "text-purple-300/80",
      badge: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
      icon: "text-purple-400",
    },
  };

  const style = variantStyles[variant] || variantStyles.default;

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border p-3.5 backdrop-blur-xl transition-all duration-200 hover:shadow-[0_8px_25px_-5px_rgba(0,0,0,0.5)] hover:border-zinc-700/90 flex flex-col justify-between min-h-[96px] group",
        style.card
      )}
    >
      {/* Top Subtle Gradient Light Beam Accent */}
      <div className="absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-zinc-500/20 to-transparent group-hover:via-zinc-400/40 transition-colors" />
      <div className="flex items-start justify-between gap-1">
        <span className={cn("text-[10px] font-bold tracking-tight uppercase font-mono leading-tight max-w-[70%]", style.title)}>
          {title}
        </span>
        {badge && (
          <span
            className={cn(
              "text-[9px] font-mono font-medium px-1.5 py-0.5 rounded border whitespace-nowrap shrink-0",
              style.badge
            )}
          >
            {badge}
          </span>
        )}
      </div>

      <div className="mt-1.5 flex items-baseline justify-between gap-1">
        <div className={cn("text-xl font-bold tracking-tight font-mono", style.value)}>
          {value}
        </div>
        {Icon && <Icon className={cn("w-4 h-4 shrink-0", style.icon)} />}
      </div>

      <div className={cn("mt-1 flex items-center justify-between text-xs font-medium", style.subtitle)}>
        <span className="text-[10px] truncate">{subtitle}</span>
        {trendText && (
          <span className="font-mono text-[9px] font-semibold shrink-0 ml-1">
            {trendText}
          </span>
        )}
      </div>
    </div>
  );
}

