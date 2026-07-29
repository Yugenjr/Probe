import React from 'react';
import { Filter } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FilterBarProps {
  filters: { label: string; value: string; active?: boolean }[];
  onFilterChange: (value: string) => void;
  className?: string;
}

export function FilterBar({ filters, onFilterChange, className }: FilterBarProps) {
  return (
    <div className={cn("flex flex-wrap items-center gap-2", className)}>
      <div className="flex h-7 items-center justify-center px-2 border-r border-border-subtle text-fg-muted mr-1">
        <Filter size={14} />
      </div>
      {filters.map((filter) => (
        <button
          key={filter.value}
          onClick={() => onFilterChange(filter.value)}
          className={cn(
            "h-7 rounded-md px-3 text-[11.5px] font-medium transition-all border",
            filter.active 
              ? "bg-accent/10 border-accent/20 text-accent" 
              : "bg-background border-border-subtle text-fg-muted hover:bg-raised hover:text-foreground"
          )}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}
