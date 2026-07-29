import { createFileRoute } from "@tanstack/react-router";
import { BookOpen, ArrowUpRight, Search, Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { fetchKBArticles, KBArticle } from "../lib/api-client";

export const Route = createFileRoute("/knowledge-base")({
  head: () => ({
    meta: [
      { title: "Knowledge Base · DriftGuard Probe" },
      {
        name: "description",
        content:
          "Playbooks, past investigations and remediation patterns learned by DriftGuard Probe.",
      },
      { property: "og:title", content: "Knowledge Base · DriftGuard Probe" },
      { property: "og:description", content: "Investigation playbooks and patterns." },
    ],
  }),
  component: KBPage,
});

function KBPage() {
  const [q, setQ] = useState("");
  const [articles, setArticles] = useState<KBArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchKBArticles()
      .then((data) => {
        setArticles(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Failed to load knowledge base articles.");
        setLoading(false);
      });
  }, []);

  const rows = articles.filter(
    (a) =>
      q === "" ||
      a.title.toLowerCase().includes(q.toLowerCase()) ||
      a.excerpt.toLowerCase().includes(q.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-[1200px] px-4 py-6 md:px-8 md:py-8">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight text-foreground">
            Knowledge base
          </h1>
          <p className="mt-1 text-[13px] text-muted-foreground">
            Playbooks, patterns and reference material Probe draws on during
            investigations.
          </p>
        </div>
      </div>

      <div className="mt-5 relative max-w-lg">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-muted-foreground" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search playbooks…"
          className="h-9 w-full rounded-md border border-border bg-surface pl-8 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground focus:border-primary/60 focus:outline-none focus:ring-2 focus:ring-primary/20"
        />
      </div>

      {loading ? (
        <div className="mt-12 flex flex-col items-center justify-center gap-2 py-12">
          <Loader2 className="size-6 animate-spin text-primary" />
          <span className="text-[13px] text-muted-foreground">Loading organizational memory...</span>
        </div>
      ) : error ? (
        <div className="mt-6 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-4 text-center text-[13px] text-red-400">
          {error}
        </div>
      ) : (
        <div className="mt-6 divide-y divide-border rounded-lg border border-border bg-surface">
          {rows.map((a) => (
            <a
              key={a.id}
              href="#"
              className="group flex items-start gap-4 px-4 py-4 transition-colors hover:bg-elevated/50"
            >
              <div className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-md border border-border bg-background text-muted-foreground">
                <BookOpen className="size-3.5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10.5px] text-muted-foreground">
                    {a.id}
                  </span>
                  <span className="rounded bg-surface-2 px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                    {a.category}
                  </span>
                </div>
                <h3 className="mt-1 text-[13.5px] font-medium text-foreground group-hover:text-primary">
                  {a.title}
                </h3>
                <p className="mt-1 text-[12px] text-muted-foreground line-clamp-2">
                  {a.excerpt}
                </p>
                <div className="mt-2 flex items-center gap-3 text-[11px] text-muted-foreground">
                  <span>{a.reads} reads</span>
                  <span className="text-border-strong">·</span>
                  <span>Updated {a.updated}</span>
                </div>
              </div>
              <ArrowUpRight className="mt-1 size-4 text-muted-foreground group-hover:text-foreground" />
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
