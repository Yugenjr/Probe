import { createFileRoute } from "@tanstack/react-router";
import { BookOpen, ArrowUpRight, Search, Loader2, Plus, X } from "lucide-react";
import { useState, useEffect } from "react";
import { fetchKBArticles, KBArticle, createKBArticle } from "../lib/api-client";

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
  const [articles, setArticles] = useState<KBArticle[]>(() => {
    const cached = localStorage.getItem("kb_articles_cache");
    return cached ? JSON.parse(cached) : [];
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New Article Form State
  const [showForm, setShowForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newCategory, setNewCategory] = useState("");
  const [newExcerpt, setNewExcerpt] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = () => {
    setLoading(true);
    fetchKBArticles()
      .then((data) => {
        setArticles(data);
        localStorage.setItem("kb_articles_cache", JSON.stringify(data));
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Failed to load knowledge base articles. Showing cached data.");
        setLoading(false);
      });
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await createKBArticle({ title: newTitle, category: newCategory, excerpt: newExcerpt });
      setShowForm(false);
      setNewTitle("");
      setNewCategory("");
      setNewExcerpt("");
      loadArticles();
    } catch (err) {
      console.error(err);
      alert("Failed to create article");
    } finally {
      setIsSubmitting(false);
    }
  };

  const rows = articles.filter(
    (a) =>
      q === "" ||
      a.title.toLowerCase().includes(q.toLowerCase()) ||
      a.excerpt.toLowerCase().includes(q.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-[1200px] px-4 py-6 md:px-8 md:py-8 relative">
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-[22px] font-semibold tracking-tight text-foreground flex items-center gap-2">
            <BookOpen className="size-5 text-primary" />
            Knowledge base
          </h1>
          <p className="mt-1 text-[13px] text-muted-foreground">
            Playbooks, patterns and reference material Probe draws on during investigations.
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 gap-2"
        >
          <Plus className="size-4" />
          New Article
        </button>
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

      {loading && articles.length === 0 ? (
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

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-xl border border-border bg-surface p-6 shadow-lg shadow-black/10">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-foreground">Create New Article</h2>
              <button
                onClick={() => setShowForm(false)}
                className="rounded-md p-1 text-muted-foreground hover:bg-elevated hover:text-foreground"
              >
                <X className="size-4" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Title</label>
                <input
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  placeholder="e.g. Memory Leak Diagnostic Playbook"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Category</label>
                <input
                  required
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  placeholder="e.g. Pattern, Playbook, Troubleshooting"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Excerpt (Markdown supported)</label>
                <textarea
                  required
                  value={newExcerpt}
                  onChange={(e) => setNewExcerpt(e.target.value)}
                  className="h-24 w-full resize-none rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                  placeholder="Brief description or markdown content..."
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="rounded-md border border-border bg-surface px-4 py-2 text-sm font-medium hover:bg-elevated"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                >
                  {isSubmitting ? <Loader2 className="mr-2 size-4 animate-spin" /> : null}
                  Publish Article
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
