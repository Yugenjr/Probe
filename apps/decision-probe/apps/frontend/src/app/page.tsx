"use client";

import React, { useState, useEffect, useRef } from 'react';
import { useWorkspaceStore, Workspace } from '@/store/workspaceStore';
import { BlockRenderer } from '@/components/workspace/BlockRenderer';
import { useDropzone } from 'react-dropzone';
import { SettingsModal } from '@/components/workspace/SettingsModal';
import { workspaceApi } from '@/api/workspace';

export default function Home() {
  const { 
    activeWorkspace, setActiveWorkspace, applyPatches,
    isThinking, setIsThinking,
    errorMessage, setErrorMessage,
    appendMessage, appendLog, clearExecutionLogs
  } = useWorkspaceStore();
  
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [chatMessage, setChatMessage] = useState("");
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isOffline, setIsOffline] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [newTitle, setNewTitle] = useState("");

  const thinkingStages = [
    "Planning investigation",
    "Collecting context",
    "Analyzing evidence",
    "Evaluating hypotheses",
    "Generating decision",
    "Updating workspace"
  ];
  const [thinkingStageIndex, setThinkingStageIndex] = useState(0);

  useEffect(() => { loadWorkspaces(); }, []);

  const loadWorkspaces = async () => {
    setIsLoading(true);
    setIsOffline(false);
    try {
      const data = await workspaceApi.getWorkspaces();
      setWorkspaces(data);
      if (data.length > 0) {
        if (activeWorkspace) {
          const found = data.find(w => w.id === activeWorkspace.id);
          setActiveWorkspace(found || data[0]);
        } else {
          setActiveWorkspace(data[0]);
        }
      } else {
        setActiveWorkspace(null);
      }
    } catch (e) { 
      console.error(e); 
      setIsOffline(true);
    }
    finally { setIsLoading(false); }
  };

  const handleCreateWorkspace = async () => {
    try {
      const ws = await workspaceApi.createWorkspace(`Investigation ${workspaces.length + 1}`);
      setWorkspaces([...workspaces, ws]);
      setActiveWorkspace(ws);
    } catch (e) { console.error(e); }
  };

  const handleRenameSubmit = async () => {
    if (!activeWorkspace || !newTitle.trim() || newTitle === activeWorkspace.title) {
      setIsRenaming(false); return;
    }
    try {
      const updated = await workspaceApi.updateWorkspace(activeWorkspace.id, newTitle);
      setActiveWorkspace(updated);
      setWorkspaces(workspaces.map(w => w.id === updated.id ? updated : w));
    } catch (e) { console.error(e); }
    finally { setIsRenaming(false); }
  };

  const handleDeleteWorkspace = async () => {
    if (!activeWorkspace) return;
    try {
      await workspaceApi.deleteWorkspace(activeWorkspace.id);
      const remaining = workspaces.filter(w => w.id !== activeWorkspace.id);
      setWorkspaces(remaining);
      setActiveWorkspace(remaining.length > 0 ? remaining[0] : null);
    } catch (e) { console.error(e); }
  };

  const onDrop = async (acceptedFiles: File[]) => {
    if (!activeWorkspace || acceptedFiles.length === 0) return;
    try {
      const block = await workspaceApi.uploadResource(activeWorkspace.id, acceptedFiles[0]);
      applyPatches([{ type: 'PatchOperation', operations: [{ op: 'append_block', payload: block }] }]);
    } catch (e) { console.error("Failed to upload resource:", e); }
  };

  const { getInputProps, open } = useDropzone({ onDrop, noClick: true, noKeyboard: true });
  const chatInputRef = useRef<HTMLTextAreaElement>(null);
  const streamEndRef = useRef<HTMLDivElement>(null);
  
  const currentLogs = activeWorkspace?.execution_logs || [];
  const currentConversation = activeWorkspace?.conversations || [];

  useEffect(() => { chatInputRef.current?.focus(); }, [activeWorkspace]);
  useEffect(() => { streamEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [currentConversation, currentLogs]);

  useEffect(() => {
    let interval: any;
    if (isThinking) {
      setThinkingStageIndex(0);
      interval = setInterval(() => {
        setThinkingStageIndex(prev => Math.min(prev + 1, thinkingStages.length - 1));
      }, 1800);
    }
    return () => clearInterval(interval);
  }, [isThinking]);

  const handleChat = async () => {
    if (!chatMessage || !activeWorkspace || isThinking) return;
    const msg = chatMessage;
    setIsThinking(true);
    setErrorMessage("");
    setChatMessage("");
    clearExecutionLogs();
    
    try {
      const response = await fetch(`http://localhost:8005/api/v1/workspaces/${activeWorkspace.id}/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
      if (!response.ok) throw new Error("Investigation failed.");
      if (!response.body) throw new Error("No readable stream");
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let done = false, buffer = "";

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          let eolIndex;
          while ((eolIndex = buffer.indexOf('\n\n')) >= 0) {
            const eventChunk = buffer.slice(0, eolIndex).trim();
            buffer = buffer.slice(eolIndex + 2);
            if (!eventChunk) continue;
            const lines = eventChunk.split('\n');
            let dataStr = "";
            for (const line of lines) { if (line.startsWith('data: ')) dataStr += line.slice(6); }
            dataStr = dataStr.trim();
            if (!dataStr) continue;
            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'error') {
                setErrorMessage(data.content || "Runtime error.");
                setIsThinking(false); break;
              }
              if (data.type === 'PatchOperation') {
                applyPatches([data]);
              } else if (data.type === 'execution_log') {
                appendLog(data.payload);
              } else if (data.type === 'chat_message') {
                appendMessage(data.payload);
              }
            } catch (e) {
              setErrorMessage("Stream parse error.");
            }
          }
        }
      }
    } catch (e: any) {
      setErrorMessage(e.message || "Investigation failed.");
    } finally {
      setIsThinking(false);
      chatInputRef.current?.focus();
    }
  };

  const blocks = activeWorkspace?.blocks || [];
  const hasBlocks = blocks.length > 0;

  if (isOffline) {
    return (
      <div className="flex h-screen items-center justify-center bg-background text-center">
        <div className="flex flex-col items-center gap-4">
          <div className="grid h-12 w-12 place-items-center rounded-full bg-danger/10">
            <span className="text-xl text-danger">⚠️</span>
          </div>
          <div>
            <h2 className="text-base font-medium text-fg-strong">Backend Offline</h2>
            <p className="mt-1 text-[13px] text-fg-muted">Could not connect to the DecisionVerse API.</p>
          </div>
          <button 
            onClick={loadWorkspaces}
            className="mt-2 rounded bg-foreground px-4 py-2 text-[12.5px] font-medium text-background hover:bg-foreground/90 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <input {...getInputProps()} />

      {/* ──── EXPLORER ──── */}
      <aside className="flex h-full w-[260px] min-w-[260px] flex-col bg-panel border-r border-border-subtle">
        {/* header */}
        <div className="flex h-11 shrink-0 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="grid h-4 w-4 place-items-center">
              <span className="block h-2 w-2 rotate-45 bg-accent" />
            </div>
            <span className="text-[13px] font-medium tracking-tight text-fg-strong">DecisionVerse</span>
          </div>
          <button className="text-fg-muted hover:text-foreground">
            <span className="kbd text-[9px]">⌘K</span>
          </button>
        </div>

        {/* search */}
        <div className="px-4 pb-3">
          <div className="relative">
            <span className="absolute left-2.5 top-1.5 text-[11px] text-fg-muted">⌕</span>
            <input 
              type="text" 
              placeholder="Search investigations..." 
              className="w-full rounded-md border border-border-subtle bg-background/50 py-1 pl-7 pr-2 text-[12px] text-foreground placeholder:text-fg-muted focus:border-accent focus:outline-none"
            />
          </div>
        </div>

        {/* scrollable lists */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          {isLoading ? (
            <div className="px-4 py-2 text-[12px] text-fg-muted">Loading...</div>
          ) : (
            <>
              {/* WORKSPACES */}
              <div className="mb-4">
                <div className="group flex items-center justify-between px-4 pb-1">
                  <div className="text-micro text-fg-muted">Workspaces</div>
                  <button onClick={handleCreateWorkspace} className="opacity-0 group-hover:opacity-100 text-fg-muted hover:text-foreground transition-opacity">
                    <span className="mono text-[14px] leading-none">+</span>
                  </button>
                </div>
                <ul>
                  {workspaces.map(ws => {
                    const active = ws.id === activeWorkspace?.id;
                    return (
                      <li key={ws.id}>
                        <button
                          onClick={() => setActiveWorkspace(ws)}
                          className={`group relative flex h-7 w-full items-center gap-2.5 pr-2 pl-4 text-left text-[12.5px] transition-colors ${
                            active ? 'bg-raised text-fg-strong' : 'text-foreground hover:bg-raised/60'
                          }`}
                        >
                          {active && <span className="absolute left-0 top-1 bottom-1 w-[2px] rounded-r bg-accent" />}
                          <span className={`h-1.5 w-1.5 rounded-full ${active ? 'bg-accent' : 'bg-border-subtle'}`} />
                          <span className="min-w-0 flex-1 truncate">{ws.title}</span>
                          <span className="opacity-0 group-hover:opacity-100 text-[10px] text-fg-muted transition-opacity">
                            •••
                          </span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </div>
            </>
          )}
        </div>

        {/* footer */}
        <div className="shrink-0 border-t border-border-subtle px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-5 w-5 rounded-full bg-raised flex items-center justify-center text-[10px] text-fg-strong">U</span>
            <span className="text-[12px] text-fg-strong">User</span>
          </div>
          <button 
            onClick={() => setIsSettingsOpen(true)}
            className="text-fg-muted hover:text-foreground transition-colors"
          >
            <span className="mono text-[14px]">⚙</span>
          </button>
        </div>
      </aside>

      {/* ──── WORKSPACE ──── */}
      <div className="flex h-full min-h-0 flex-1 flex-col bg-background">
        {/* top toolbar */}
        {activeWorkspace ? (
          <div className="flex h-12 shrink-0 items-center justify-between border-b border-border-subtle px-6">
            <div className="flex items-center gap-3">
              <span className="text-fg-muted text-[12.5px]">Production Incidents</span>
              <span className="text-border-subtle">/</span>
              {isRenaming ? (
                <input 
                  autoFocus value={newTitle}
                  onChange={e => setNewTitle(e.target.value)}
                  onBlur={handleRenameSubmit}
                  onKeyDown={e => { if (e.key === 'Enter') handleRenameSubmit(); if (e.key === 'Escape') setIsRenaming(false); }}
                  className="text-[13px] font-medium text-foreground bg-transparent focus:outline-none border-b border-accent min-w-[150px]"
                />
              ) : (
                <span 
                  className="text-[13px] font-medium text-fg-strong cursor-text hover:text-accent transition-colors"
                  onDoubleClick={() => { setNewTitle(activeWorkspace.title); setIsRenaming(true); }}
                >
                  {activeWorkspace.title}
                </span>
              )}
              <div className="flex items-center gap-1.5 ml-2">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider bg-danger/10 text-danger border border-danger/20">Critical</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider bg-info/10 text-info border border-info/20">Investigating</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-[11px] text-fg-muted mr-4">
                Updated {new Date(activeWorkspace.metadata?.updated_at || Date.now()).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
              </span>
              <button className="flex h-6 items-center rounded bg-raised/40 px-2.5 text-[11.5px] font-medium text-foreground hover:bg-raised transition-colors border border-border-subtle">Share</button>
              <button className="flex h-6 items-center rounded bg-raised/40 px-2.5 text-[11.5px] font-medium text-foreground hover:bg-raised transition-colors border border-border-subtle">Export</button>
              <button onClick={open} className="flex h-6 items-center gap-1.5 rounded bg-raised/40 px-2.5 text-[11.5px] font-medium text-foreground hover:bg-raised transition-colors border border-border-subtle">
                Upload <span className="kbd ml-1 border-none bg-transparent">⇧U</span>
              </button>
              <button onClick={handleDeleteWorkspace} className="flex h-6 w-6 items-center justify-center rounded hover:bg-raised text-fg-muted hover:text-danger transition-colors">
                •••
              </button>
            </div>
          </div>
        ) : (
          <div className="h-12 border-b border-border-subtle" />
        )}

        {/* scroll region */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          {activeWorkspace && hasBlocks && (
            <div className="mx-auto max-w-4xl py-6 px-8">
              {/* investigation summary metadata */}
              <div className="mb-8 flex items-center gap-6 text-[12.5px] text-fg-muted">
                <div className="flex items-center gap-2">
                  <span className="text-micro">Started</span>
                  <span className="text-foreground">{new Date(activeWorkspace.metadata?.created_at || Date.now()).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})} UTC</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-micro">Owner</span>
                  <span className="text-foreground">@maya</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-micro">Region</span>
                  <span className="text-foreground mono">us-east-1</span>
                </div>
              </div>

              {/* blocks as sections */}
              <div className="space-y-6">
                {blocks.map(block => (
                  <BlockRenderer key={block.id} block={block} />
                ))}
              </div>
              <div className="h-24" />
            </div>
          )}

          {activeWorkspace && !hasBlocks && (
            <div className="flex flex-col items-center justify-center h-full text-center px-8">
              <div className="grid h-16 w-16 place-items-center rounded-xl bg-raised/50 border border-border-subtle mb-6">
                <span className="text-2xl opacity-50">🔍</span>
              </div>
              <h2 className="text-[15px] font-medium text-fg-strong mb-2">Investigation Workspace</h2>
              <p className="text-[13px] text-fg-muted max-w-[320px] mb-8">
                Upload evidence or provide an incident description to begin the automated investigation.
              </p>
              
              <div className="flex flex-col gap-2 w-64 text-left">
                <button onClick={() => { setChatMessage("Investigate this incident"); chatInputRef.current?.focus(); }} className="flex items-center justify-between px-4 py-2.5 rounded-lg border border-border-subtle bg-raised/30 hover:bg-raised transition-colors group">
                  <span className="text-[12.5px] text-foreground font-medium">Start investigation</span>
                  <span className="text-fg-muted group-hover:text-foreground">→</span>
                </button>
                <button onClick={open} className="flex items-center justify-between px-4 py-2.5 rounded-lg border border-border-subtle bg-raised/30 hover:bg-raised transition-colors group">
                  <span className="text-[12.5px] text-foreground font-medium">Upload evidence files</span>
                  <span className="text-fg-muted group-hover:text-foreground">→</span>
                </button>
              </div>
            </div>
          )}

          {!activeWorkspace && (
            <div className="flex items-center justify-center h-full text-[13px] text-fg-muted">
              Select or create an investigation from the sidebar.
            </div>
          )}
        </div>
      </div>

      {/* ──── COMMAND CENTER ──── */}
      <aside className="flex h-full w-[360px] min-w-[360px] flex-col bg-panel border-l border-border-subtle shadow-xl">
        {/* header */}
        <div className="flex h-12 shrink-0 items-center justify-between px-5 border-b border-border-subtle/50">
          <div className="flex items-center gap-2.5">
            <span className="text-[13px] font-medium text-fg-strong">Command Center</span>
            {activeWorkspace && (
              <span className="mono text-[10px] text-fg-muted uppercase">· {activeWorkspace.id.substring(0,6)}</span>
            )}
          </div>
          {isThinking && (
            <span className="flex items-center gap-1.5 text-[11px] text-info font-medium">
              <span className="animate-spin mono">⟳</span> running
            </span>
          )}
        </div>

        {/* live execution console stream */}
        <div className="flex-1 min-h-0 overflow-y-auto px-5 py-4 flex flex-col gap-5">
          {errorMessage && (
            <div className="text-[12px] text-danger border border-danger/20 rounded-md bg-danger/5 px-3 py-2">
              {errorMessage}
            </div>
          )}

          {currentConversation.map((msg, i) => (
            <div key={i} className="fade-in flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <span className={`text-[11.5px] font-medium ${msg.role === 'user' ? 'text-fg-strong' : 'text-accent'}`}>
                  {msg.role === 'user' ? 'You' : 'DecisionVerse'}
                </span>
                <span className="mono text-[10px] text-fg-muted">
                  {new Date(msg.timestamp).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
                </span>
              </div>
              <div className="text-[13px] text-foreground leading-relaxed">
                {msg.content}
              </div>
              {/* Inline execution logs directly beneath assistant messages if this is the latest one? We'll render logs separate for now. */}
            </div>
          ))}

          {currentLogs.length > 0 && (
            <div className="mt-2 rounded-lg bg-raised/30 border border-border-subtle p-3">
              <div className="text-micro mb-2 text-fg-muted">Execution</div>
              <ul className="space-y-1.5">
                {currentLogs.map((log, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-[12px]">
                    <span className={`mt-0.5 mono text-[10px] ${log.success ? 'text-success' : 'text-danger'}`}>
                      {log.success ? '✓' : '✗'}
                    </span>
                    <span className="min-w-0 flex-1 text-fg-muted leading-snug">{log.message}</span>
                  </li>
                ))}
                {isThinking && (
                  <li className="flex items-center gap-2.5 text-[12px] text-info mt-2">
                    <span className="animate-spin mono text-[10px]">⟳</span>
                    <span>{thinkingStages[thinkingStageIndex]}</span>
                  </li>
                )}
              </ul>
            </div>
          )}

          <div ref={streamEndRef} />
        </div>

        {/* composer */}
        <div className="shrink-0 p-4 pt-0">
          <div className="rounded-xl border border-border-subtle bg-background shadow-sm focus-within:border-accent/50 focus-within:ring-1 focus-within:ring-accent/20 transition-all">
            <textarea
              ref={chatInputRef}
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (!isThinking) handleChat();
                }
              }}
              disabled={isThinking}
              rows={2}
              placeholder="Command or ask a question..."
              className="block w-full resize-none bg-transparent px-3.5 py-3 text-[13px] text-foreground placeholder:text-fg-muted focus:outline-none"
            />
            <div className="flex flex-wrap items-center gap-1.5 px-3 pb-3">
              <button onClick={() => setChatMessage("/investigate ")} className="rounded px-2 py-0.5 text-[11px] font-mono text-fg-muted hover:bg-raised hover:text-foreground transition-colors">/investigate</button>
              <button onClick={() => setChatMessage("/explain ")} className="rounded px-2 py-0.5 text-[11px] font-mono text-fg-muted hover:bg-raised hover:text-foreground transition-colors">/explain</button>
              <button onClick={() => setChatMessage("/diff ")} className="rounded px-2 py-0.5 text-[11px] font-mono text-fg-muted hover:bg-raised hover:text-foreground transition-colors">/diff</button>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}
