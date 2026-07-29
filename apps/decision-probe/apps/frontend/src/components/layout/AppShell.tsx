import React from 'react';
import { LeftSidebar } from './LeftSidebar';
import { RightPanel } from './RightPanel';
import { TopNavBar } from './TopNavBar';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background text-foreground font-sans">
      <LeftSidebar />
      
      <div className="flex flex-col flex-1 min-w-0">
        <TopNavBar />
        
        <main className="flex-1 min-h-0 overflow-y-auto bg-background/50 relative">
          {children}
        </main>
      </div>

      <RightPanel />
    </div>
  );
}
