import React from 'react';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
  children: React.ReactNode;
}

export function Alert({
  variant = 'info',
  title,
  dismissible = false,
  onDismiss,
  className,
  children,
  ...props
}: AlertProps) {
  const variants = {
    success: "bg-green-500/20 border-green-500/30 text-green-300",
    error: "bg-red-500/20 border-red-500/30 text-red-300",
    warning: "bg-yellow-500/20 border-yellow-500/30 text-yellow-300",
    info: "bg-blue-500/20 border-blue-500/30 text-blue-300"
  };
  
  const icons = {
    success: CheckCircle2,
    error: AlertCircle,
    warning: AlertCircle,
    info: Info
  };
  
  const Icon = icons[variant];
  
  return (
    <div
      className={cn(
        "relative rounded-xl p-4 border backdrop-blur-xl",
        variants[variant],
        className
      )}
      role="alert"
      {...props}
    >
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className="font-semibold mb-1">{title}</h4>
          )}
          <div className="text-sm">{children}</div>
        </div>
        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 hover:opacity-70 transition-opacity"
            aria-label="Dismiss alert"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}

