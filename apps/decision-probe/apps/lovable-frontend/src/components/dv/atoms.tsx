import { type ReactNode } from "react";
import type { Severity, Status } from "./data";

export function SeverityDot({ severity, className = "" }: { severity: Severity; className?: string }) {
  const c =
    severity === "critical" ? "bg-danger" :
    severity === "high" ? "bg-warning" :
    severity === "medium" ? "bg-accent" :
    "bg-fg-muted";
  return <span className={`inline-block h-1.5 w-1.5 rounded-full ${c} ${className}`} />;
}

export function StatusGlyph({ status }: { status: Status }) {
  const map = { active: "●", decided: "◐", resolved: "○" } as const;
  const color = status === "active" ? "text-fg-strong" : "text-fg-muted";
  return <span className={`mono text-[10px] ${color}`}>{map[status]}</span>;
}

export function Kbd({ children }: { children: ReactNode }) {
  return <span className="kbd">{children}</span>;
}

export function Confidence({ value }: { value: number }) {
  const color =
    value >= 0.75 ? "text-accent" :
    value >= 0.4 ? "text-foreground" :
    "text-fg-muted";
  return <span className={`mono text-[11.5px] ${color}`}>{value.toFixed(2)}</span>;
}

export function Sparkline({ data, trend = "up" }: { data: number[]; trend?: "up" | "down" }) {
  const w = 88, h = 20, pad = 1;
  const max = Math.max(...data), min = Math.min(...data);
  const range = max - min || 1;
  const step = (w - pad * 2) / (data.length - 1);
  const pts = data.map((v, i) => {
    const x = pad + i * step;
    const y = h - pad - ((v - min) / range) * (h - pad * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  const stroke = trend === "up" ? "var(--danger)" : "var(--info)";
  return (
    <svg width={w} height={h} className="overflow-visible">
      <polyline points={pts} fill="none" stroke={stroke} strokeWidth="1" strokeLinejoin="round" strokeLinecap="round" opacity="0.85" />
    </svg>
  );
}

export function TaskGlyph({ state }: { state: "done" | "running" | "warn" | "fail" }) {
  if (state === "done") return <span className="mono text-[11px] text-success">✓</span>;
  if (state === "running") return <span className="mono text-[11px] text-info">⟳</span>;
  if (state === "warn") return <span className="mono text-[11px] text-warning">⚠</span>;
  return <span className="mono text-[11px] text-danger">✗</span>;
}

export function SourceTag({ source }: { source: string }) {
  return <span className="mono text-[11px] text-fg-muted uppercase tracking-wider">{source}</span>;
}
