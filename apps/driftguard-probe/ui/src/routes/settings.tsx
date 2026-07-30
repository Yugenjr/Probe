import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings · DriftGuard Probe" },
      {
        name: "description",
        content: "Configure Probe engine, integrations and workspace preferences.",
      },
      { property: "og:title", content: "Settings · DriftGuard Probe" },
      { property: "og:description", content: "Configure Probe engine and integrations." },
    ],
  }),
  component: SettingsPage,
});

const sections = [
  { k: "general", l: "General" },
  { k: "engine", l: "Investigation engine" },
  { k: "integrations", l: "Integrations" },
  { k: "notifications", l: "Notifications" },
  { k: "api", l: "API keys" },
] as const;

function SettingsPage() {
  const [active, setActive] = useState<(typeof sections)[number]["k"]>("engine");
  const [autoRun, setAutoRun] = useState(true);
  const [notifyCritical, setNotifyCritical] = useState(true);
  const [notifyDaily, setNotifyDaily] = useState(false);

  return (
    <div className="mx-auto max-w-[1200px] px-4 py-6 md:px-8 md:py-8">
      <h1 className="text-[22px] font-semibold tracking-tight text-foreground">
        Settings
      </h1>
      <p className="mt-1 text-[13px] text-muted-foreground">
        Manage how Probe runs investigations for your workspace.
      </p>

      <div className="mt-6 grid grid-cols-1 gap-8 md:grid-cols-[200px_minmax(0,1fr)]">
        <nav className="space-y-0.5">
          {sections.map((s) => (
            <button
              key={s.k}
              onClick={() => setActive(s.k)}
              className={cn(
                "block w-full rounded-md px-2.5 py-1.5 text-left text-[13px] font-medium transition-colors",
                active === s.k
                  ? "bg-surface text-foreground"
                  : "text-muted-foreground hover:bg-surface/60 hover:text-foreground",
              )}
            >
              {s.l}
            </button>
          ))}
        </nav>

        <div className="space-y-4">
          {active === "engine" && (
            <>
              <Card
                title="Auto-run on new incidents"
                description="Start an investigation automatically when DriftGuard raises a new drift alert."
              >
                <Toggle checked={autoRun} onChange={setAutoRun} />
              </Card>

              <Card
                title="Investigation depth"
                description="How aggressively Probe explores hypotheses. Deeper searches take longer but improve confidence."
              >
                <SegmentedControl
                  options={["Fast", "Balanced", "Thorough"]}
                  defaultValue="Balanced"
                />
              </Card>

              <Card
                title="Telemetry window"
                description="Default lookback window when Probe queries feature and prediction telemetry."
              >
                <select className="h-9 rounded-md border border-border bg-surface px-2.5 text-[13px] text-foreground">
                  <option>Last 6 hours</option>
                  <option>Last 24 hours</option>
                  <option>Last 7 days</option>
                </select>
              </Card>
            </>
          )}

          {active === "notifications" && (
            <>
              <Card
                title="Critical incidents"
                description="Page the on-call engineer immediately when Probe classifies an incident as critical."
              >
                <Toggle
                  checked={notifyCritical}
                  onChange={setNotifyCritical}
                />
              </Card>
              <Card
                title="Daily digest"
                description="Email a summary of all investigations completed in the last 24 hours."
              >
                <Toggle checked={notifyDaily} onChange={setNotifyDaily} />
              </Card>
            </>
          )}

          {active === "integrations" && (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {[
                { name: "DriftGuard", status: "Connected", note: "workspace/prod" },
                { name: "Datadog", status: "Connected", note: "org 41291" },
                { name: "Slack", status: "Connected", note: "#ml-incidents" },
                { name: "GitHub", status: "Connected", note: "org/ml", hasStats: true },
                { name: "PagerDuty", status: "Not connected" },
                { name: "Notion", status: "Not connected" },
              ].map((i) => (
                <div
                  key={i.name}
                  className="rounded-lg border border-border bg-surface p-3.5"
                >
                  <div className="flex items-center justify-between">
                    <div className="text-[13px] font-medium text-foreground">
                      {i.name}
                    </div>
                    <span
                      className={cn(
                        "inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10.5px] font-medium",
                        i.status === "Connected"
                          ? "text-success border-success/30 bg-success/10"
                          : "text-muted-foreground border-border bg-muted/40",
                      )}
                    >
                      {i.status === "Connected" && <Check className="size-3" />}
                      {i.status}
                    </span>
                  </div>
                  {i.note && (
                    <div className="mt-1 text-[11px] font-mono text-muted-foreground">
                      {i.note}
                    </div>
                  )}
                  {i.hasStats ? (
                    <button 
                      onClick={async () => {
                        try {
                          const res = await fetch("http://localhost:8006/api/v1/github/stats");
                          if(res.ok) {
                            const data = await res.json();
                            alert(`GitHub Stats Fetched!\nStars: ${data.stars}\nIssues: ${data.open_issues}\nLatest: ${data.latest_commit}`);
                          } else {
                            alert("Failed to fetch stats.");
                          }
                        } catch(e) {
                          alert("Error fetching GitHub stats.");
                        }
                      }}
                      className="mt-3 h-7 rounded-md border border-border bg-background px-2 text-[11.5px] font-medium text-foreground hover:border-border-strong">
                      Fetch Repository Stats
                    </button>
                  ) : (
                    <button className="mt-3 h-7 rounded-md border border-border bg-background px-2 text-[11.5px] font-medium text-foreground hover:border-border-strong">
                      {i.status === "Connected" ? "Configure" : "Connect"}
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}

          {active === "general" && (
            <>
              <Card title="Workspace name" description="Shown across the Probe UI and in exported reports.">
                <input
                  defaultValue="Acme ML"
                  className="h-9 w-full max-w-xs rounded-md border border-border bg-surface px-2.5 text-[13px] text-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </Card>
              <Card title="Default region" description="Region used when telemetry sources are ambiguous.">
                <select className="h-9 rounded-md border border-border bg-surface px-2.5 text-[13px] text-foreground">
                  <option>us-east-1</option>
                  <option>us-west-2</option>
                  <option>eu-west-1</option>
                </select>
              </Card>
            </>
          )}

          {active === "api" && (
            <Card title="Personal access token" description="Use this token for programmatic access to the Probe API.">
              <div className="flex items-center gap-2">
                <code className="flex-1 rounded-md border border-border bg-background px-2.5 py-1.5 font-mono text-[12px] text-muted-foreground">
                  dgp_••••••••••••••••4a7c
                </code>
                <button className="h-8 rounded-md border border-border bg-background px-2.5 text-[12px] font-medium text-foreground hover:border-border-strong">
                  Rotate
                </button>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function Card({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-border bg-surface p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <div className="text-[13px] font-medium text-foreground">{title}</div>
        <p className="mt-0.5 text-[12px] text-muted-foreground">{description}</p>
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  );
}

function Toggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={cn(
        "relative h-5 w-9 rounded-full border transition-colors",
        checked
          ? "bg-primary border-primary/60"
          : "bg-surface-2 border-border",
      )}
    >
      <span
        className={cn(
          "absolute top-0.5 size-3.5 rounded-full bg-background transition-transform",
          checked ? "translate-x-[18px]" : "translate-x-0.5",
        )}
      />
    </button>
  );
}

function SegmentedControl({
  options,
  defaultValue,
}: {
  options: string[];
  defaultValue: string;
}) {
  const [v, setV] = useState(defaultValue);
  return (
    <div className="inline-flex rounded-md border border-border bg-surface p-0.5">
      {options.map((o) => (
        <button
          key={o}
          onClick={() => setV(o)}
          className={cn(
            "rounded px-2.5 py-1 text-[12px] font-medium transition-colors",
            v === o
              ? "bg-elevated text-foreground"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          {o}
        </button>
      ))}
    </div>
  );
}
