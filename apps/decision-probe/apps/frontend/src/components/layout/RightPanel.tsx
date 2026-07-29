import React, { useRef, useEffect, useState } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Sparkles, Terminal, X } from 'lucide-react';
import { cn } from '@/lib/utils';

export function RightPanel() {
  const { 
    activeWorkspace, 
    isThinking, 
    errorMessage, 
    setIsThinking, 
    setErrorMessage, 
    clearExecutionLogs,
    applyPatches,
    appendLog,
    appendMessage
  } = useWorkspaceStore();
  
  const [chatMessage, setChatMessage] = useState("");
  const chatInputRef = useRef<HTMLTextAreaElement>(null);
  const streamEndRef = useRef<HTMLDivElement>(null);

  const currentLogs = activeWorkspace?.execution_logs || [];
  const currentConversation = activeWorkspace?.conversations || [];

  const thinkingStages = [
    "Analyzing telemetry...",
    "Querying logs...",
    "Correlating evidence...",
    "Generating insights..."
  ];
  const [thinkingStageIndex, setThinkingStageIndex] = useState(0);

  useEffect(() => {
    let interval: any;
    if (isThinking) {
      setThinkingStageIndex(0);
      interval = setInterval(() => {
        setThinkingStageIndex(prev => Math.min(prev + 1, thinkingStages.length - 1));
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [isThinking]);

  useEffect(() => { streamEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [currentConversation, currentLogs, isThinking]);

  const handleChat = async () => {
    if (!chatMessage.trim() || !activeWorkspace || isThinking) return;
    const msg = chatMessage;
    setIsThinking(true);
    setErrorMessage("");
    setChatMessage("");
    clearExecutionLogs();
    
    // Simulate API chat for layout redesign (backend integration should remain identical)
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

  return (
    <aside className="flex h-full w-[380px] shrink-0 flex-col bg-panel border-l border-border-subtle shadow-2xl z-20">
      {/* Header */}
      <div className="flex h-14 shrink-0 items-center justify-between px-5 border-b border-border-subtle/50 bg-panel/80 backdrop-blur-sm">
        <div className="flex items-center gap-2.5">
          <div className="h-6 w-6 rounded bg-accent/10 flex items-center justify-center text-accent">
            <Sparkles size={14} />
          </div>
          <span className="text-[13px] font-semibold text-fg-strong">AI Assistant</span>
          {activeWorkspace && (
            <span className="mono text-[10px] text-fg-muted uppercase ml-2 bg-raised px-1.5 py-0.5 rounded">
              {activeWorkspace.id.substring(0,6)}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {isThinking && (
            <span className="flex items-center gap-1.5 text-[10px] text-accent font-medium uppercase tracking-wider fade-in">
              <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse" /> Processing
            </span>
          )}
          <button className="text-fg-muted hover:text-foreground transition-colors p-1 rounded-md hover:bg-raised">
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Chat History & Logs */}
      <div className="flex-1 min-h-0 overflow-y-auto px-5 py-6 flex flex-col gap-6">
        {errorMessage && (
          <div className="text-[12px] text-danger border border-danger/20 rounded-md bg-danger/5 px-4 py-3 flex items-start gap-2 fade-in">
            <div className="mt-0.5 text-[14px]">⚠️</div>
            <div className="flex-1">{errorMessage}</div>
          </div>
        )}

        {currentConversation.map((msg, i) => (
          <div key={i} className={cn("fade-in flex flex-col gap-1.5", msg.role === 'user' ? "items-end" : "items-start")}>
            <div className="flex items-center gap-2">
              <span className={cn("text-[11px] font-medium", msg.role === 'user' ? 'text-fg-strong' : 'text-accent')}>
                {msg.role === 'user' ? 'You' : 'DecisionVerse'}
              </span>
              <span className="mono text-[9px] text-fg-muted">
                {new Date(msg.timestamp).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
              </span>
            </div>
            <div className={cn(
              "text-[13px] leading-relaxed px-4 py-2.5 rounded-2xl max-w-[90%]",
              msg.role === 'user' 
                ? "bg-raised border border-border-subtle text-foreground rounded-tr-sm" 
                : "bg-accent/10 border border-accent/20 text-foreground rounded-tl-sm"
            )}>
              {msg.content}
            </div>
          </div>
        ))}

        {currentLogs.length > 0 && (
          <div className="mt-2 rounded-xl bg-background border border-border-subtle p-4 shadow-sm fade-in">
            <div className="flex items-center gap-2 mb-3 border-b border-border-subtle pb-2">
              <Terminal size={14} className="text-fg-muted" />
              <span className="text-[11px] font-mono text-fg-muted font-medium tracking-wide uppercase">Execution Trace</span>
            </div>
            <ul className="space-y-2">
              {currentLogs.map((log, i) => (
                <li key={i} className="flex items-start gap-2.5 text-[12px] font-mono">
                  <span className={cn("mt-0.5 text-[11px]", log.success ? 'text-success' : 'text-danger')}>
                    {log.success ? '✓' : '✗'}
                  </span>
                  <span className="min-w-0 flex-1 text-fg-muted leading-relaxed break-words">{log.message}</span>
                </li>
              ))}
              {isThinking && (
                <li className="flex items-center gap-2.5 text-[12px] font-mono text-accent mt-3 fade-in">
                  <span className="animate-spin text-[11px]">⟳</span>
                  <span className="animate-pulse">{thinkingStages[thinkingStageIndex]}</span>
                </li>
              )}
            </ul>
          </div>
        )}

        <div ref={streamEndRef} />
      </div>

      {/* Input Composer */}
      <div className="shrink-0 p-5 pt-2 bg-panel">
        <div className="relative rounded-xl border border-border-subtle bg-background shadow-sm focus-within:border-accent focus-within:ring-1 focus-within:ring-accent/20 transition-all overflow-hidden group">
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
            placeholder="Ask AI to analyze logs, suggest remediations..."
            className="block w-full resize-none bg-transparent px-4 py-3.5 text-[13px] text-foreground placeholder:text-fg-muted focus:outline-none disabled:opacity-50"
          />
          
          <div className="flex items-center justify-between px-3 pb-3">
            <div className="flex gap-1.5 opacity-0 group-focus-within:opacity-100 transition-opacity">
              <button onClick={() => setChatMessage("/investigate ")} className="rounded px-2 py-1 text-[10px] font-mono font-medium text-fg-muted bg-raised hover:text-foreground transition-colors">/investigate</button>
              <button onClick={() => setChatMessage("/analyze ")} className="rounded px-2 py-1 text-[10px] font-mono font-medium text-fg-muted bg-raised hover:text-foreground transition-colors">/analyze</button>
            </div>
            
            <button 
              onClick={handleChat}
              disabled={isThinking || !chatMessage.trim()}
              className="h-7 w-7 rounded-md bg-accent flex items-center justify-center text-white hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
            >
              <span className="text-[14px]">↑</span>
            </button>
          </div>
        </div>
        <div className="text-center mt-3">
          <span className="text-[10px] text-fg-muted">AI can make mistakes. Verify critical actions.</span>
        </div>
      </div>
    </aside>
  );
}
