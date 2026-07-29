"use client";

import React, { useState, useEffect } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { AppShell } from '@/components/layout/AppShell';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { InvestigationOverview } from '@/components/dashboard/InvestigationOverview';
import { InvestigationPipeline } from '@/components/dashboard/InvestigationPipeline';
import { RootCauseAnalysis } from '@/components/dashboard/RootCauseAnalysis';
import { EvidenceIntelligence } from '@/components/dashboard/EvidenceIntelligence';
import { IncidentResponse } from '@/components/dashboard/IncidentResponse';
import { PredictiveIntelligence } from '@/components/dashboard/PredictiveIntelligence';
import { EmptyState } from '@/components/ui/empty-state';
import { workspaceApi } from '@/api/workspace';
import { useDropzone } from 'react-dropzone';

export default function Home() {
  const { 
    activeWorkspace, 
    isPlanning, 
    setIsPlanning,
    setErrorMessage,
    clearExecutionLogs,
    appendLog,
    setActiveWorkspace,
    indexingDocuments,
    setIndexingDocuments
  } = useWorkspaceStore();

  const [investigationGoal, setInvestigationGoal] = useState("Analyze the uploaded files for anomalies and root causes.");

  useEffect(() => {
    if (!activeWorkspace) return;
    
    const fetchStatus = async () => {
      try {
        const statusData = await workspaceApi.getDocumentStatus(activeWorkspace.id);
        setIndexingDocuments(statusData.documents || []);
      } catch (e) {
        console.error("Failed to fetch document status:", e);
      }
    };
    
    fetchStatus();
    
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, [activeWorkspace, setIndexingDocuments]);

  const handleStartInvestigation = async () => {
    if (!activeWorkspace || isPlanning) return;
    setIsPlanning(true);
    setErrorMessage("");
    clearExecutionLogs();
    appendLog({ message: "Starting lead planner agent...", success: true });
    
    try {
      await workspaceApi.startInvestigation(activeWorkspace.id, investigationGoal);
      appendLog({ message: "Investigation plan generated.", success: true });
      
      const updatedWs = await workspaceApi.getWorkspace(activeWorkspace.id);
      setActiveWorkspace(updatedWs);
    } catch (e: any) {
      setErrorMessage(e.message || "Failed to generate investigation plan.");
      appendLog({ message: "Planning failed.", success: false });
    } finally {
      setIsPlanning(false);
    }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    if (!activeWorkspace || acceptedFiles.length === 0) return;
    try {
      appendLog({ message: `Uploading ${acceptedFiles[0].name}...`, success: true });
      await workspaceApi.uploadDocument(activeWorkspace.id, acceptedFiles[0]);
      appendLog({ message: `Upload completed. Parsing and indexing document...`, success: true });
      
      const statusData = await workspaceApi.getDocumentStatus(activeWorkspace.id);
      setIndexingDocuments(statusData.documents || []);
    } catch (e) { 
      console.error("Failed to upload document:", e); 
      setErrorMessage("Failed to upload document.");
      appendLog({ message: "Upload failed.", success: false });
    }
  };

  const { getInputProps, open } = useDropzone({ onDrop, noClick: true, noKeyboard: true });

  const blocks = activeWorkspace?.blocks || [];
  const hasBlocks = blocks.length > 0;

  // Group blocks by sections
  const getBlocks = (types: string[]) => blocks.filter(b => types.includes(b.type));
  
  const overviewBlocks = getBlocks(['summary', 'severity', 'incident_summary']);
  const pipelineBlocks = getBlocks(['plan', 'hypotheses', 'investigation_iteration']);
  const rcaBlocks = getBlocks(['metric_analysis', 'git_analysis', 'failure_patterns', 'reasoning', 'validation', 'review', 'root_cause']);
  const evidenceBlocks = getBlocks(['evidence', 'external_evidence', 'evidence_request', 'evidence_gap', 'chart', 'graph']);
  const responseBlocks = getBlocks(['incident', 'remediation', 'timeline', 'deployment_changes', 'response_plan', 'communication', 'resolution', 'incident_similarity', 'incident_knowledge', 'learning_recommendations']);
  const predictiveBlocks = getBlocks(['risk_score', 'prediction', 'anomaly', 'reliability', 'deployment_risk', 'dependency_graph', 'preventive_recommendation']);

  return (
    <AppShell>
      <input {...getInputProps()} />
      <div className="mx-auto max-w-6xl py-8 px-6 lg:px-8 fade-in">
        {!activeWorkspace ? (
          <div className="h-[60vh] flex items-center justify-center">
            <EmptyState 
              title="No Investigation Selected" 
              description="Select an investigation from the sidebar or create a new one to begin." 
            />
          </div>
        ) : !hasBlocks ? (
          <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center mb-10">
              <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-accent/20 to-primary/20 border border-accent/20 mb-6 shadow-sm">
                <span className="text-3xl text-accent">✧</span>
              </div>
              <h1 className="text-[24px] font-bold tracking-tight text-fg-strong">New Investigation</h1>
              <p className="mt-2 text-[14px] text-fg-muted max-w-lg mx-auto leading-relaxed">
                Provide an investigation goal and upload system telemetry to initialize the AIOps pipeline.
              </p>
            </div>

            <div className="bg-panel border border-border-subtle rounded-xl p-6 shadow-sm">
              <h3 className="text-[12px] font-bold tracking-widest text-fg-muted uppercase mb-4">1. Provide Context</h3>
              <textarea
                value={investigationGoal}
                onChange={(e) => setInvestigationGoal(e.target.value)}
                placeholder="Describe what you want the agent to investigate..."
                className="w-full rounded-lg border border-border-subtle bg-background px-4 py-3 text-[13.5px] text-foreground focus:border-accent focus:ring-1 focus:ring-accent/20 focus:outline-none min-h-[100px] resize-y"
              />
            </div>

            <div className="bg-panel border border-border-subtle rounded-xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[12px] font-bold tracking-widest text-fg-muted uppercase">2. Upload Evidence</h3>
                <button 
                  onClick={open}
                  className="rounded-md bg-raised px-3 py-1.5 text-[12px] font-medium text-foreground hover:bg-raised/80 transition-colors border border-border-subtle"
                >
                  Browse Files
                </button>
              </div>

              {indexingDocuments.length > 0 ? (
                <ul className="space-y-2">
                  {indexingDocuments.map((doc: any) => (
                    <li key={doc.id} className="flex items-center justify-between text-[13px] rounded-lg border border-border-subtle bg-background px-4 py-3">
                      <div className="flex items-center gap-3">
                        <span className="text-[16px]">📄</span>
                        <span className="font-medium text-foreground truncate">{doc.filename}</span>
                        <span className="text-[10px] uppercase text-fg-muted bg-raised px-1.5 py-0.5 rounded font-mono">{doc.file_type}</span>
                      </div>
                      <div className="text-[11px] font-medium">
                        {doc.status === "pending" && <span className="text-fg-muted">Pending...</span>}
                        {doc.status === "processing" && <span className="text-accent flex items-center gap-1.5"><span className="animate-spin text-[10px]">⟳</span> Processing</span>}
                        {doc.status === "indexed" && <span className="text-success flex items-center gap-1.5">✓ Indexed</span>}
                        {doc.status === "failed" && <span className="text-danger flex items-center gap-1.5">✗ Failed</span>}
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div 
                  onClick={open}
                  className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-border-subtle py-12 text-center cursor-pointer hover:bg-raised/30 transition-all bg-background/50"
                >
                  <div className="h-12 w-12 rounded-full bg-raised flex items-center justify-center mb-3 text-fg-muted">
                    <span className="text-xl">📥</span>
                  </div>
                  <span className="text-[13px] text-fg-strong font-medium">Drag & Drop files here</span>
                  <span className="text-[11.5px] text-fg-muted mt-1">Supports PDF, TXT, MD, LOG</span>
                </div>
              )}
            </div>

            <button
              disabled={isPlanning}
              onClick={handleStartInvestigation}
              className="w-full h-12 flex items-center justify-center gap-2 rounded-xl bg-accent text-[14px] font-semibold text-white shadow-md hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isPlanning ? (
                <>
                  <span className="animate-spin text-[16px]">⟳</span>
                  <span>Agent Planning Investigation...</span>
                </>
              ) : (
                <>
                  <span>Initialize Pipeline</span>
                </>
              )}
            </button>
          </div>
        ) : (
          <div className="space-y-12">
            <DashboardHeader workspace={activeWorkspace} />
            <InvestigationOverview blocks={overviewBlocks} />
            <PredictiveIntelligence blocks={predictiveBlocks} />
            <EvidenceIntelligence blocks={evidenceBlocks} />
            <RootCauseAnalysis blocks={rcaBlocks} />
            <InvestigationPipeline blocks={pipelineBlocks} />
            <IncidentResponse blocks={responseBlocks} />
          </div>
        )}
      </div>
    </AppShell>
  );
}
