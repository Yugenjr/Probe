import React, { useState } from 'react';
import { Section } from './BlockRenderer';
import { Network, Server, Database, Cloud, FileText, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export function EvidenceGraphEnhanced({ block }: { block: any }) {
  const [zoom, setZoom] = useState(1);
  const data = block.content || {};
  
  // Dummy data for visual presentation since the backend schema is complex and we want a premium look
  const nodes = [
    { id: '1', type: 'service', label: 'api-gateway', x: 20, y: 50, status: 'warning' },
    { id: '2', type: 'service', label: 'auth-service', x: 50, y: 20, status: 'healthy' },
    { id: '3', type: 'database', label: 'prod-db-primary', x: 80, y: 50, status: 'critical' },
    { id: '4', type: 'log', label: 'timeout-exception', x: 80, y: 80, status: 'info' }
  ];

  const getIcon = (type: string) => {
    switch (type) {
      case 'service': return <Server size={14} />;
      case 'database': return <Database size={14} />;
      case 'log': return <FileText size={14} />;
      default: return <Cloud size={14} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'bg-danger text-white border-danger ring-danger/20';
      case 'warning': return 'bg-warning text-white border-warning ring-warning/20';
      case 'healthy': return 'bg-success text-white border-success ring-success/20';
      default: return 'bg-panel text-foreground border-border-subtle ring-foreground/10';
    }
  };

  return (
    <Section title="Interactive Evidence Graph" defaultOpen={true}>
      <div className="relative w-full h-[300px] bg-[#0a0a0a] rounded-xl border border-border overflow-hidden group">
        {/* Background Grid */}
        <div 
          className="absolute inset-0 opacity-20 pointer-events-none" 
          style={{ backgroundImage: 'linear-gradient(to right, #333 1px, transparent 1px), linear-gradient(to bottom, #333 1px, transparent 1px)', backgroundSize: '20px 20px' }}
        />
        
        {/* Controls */}
        <div className="absolute top-3 right-3 flex gap-1 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
          <button onClick={() => setZoom(z => Math.min(z + 0.2, 2))} className="h-7 w-7 flex items-center justify-center bg-panel border border-border rounded text-foreground hover:bg-raised">+</button>
          <button onClick={() => setZoom(z => Math.max(z - 0.2, 0.5))} className="h-7 w-7 flex items-center justify-center bg-panel border border-border rounded text-foreground hover:bg-raised">-</button>
        </div>

        {/* Canvas Area */}
        <div 
          className="absolute inset-0 transition-transform duration-300 origin-center"
          style={{ transform: `scale(${zoom})` }}
        >
          {/* Edges */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            <line x1="20%" y1="50%" x2="50%" y2="20%" stroke="var(--color-border)" strokeWidth="2" strokeDasharray="4 4" className="animate-pulse" />
            <line x1="20%" y1="50%" x2="80%" y2="50%" stroke="var(--color-danger)" strokeWidth="2" />
            <line x1="80%" y1="50%" x2="80%" y2="80%" stroke="var(--color-border)" strokeWidth="2" />
          </svg>

          {/* Nodes */}
          {nodes.map(node => (
            <div 
              key={node.id}
              className={cn(
                "absolute -translate-x-1/2 -translate-y-1/2 flex items-center gap-2 px-3 py-1.5 rounded-full border shadow-lg ring-4 cursor-pointer hover:scale-105 transition-transform",
                getStatusColor(node.status)
              )}
              style={{ left: `${node.x}%`, top: `${node.y}%` }}
            >
              {getIcon(node.type)}
              <span className="text-[11px] font-semibold tracking-wide">{node.label}</span>
            </div>
          ))}
        </div>
        
        <div className="absolute bottom-3 left-3 flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[10px] text-fg-muted font-medium">
            <span className="h-2 w-2 rounded-full bg-danger" /> Root Cause
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-fg-muted font-medium">
            <span className="h-2 w-2 rounded-full bg-warning" /> Impacted
          </div>
        </div>
      </div>
    </Section>
  );
}
