"use client";

import React, { useState, type ReactNode } from 'react';
import { ChartBlock } from './ChartBlock';
import { EvidenceBlock } from './EvidenceBlock';
import { DecisionBlock } from './DecisionBlock';
import { TimelineBlock } from './TimelineBlock';
import { IncidentBlock } from './IncidentBlock';
import { ReasoningBlock } from './ReasoningBlock';
import { SummaryBlock } from './SummaryBlock';
import { PlanBlock } from './PlanBlock';
import { HypothesisBlock } from './HypothesisBlock';
import { CriticBlock } from './CriticBlock';
import { ValidationBlock } from './ValidationBlock';
import { RemediationBlock } from './RemediationBlock';
import { EvidenceGapBlock } from './EvidenceGapBlock';
import { EvidenceRequestBlock } from './EvidenceRequestBlock';
import { InvestigationIterationBlock } from './InvestigationIterationBlock';
import { ExternalEvidenceBlock } from './ExternalEvidenceBlock';
import { DeploymentChangeBlock } from './DeploymentChangeBlock';
import { MetricAnalysisBlock } from './MetricAnalysisBlock';
import { GitAnalysisBlock } from './GitAnalysisBlock';
import { IncidentSummaryBlock } from './IncidentSummaryBlock';
import { SeverityBlock } from './SeverityBlock';
import { ResponsePlanBlock } from './ResponsePlanBlock';
import { CommunicationBlock } from './CommunicationBlock';
import { ResolutionBlock } from './ResolutionBlock';
import { KnowledgeBlock } from './KnowledgeBlock';
import { SimilarIncidentBlock } from './SimilarIncidentBlock';
import { LearningRecommendationBlock } from './LearningRecommendationBlock';
import { FailurePatternBlock } from './FailurePatternBlock';
import { Block } from '@/store/workspaceStore';

const BlockRegistry: Record<string, React.FC<{ block: Block }>> = {
  incident: IncidentBlock,
  evidence: EvidenceBlock,
  timeline: TimelineBlock,
  decision: DecisionBlock,
  summary: SummaryBlock,
  chart: ChartBlock,
  reasoning: ReasoningBlock,
  plan: PlanBlock as any,
  hypotheses: HypothesisBlock as any,
  review: CriticBlock as any,
  root_cause: DecisionBlock as any,
  validation: ValidationBlock as any,
  remediation: RemediationBlock as any,
  evidence_gap: EvidenceGapBlock as any,
  evidence_request: EvidenceRequestBlock as any,
  investigation_iteration: InvestigationIterationBlock as any,
  external_evidence: ExternalEvidenceBlock as any,
  deployment_changes: DeploymentChangeBlock as any,
  metric_analysis: MetricAnalysisBlock as any,
  git_analysis: GitAnalysisBlock as any,
  incident_summary: IncidentSummaryBlock as any,
  severity: SeverityBlock as any,
  response_plan: ResponsePlanBlock as any,
  communication: CommunicationBlock as any,
  resolution: ResolutionBlock as any,
  incident_knowledge: KnowledgeBlock as any,
  incident_similarity: SimilarIncidentBlock as any,
  learning_recommendations: LearningRecommendationBlock as any,
  failure_patterns: FailurePatternBlock as any
};

export function BlockRenderer({ block }: { block: Block }) {
  const Component = BlockRegistry[block.type];
  if (Component) return <Component block={block} />;
  
  if (block.type === 'graph') {
    return (
      <Section title="Graph Topology" defaultOpen={false}>
        <div className="bg-raised/20 border border-border-subtle rounded-md p-4 text-[12.5px] text-fg-muted">
          <p className="font-semibold text-foreground">Graph topology data successfully generated and persisted on backend.</p>
          <p className="mt-1 text-[11px]">Nodes and relationships are available via the <code className="mono bg-background px-1.5 py-0.5 rounded text-fg-strong">/api/v1/workspaces/{"{"}workspace_id{"}"}/graph</code> API.</p>
          <details className="mt-3">
            <summary className="cursor-pointer hover:text-foreground transition-colors font-medium text-[11.5px]">View Raw Graph JSON</summary>
            <pre className="mt-2 text-[11.5px] mono whitespace-pre-wrap max-h-60 overflow-y-auto bg-background p-2.5 rounded border border-border-subtle/40">
              {JSON.stringify(block.content, null, 2)}
            </pre>
          </details>
        </div>
      </Section>
    );
  }

  return (
    <Section title={block.type} defaultOpen>
      <pre className="px-4 text-[12.5px] mono text-fg-muted whitespace-pre-wrap overflow-x-auto">
        {JSON.stringify(block.content, null, 2)}
      </pre>
    </Section>
  );
}

/** Shared collapsible section — matches lovable-frontend's Section component exactly */
export function Section({
  title, count, defaultOpen = true, action, children,
}: {
  title: string; count?: number | string; defaultOpen?: boolean; action?: ReactNode; children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className="mb-8">
      <header className="sticky top-0 z-10 flex h-8 items-center bg-background">
        <button
          onClick={() => setOpen(v => !v)}
          className="group flex flex-1 items-center gap-2 pr-2 text-left"
        >
          <span className="mono w-3 text-[11px] text-fg-muted transition-transform" style={{ transform: open ? 'rotate(90deg)' : 'none' }}>›</span>
          <span className="text-micro">{title}</span>
          {count !== undefined && <span className="mono text-[10.5px] text-fg-muted">· {count}</span>}
        </button>
        {action && open && <div className="pr-4">{action}</div>}
      </header>
      {open && <div className="fade-in pt-1 pb-4">{children}</div>}
    </section>
  );
}

/** Row helper — matches lovable-frontend's Row component */
export function Row({ children, onClick }: { children: ReactNode; onClick?: () => void }) {
  return (
    <div
      onClick={onClick}
      className="group flex h-7 cursor-default items-center gap-3 px-4 text-[12.5px] transition-colors hover:bg-raised/50"
    >
      {children}
    </div>
  );
}
