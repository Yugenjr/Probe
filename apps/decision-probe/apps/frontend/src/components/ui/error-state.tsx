import React from 'react';
import { AlertCircle } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ title = "Error", message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-start p-4 bg-danger/5 border border-danger/20 rounded-xl">
      <div className="flex items-center gap-2 text-danger mb-1.5">
        <AlertCircle size={16} />
        <h3 className="text-[13px] font-semibold">{title}</h3>
      </div>
      <p className="text-[12.5px] text-danger/80 mb-3">{message}</p>
      {onRetry && (
        <button 
          onClick={onRetry}
          className="text-[12px] font-medium bg-danger/10 hover:bg-danger/20 text-danger px-3 py-1 rounded transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
}
