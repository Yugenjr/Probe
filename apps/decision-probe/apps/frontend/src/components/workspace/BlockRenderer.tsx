"use client";

import React, { useState, type ReactNode } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
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
import { RiskScoreBlock } from './RiskScoreBlock';
import { PredictionBlock } from './PredictionBlock';
import { AnomalyBlock } from './AnomalyBlock';
import { ReliabilityBlock } from './ReliabilityBlock';
import { DeploymentRiskBlock } from './DeploymentRiskBlock';
import { DependencyGraphBlock } from './DependencyGraphBlock';
import { PreventiveRecommendationBlock } from './PreventiveRecommendationBlock';
import { EvidenceGraphEnhanced } from './EvidenceGraphEnhanced';
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
  failure_patterns: FailurePatternBlock as any,
  risk_score: RiskScoreBlock as any,
  prediction: PredictionBlock as any,
  anomaly: AnomalyBlock as any,
  reliability: ReliabilityBlock as any,
  deployment_risk: DeploymentRiskBlock as any,
  dependency_graph: DependencyGraphBlock as any,
  preventive_recommendation: PreventiveRecommendationBlock as any
};

export function BlockRenderer({ block }: { block: Block }) {
  const Component = BlockRegistry[block.type];
  if (Component) return <Component block={block} />;
  
  if (block.type === 'graph') {
    return <EvidenceGraphEnhanced block={block} />;
  }

  return (
    <Section title={block.type} defaultOpen>
      <pre className="px-4 text-[12.5px] mono text-fg-muted whitespace-pre-wrap overflow-x-auto">
        {JSON.stringify(block.content, null, 2)}
      </pre>
    </Section>
  );
}

/** Shared collapsible section — refactored to use Card design */
export function Section({
  title, count, defaultOpen = true, action, children,
}: {
  title: string; count?: number | string; defaultOpen?: boolean; action?: ReactNode; children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <Card className="w-full mb-4">
      <CardHeader 
        className="cursor-pointer hover:bg-raised/30 transition-colors select-none py-3 px-4" 
        onClick={() => setOpen(v => !v)}
      >
        <div className="flex flex-1 items-center gap-2">
          <span 
            className="mono w-3 text-[14px] text-fg-muted transition-transform duration-200" 
            style={{ transform: open ? 'rotate(90deg)' : 'none' }}
          >
            ›
          </span>
          <CardTitle className="text-[13px]">{title}</CardTitle>
          {count !== undefined && (
            <span className="ml-2 inline-flex items-center rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-medium text-accent">
              {count}
            </span>
          )}
        </div>
        {action && (
          <div className="pr-1" onClick={e => e.stopPropagation()}>
            {action}
          </div>
        )}
      </CardHeader>
      {open && (
        <CardContent className="pt-2 pb-4 px-1 fade-in">
          {children}
        </CardContent>
      )}
    </Card>
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
