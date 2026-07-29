import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressProps {
  value: number; // 0-100
  className?: string;
  indicatorClassName?: string;
}

export function Progress({ value, className, indicatorClassName }: ProgressProps) {
  return (
    <div className={cn("relative h-2 w-full overflow-hidden rounded-full bg-raised", className)}>
      <div 
        className={cn("h-full w-full flex-1 bg-accent transition-all duration-500 ease-in-out", indicatorClassName)} 
        style={{ transform: `translateX(-${100 - (value || 0)}%)` }} 
      />
    </div>
  );
}
