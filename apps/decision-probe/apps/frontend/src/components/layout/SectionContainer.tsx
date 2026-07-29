import React from 'react';
import { cn } from '@/lib/utils';

interface SectionContainerProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  headerAction?: React.ReactNode;
}

export function SectionContainer({ 
  title, 
  description, 
  children, 
  className,
  headerAction 
}: SectionContainerProps) {
  return (
    <section className={cn("mb-10 w-full animate-in fade-in slide-in-from-bottom-4 duration-500", className)}>
      {(title || description || headerAction) && (
        <div className="mb-5 flex items-end justify-between">
          <div>
            {title && <h2 className="text-[16px] font-semibold tracking-tight text-fg-strong">{title}</h2>}
            {description && <p className="text-[13px] text-fg-muted mt-1">{description}</p>}
          </div>
          {headerAction && (
            <div className="shrink-0">
              {headerAction}
            </div>
          )}
        </div>
      )}
      <div className="w-full">
        {children}
      </div>
    </section>
  );
}
