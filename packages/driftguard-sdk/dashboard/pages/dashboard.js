import React from 'react';
import Head from 'next/head';
import Layout from '../components/Layout';
import StatCard from '../components/StatCard';
import ModelCard from '../components/ModelCard';
import { useModels } from '../hooks/useModels';
import { withAuth } from '../hooks/useAuth';
import { Terminal, Activity } from 'lucide-react';

function SkeletonCard() {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg p-5 flex flex-col gap-4">
      <div className="flex justify-between">
        <div className="flex gap-3">
          <div className="animate-pulse bg-[var(--border)] w-8 h-8 rounded-md" />
          <div className="flex flex-col gap-2">
            <div className="animate-pulse bg-[var(--border)] w-24 h-3 rounded" />
            <div className="animate-pulse bg-[var(--border)] w-16 h-2 rounded" />
          </div>
        </div>
        <div className="animate-pulse bg-[var(--border)] w-16 h-5 rounded" />
      </div>
      <div className="flex justify-between pt-4 border-t border-[var(--border)]">
        <div className="animate-pulse bg-[var(--border)] w-20 h-10 rounded" />
        <div className="animate-pulse bg-[var(--border)] w-20 h-10 rounded" />
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg p-12 text-center max-w-xl mx-auto">
      <div className="w-12 h-12 rounded-lg bg-[var(--bg-base)] border border-[var(--border)] flex items-center justify-center mx-auto mb-5">
        <Terminal size={20} className="text-[var(--text-primary)]" />
      </div>
      <h3 className="text-[14px] font-semibold text-[var(--text-primary)] mb-2 tracking-tight">
        No models detected
      </h3>
      <p className="text-[13px] text-[var(--text-secondary)] leading-relaxed mb-8 max-w-sm mx-auto">
        Register your first model with the DriftGuard SDK to begin monitoring accuracy, drift, and retraining events.
      </p>

      <div className="text-left bg-[var(--bg-base)] border border-[var(--border)] rounded-md p-4 font-mono text-[12px] leading-relaxed">
        <div className="text-[var(--text-muted)] mb-1"># Install the SDK</div>
        <div className="text-[var(--text-primary)] mb-3">pip install driftguard-sdk</div>
        <div className="text-[var(--text-muted)] mb-1"># Wrap your model</div>
        <div className="text-[var(--text-secondary)]">from driftguard import DriftGuard</div>
        <div className="text-[var(--text-secondary)]">dg = DriftGuard(model_id="my-model")</div>
        <div className="text-[var(--text-secondary)]">model = dg.wrap(sklearn_model)</div>
      </div>
    </div>
  );
}

function Dashboard() {
  const { models, loading, error, lastUpdated, refresh } = useModels();

  const total      = models?.length ?? 0;
  const healthy    = models?.filter(m => m.status === 'healthy').length ?? 0;
  const degraded   = models?.filter(m => m.status === 'degraded').length ?? 0;
  const retraining = models?.filter(m => m.status === 'retraining').length ?? 0;

  return (
    <Layout onRefresh={refresh} lastUpdated={lastUpdated} isRefreshing={loading} error={error}>
      <Head>
        <title>Fleet Overview - DriftGuard</title>
      </Head>

      <div className="flex flex-col gap-6">
        {/* Page header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-[var(--text-primary)] tracking-tight mb-1">
              Model Fleet
            </h1>
            <p className="text-[13px] text-[var(--text-secondary)]">
              {total > 0 ? `${total} model${total > 1 ? 's' : ''} under active monitoring` : 'No models registered yet'}
            </p>
          </div>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <StatCard label="Fleet Monitored"        value={total} />
          <StatCard label="Stable Champion Models" value={healthy} />
          <StatCard label="Drifting (SLA Breach)"  value={degraded} />
          <StatCard label="Active Retraining Loops" value={retraining} />
        </div>

        {/* Models section */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity size={16} className="text-[var(--text-secondary)]" />
              <span className="text-[14px] font-medium text-[var(--text-primary)]">
                Deployed Models
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {loading && (!models || models.length === 0)
              ? [...Array(6)].map((_, i) => <SkeletonCard key={i} />)
              : !models || models.length === 0
                ? <div className="col-span-full"><EmptyState /></div>
                : models.map(model => <ModelCard key={model.model_id} model={model} />)
            }
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default withAuth(Dashboard);
