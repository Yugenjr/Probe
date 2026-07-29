import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'raised' | 'interactive';
}

export function Card({ className, variant = 'default', ...props }: CardProps) {
  return (
    <div 
      className={cn(
        "rounded-xl border border-border-subtle bg-panel shadow-sm overflow-hidden",
        variant === 'raised' && "shadow-md bg-raised",
        variant === 'interactive' && "hover:border-accent/50 hover:shadow-md cursor-pointer transition-all",
        className
      )} 
      {...props} 
    />
  );
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-5 py-4 flex items-center justify-between border-b border-border-subtle/50", className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h3 className={cn("text-[14px] font-semibold tracking-tight text-fg-strong", className)} {...props} />;
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-5", className)} {...props} />;
}

export function CardFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("px-5 py-3 bg-raised/30 border-t border-border-subtle/50 text-[12px] flex items-center", className)} {...props} />;
}
