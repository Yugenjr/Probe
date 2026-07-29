import React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'outline' | 'secondary';
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold tracking-wider uppercase whitespace-nowrap",
        {
          'bg-accent text-white': variant === 'default',
          'bg-success/10 text-success ring-1 ring-inset ring-success/20': variant === 'success',
          'bg-warning/10 text-warning ring-1 ring-inset ring-warning/20': variant === 'warning',
          'bg-danger/10 text-danger ring-1 ring-inset ring-danger/20': variant === 'danger',
          'bg-info/10 text-info ring-1 ring-inset ring-info/20': variant === 'info',
          'bg-raised text-foreground': variant === 'secondary',
          'border border-border-subtle text-fg-muted': variant === 'outline',
        },
        className
      )}
      {...props}
    />
  );
}
