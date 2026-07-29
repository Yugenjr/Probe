import React, { useState, useEffect } from 'react';
import { useWorkspaceStore, Workspace } from '@/store/workspaceStore';
import { workspaceApi } from '@/api/workspace';
import { 
  Activity, 
  BrainCircuit, 
  Database, 
  FileSearch, 
  GitMerge, 
  History, 
  LayoutDashboard, 
  Plus,
  Settings,
  ShieldAlert
} from 'lucide-react';
import { cn } from '@/lib/utils';

export function LeftSidebar() {
  const { activeWorkspace, setActiveWorkspace } = useWorkspaceStore();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadWorkspaces = async () => {
    setIsLoading(true);
    try {
      const data = await workspaceApi.getWorkspaces();
      setWorkspaces(data);
      if (data.length > 0 && !activeWorkspace) {
        setActiveWorkspace(data[0]);
      }
    } catch (e) { 
      console.error(e); 
    } finally { 
      setIsLoading(false); 
    }
  };

  useEffect(() => { loadWorkspaces(); }, []);

  const handleCreateWorkspace = async () => {
    try {
      const ws = await workspaceApi.createWorkspace(`Investigation ${workspaces.length + 1}`);
      setWorkspaces([...workspaces, ws]);
      setActiveWorkspace(ws);
    } catch (e) { console.error(e); }
  };

  const navGroups = [
    {
      title: "OVERVIEW",
      items: [
        { icon: LayoutDashboard, label: "Dashboard", active: true },
        { icon: Activity, label: "Active Incidents", active: false },
      ]
    },
    {
      title: "INTELLIGENCE",
      items: [
        { icon: BrainCircuit, label: "Predictive Models", active: false },
        { icon: FileSearch, label: "Evidence Graph", active: false },
        { icon: GitMerge, label: "Root Cause Paths", active: false },
      ]
    },
    {
      title: "KNOWLEDGE",
      items: [
        { icon: Database, label: "Runbooks", active: false },
        { icon: History, label: "Past Resolutions", active: false },
      ]
    }
  ];

  return (
    <aside className="flex h-full w-[260px] shrink-0 flex-col bg-panel border-r border-border-subtle z-20">
      {/* Brand Header */}
      <div className="flex h-14 shrink-0 items-center px-5 gap-3 border-b border-border-subtle/50">
        <div className="grid h-7 w-7 place-items-center rounded-md bg-gradient-to-br from-accent to-primary shadow-sm">
          <ShieldAlert size={16} className="text-white" />
        </div>
        <span className="text-[14px] font-bold tracking-tight text-fg-strong">AIOps Center</span>
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto py-4 flex flex-col gap-6">
        
        {/* Primary Navigation */}
        <div className="px-3 flex flex-col gap-6">
          {navGroups.map((group, i) => (
            <div key={i}>
              <div className="px-2 mb-2 text-[10px] font-bold tracking-widest text-fg-muted uppercase">
                {group.title}
              </div>
              <nav className="flex flex-col gap-0.5">
                {group.items.map((item, j) => (
                  <button 
                    key={j}
                    className={cn(
                      "flex items-center gap-3 px-2 py-1.5 rounded-md text-[13px] font-medium transition-all",
                      item.active 
                        ? "bg-accent/10 text-accent" 
                        : "text-fg-muted hover:bg-raised hover:text-foreground"
                    )}
                  >
                    <item.icon size={15} className={cn(item.active ? "text-accent" : "text-fg-muted")} />
                    {item.label}
                  </button>
                ))}
              </nav>
            </div>
          ))}
        </div>

        {/* Workspaces List */}
        <div className="mt-auto px-3">
          <div className="group flex items-center justify-between px-2 mb-2">
            <span className="text-[10px] font-bold tracking-widest text-fg-muted uppercase">Investigations</span>
            <button 
              onClick={handleCreateWorkspace} 
              className="opacity-0 group-hover:opacity-100 text-fg-muted hover:text-foreground hover:bg-raised p-0.5 rounded transition-all"
            >
              <Plus size={14} />
            </button>
          </div>
          
          <div className="flex flex-col gap-0.5">
            {isLoading ? (
              <div className="px-2 py-2 text-[12px] text-fg-muted flex items-center gap-2">
                <div className="h-3 w-3 rounded-full border-2 border-accent border-r-transparent animate-spin" />
                Loading...
              </div>
            ) : workspaces.length === 0 ? (
              <div className="px-2 py-2 text-[12px] text-fg-muted">No active investigations</div>
            ) : (
              workspaces.map(ws => {
                const active = ws.id === activeWorkspace?.id;
                return (
                  <button
                    key={ws.id}
                    onClick={() => setActiveWorkspace(ws)}
                    className={cn(
                      "group relative flex items-center gap-2.5 px-2 py-1.5 rounded-md text-left text-[12.5px] transition-colors",
                      active ? 'bg-raised text-fg-strong font-medium' : 'text-fg-muted hover:bg-raised/60 hover:text-foreground'
                    )}
                  >
                    {active && <span className="absolute left-0 top-1.5 bottom-1.5 w-[2px] rounded-r bg-accent" />}
                    <span className={cn(
                      "h-1.5 w-1.5 rounded-full shrink-0", 
                      active ? 'bg-accent' : 'bg-border-subtle group-hover:bg-fg-muted'
                    )} />
                    <span className="min-w-0 flex-1 truncate">{ws.title}</span>
                  </button>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Footer Settings */}
      <div className="shrink-0 p-4 border-t border-border-subtle/50 mt-auto">
        <button className="flex w-full items-center gap-3 px-2 py-2 rounded-md text-[13px] font-medium text-fg-muted hover:bg-raised hover:text-foreground transition-all">
          <Settings size={15} />
          Workspace Settings
        </button>
      </div>
    </aside>
  );
}
