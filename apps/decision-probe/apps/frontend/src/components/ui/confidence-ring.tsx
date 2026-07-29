import React from 'react';
import { cn } from '@/lib/utils';

interface ConfidenceRingProps {
  score: number; // 0.0 to 1.0
  size?: number;
  strokeWidth?: number;
  className?: string;
  showText?: boolean;
}

export function ConfidenceRing({ 
  score, 
  size = 40, 
  strokeWidth = 4, 
  className,
  showText = true 
}: ConfidenceRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const percent = Math.min(100, Math.max(0, score * 100));
  const offset = circumference - (percent / 100) * circumference;

  let colorClass = "text-success";
  if (percent < 50) colorClass = "text-danger";
  else if (percent < 80) colorClass = "text-warning";

  return (
    <div className={cn("relative flex items-center justify-center", className)} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background ring */}
        <circle
          className="text-raised stroke-current"
          strokeWidth={strokeWidth}
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        {/* Progress ring */}
        <circle
          className={cn("stroke-current transition-all duration-1000 ease-out", colorClass)}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          fill="transparent"
          r={radius}
          cx={size / 2}
          cy={size / 2}
          style={{ strokeDasharray: circumference, strokeDashoffset: offset }}
        />
      </svg>
      {showText && (
        <span className={cn("absolute text-[10px] font-bold", colorClass)}>
          {Math.round(percent)}%
        </span>
      )}
    </div>
  );
}
