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
        "relative overflow-hidden rounded-xl border p-5 shadow-sm transition-all duration-200 hover:shadow-md",
        style.card
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className={cn("text-xs font-bold tracking-wider uppercase font-mono truncate", style.title)}>
          {title}
        </span>
        {badge && (
          <span
            className={cn(
              "text-[10px] font-mono font-medium px-2 py-0.5 rounded border whitespace-nowrap shrink-0",
              style.badge
            )}
          >
            {badge}
          </span>
        )}
      </div>

      <div className="mt-3 flex items-baseline justify-between gap-2">
        <div className={cn("text-2xl font-bold tracking-tight font-mono", style.value)}>
          {value}
        </div>
        {Icon && <Icon className={cn("w-4 h-4 shrink-0", style.icon)} />}
      </div>

      <div className={cn("mt-2 flex items-center justify-between text-sm font-medium", style.subtitle)}>
        <span className="truncate">{subtitle}</span>
        {trendText && (
          <span className="font-mono text-xs font-semibold shrink-0 ml-2">
            {trendText}
          </span>
        )}
      </div>
    </div>
  );
}
