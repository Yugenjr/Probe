import React from 'react';
import { cn } from '@/lib/utils';

interface TabsProps {
  value: string;
  onValueChange: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

export function Tabs({ value, onValueChange, children, className }: TabsProps) {
  // Simple context-less tabs for this specific implementation
  // We'll pass the state down by cloning elements for simplicity in this architecture
  return (
    <div className={cn("w-full", className)}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { value, onValueChange } as any);
        }
        return child;
      })}
    </div>
  );
}

export function TabsList({ children, className, value, onValueChange }: any) {
  return (
    <div className={cn("inline-flex h-9 items-center justify-center rounded-lg bg-raised p-1 text-fg-muted", className)}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child, { activeValue: value, onValueChange } as any);
        }
        return child;
      })}
    </div>
  );
}

export function TabsTrigger({ value, children, className, activeValue, onValueChange }: any) {
  const isActive = activeValue === value;
  return (
    <button
      type="button"
      onClick={() => onValueChange(value)}
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-[12.5px] font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent disabled:pointer-events-none disabled:opacity-50",
        isActive ? "bg-panel text-foreground shadow-sm" : "hover:text-foreground hover:bg-panel/50",
        className
      )}
    >
      {children}
    </button>
  );
}

export function TabsContent({ value, children, className, activeValue }: any) {
  if (value !== activeValue) return null;
  return (
    <div className={cn("mt-4 animate-in fade-in duration-300", className)}>
      {children}
    </div>
  );
}
