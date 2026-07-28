import { cn } from "@/lib/utils";
import type { Severity, InvestigationStatus } from "@/lib/mock-data";

const severityStyles: Record<Severity, string> = {
  critical: "text-destructive border-destructive/30 bg-destructive/10",
  high: "text-warning border-warning/30 bg-warning/10",
  medium: "text-info border-info/30 bg-info/10",
  low: "text-muted-foreground border-border bg-muted/40",
};

const statusStyles: Record<InvestigationStatus, string> = {
  running: "text-info border-info/30 bg-info/10",
  completed: "text-success border-success/30 bg-success/10",
  failed: "text-destructive border-destructive/30 bg-destructive/10",
  queued: "text-muted-foreground border-border bg-muted/40",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-medium uppercase tracking-wider",
        severityStyles[severity],
      )}
    >
      <span
        className={cn(
          "size-1.5 rounded-full",
          severity === "critical" && "bg-destructive",
          severity === "high" && "bg-warning",
          severity === "medium" && "bg-info",
          severity === "low" && "bg-muted-foreground",
        )}
      />
      {severity}
    </span>
  );
}

export function StatusBadge({ status }: { status: InvestigationStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-medium capitalize",
        statusStyles[status],
      )}
    >
      <span
        className={cn(
          "size-1.5 rounded-full",
          status === "running" && "bg-info animate-pulse",
          status === "completed" && "bg-success",
          status === "failed" && "bg-destructive",
          status === "queued" && "bg-muted-foreground",
        )}
      />
      {status}
    </span>
  );
}
