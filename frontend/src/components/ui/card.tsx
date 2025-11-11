import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hover?: boolean;
  glow?: boolean;
}

export function Card({ children, className, hover = false, glow = false, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl p-6",
        hover && "hover:border-purple-500/50 transition-all duration-300",
        glow && "hover:shadow-lg hover:shadow-purple-500/25",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

