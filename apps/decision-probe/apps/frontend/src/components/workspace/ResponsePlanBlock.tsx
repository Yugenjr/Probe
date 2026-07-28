"use client";

import React from 'react';
import { Section } from './BlockRenderer';

export interface TaskItem {
  title: string;
  priority: "high" | "medium" | "low" | string;
  owner: string;
  status: "pending" | "in_progress" | "completed" | string;
}

export interface ResponsePlanBlockProps {
  block: {
    id: string;
    type: string;
    content: {
      tasks?: TaskItem[];
    };
  };
}

export function ResponsePlanBlock({ block }: ResponsePlanBlockProps) {
  const content = block.content || {};
  const tasks = content.tasks || [];

  const priorityColor = (prio: string) => {
    switch (prio.toLowerCase()) {
      case "high":
        return "text-danger bg-danger/10 border-danger/20";
      case "medium":
        return "text-warning bg-warning/10 border-warning/20";
      default:
        return "text-accent bg-accent/10 border-accent/20";
    }
  };

  return (
    <Section title="Incident Response Task Plan" count={tasks.length}>
      <div className="mx-2 rounded-xl border border-border bg-panel/30 p-5 shadow-sm">
        {tasks.length > 0 ? (
          <div className="space-y-3.5">
            {tasks.map((task, idx) => (
              <div key={idx} className="flex items-start md:items-center justify-between gap-4 border border-border-subtle/50 bg-raised/10 rounded-xl p-4 text-[12.5px]">
                <div className="flex items-start gap-3">
                  {/* Task checkbox */}
                  <input 
                    type="checkbox" 
                    checked={task.status === "completed"} 
                    readOnly 
                    className="h-4 w-4 rounded border-border-subtle/80 text-accent bg-raised/10 focus:ring-0 focus:ring-offset-0 pointer-events-none mt-0.5 md:mt-0"
                  />
                  <div className="space-y-1">
                    <p className={`font-semibold text-foreground ${task.status === "completed" ? "line-through text-fg-muted" : ""}`}>
                      {task.title}
                    </p>
                    <div className="flex flex-wrap items-center gap-2 text-[11px] text-fg-muted">
                      <span>Owner: <strong className="text-foreground/80 font-medium">{task.owner}</strong></span>
                      <span>•</span>
                      <span>Status: <strong className="text-foreground/80 font-medium">{task.status}</strong></span>
                    </div>
                  </div>
                </div>

                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${priorityColor(task.priority)}`}>
                  {task.priority}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[12.5px] text-fg-muted italic">No tickets generated in response plan.</p>
        )}
      </div>
    </Section>
  );
}
