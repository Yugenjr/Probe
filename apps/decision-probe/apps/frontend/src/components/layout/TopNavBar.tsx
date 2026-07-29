import React, { useState } from 'react';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { Bell, Search, LayoutDashboard, Settings, User } from 'lucide-react';
import { workspaceApi } from '@/api/workspace';

export function TopNavBar() {
  const { activeWorkspace, setActiveWorkspace } = useWorkspaceStore();
  const [isRenaming, setIsRenaming] = useState(false);
  const [newTitle, setNewTitle] = useState("");

  const handleRenameSubmit = async () => {
    if (!activeWorkspace || !newTitle.trim() || newTitle === activeWorkspace.title) {
      setIsRenaming(false); 
      return;
    }
    try {
      const updated = await workspaceApi.updateWorkspace(activeWorkspace.id, newTitle);
      setActiveWorkspace(updated);
      // We would ideally also update the workspace list in a higher store, but for now we'll just update active.
    } catch (e) { 
      console.error(e); 
    } finally { 
      setIsRenaming(false); 
    }
  };

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border-subtle bg-panel/50 px-6 backdrop-blur-md z-10 sticky top-0">
      <div className="flex items-center gap-4">
        {/* Breadcrumb / Title */}
        {activeWorkspace ? (
          <div className="flex items-center gap-3 fade-in">
            <span className="text-fg-muted text-[13px] font-medium hidden sm:inline-flex items-center gap-2">
              <LayoutDashboard size={14} />
              Investigations
            </span>
            <span className="text-border-subtle hidden sm:inline">/</span>
            {isRenaming ? (
              <input 
                autoFocus 
                value={newTitle}
                onChange={e => setNewTitle(e.target.value)}
                onBlur={handleRenameSubmit}
                onKeyDown={e => { 
                  if (e.key === 'Enter') handleRenameSubmit(); 
                  if (e.key === 'Escape') setIsRenaming(false); 
                }}
                className="text-[14px] font-semibold text-foreground bg-transparent focus:outline-none border-b border-accent min-w-[200px]"
              />
            ) : (
              <span 
                className="text-[14px] font-semibold text-fg-strong cursor-text hover:text-accent transition-colors"
                onDoubleClick={() => { setNewTitle(activeWorkspace.title); setIsRenaming(true); }}
              >
                {activeWorkspace.title}
              </span>
            )}
            
            {/* Status Badges */}
            <div className="flex items-center gap-1.5 ml-3">
              <span className="inline-flex items-center rounded-full bg-danger/10 px-2 py-0.5 text-[10px] font-medium text-danger ring-1 ring-inset ring-danger/20">
                CRITICAL
              </span>
              <span className="inline-flex items-center rounded-full bg-info/10 px-2 py-0.5 text-[10px] font-medium text-info ring-1 ring-inset ring-info/20">
                INVESTIGATING
              </span>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-fg-strong">
            <div className="grid h-5 w-5 place-items-center rounded bg-accent">
              <span className="block h-2.5 w-2.5 rotate-45 bg-white" />
            </div>
            <span className="text-[14px] font-semibold tracking-tight">DecisionVerse AIOps</span>
          </div>
        )}
      </div>
      
      {/* Right Tools */}
      <div className="flex items-center gap-4">
        {activeWorkspace && (
          <span className="text-[11px] text-fg-muted hidden md:inline">
            Updated {new Date(activeWorkspace.metadata?.updated_at || Date.now()).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}
          </span>
        )}
        
        <div className="flex items-center gap-1 border-l border-border-subtle pl-4 ml-2">
          <button className="flex h-8 w-8 items-center justify-center rounded-md text-fg-muted hover:bg-raised hover:text-foreground transition-colors">
            <Search size={15} />
          </button>
          <button className="relative flex h-8 w-8 items-center justify-center rounded-md text-fg-muted hover:bg-raised hover:text-foreground transition-colors">
            <Bell size={15} />
            <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-accent ring-2 ring-panel"></span>
          </button>
          <button className="flex h-8 w-8 items-center justify-center rounded-md text-fg-muted hover:bg-raised hover:text-foreground transition-colors">
            <Settings size={15} />
          </button>
          <div className="ml-2 flex items-center gap-2 cursor-pointer rounded-full p-1 pr-2 hover:bg-raised transition-colors border border-transparent hover:border-border-subtle">
            <div className="h-6 w-6 rounded-full bg-gradient-to-tr from-accent to-primary flex items-center justify-center text-[10px] text-white font-medium shadow-sm">
              M
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
