import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface IterationControlProps {
  currentIteration: number;
  maxIterations?: number;
  isRunning?: boolean;
  onStopClick?: () => void;
}

export function IterationControl({
  currentIteration = 0,
  maxIterations = 3,
  isRunning = false,
  onStopClick,
}: IterationControlProps) {
  const iterationPercent = (currentIteration / maxIterations) * 100;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Iteration Progress</span>
          <Badge variant={isRunning ? 'default' : 'secondary'} className="animate-pulse">
            {isRunning ? 'Running' : 'Complete'}
          </Badge>
        </CardTitle>
        <CardDescription>
          {currentIteration} / {maxIterations} iterations
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            {Array.from({ length: maxIterations }).map((_, i) => (
              <div
                key={i}
                className={`flex-1 mx-1 h-2 rounded-full transition-colors ${
                  i < currentIteration
                    ? 'bg-green-500'
                    : i === currentIteration
                      ? 'bg-yellow-500'
                      : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </div>

        <div className="text-sm text-gray-600 space-y-1">
          <p>✅ Completed iterations: {currentIteration}</p>
          <p>⏳ Remaining: {Math.max(0, maxIterations - currentIteration)}</p>
        </div>

        {isRunning && onStopClick && (
          <Button variant="destructive" onClick={onStopClick} className="w-full">
            Stop Execution
          </Button>
        )}

        {!isRunning && currentIteration >= maxIterations && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-700">✨ All iterations complete!</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
