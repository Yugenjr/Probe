import React from 'react';
import { FileSearch } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export function EmptyState({ title, description, icon, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-panel border border-dashed border-border-subtle rounded-xl h-full min-h-[200px]">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-raised text-fg-muted mb-4">
        {icon || <FileSearch size={24} />}
      </div>
      <h3 className="text-[14px] font-semibold text-fg-strong">{title}</h3>
      <p className="mt-1 text-[13px] text-fg-muted max-w-sm">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
