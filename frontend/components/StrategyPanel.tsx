import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Strategy {
  agent: string;
  output: string;
  reward: number;
  timestamp?: number;
}

interface StrategyPanelProps {
  jobId: string;
  agentType?: string;
}

export function StrategyPanel({ jobId, agentType }: StrategyPanelProps) {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStrategies = async () => {
      try {
        setLoading(true);
        setError(null);

        const url = agentType
          ? `/api/strategies/${agentType}?jobId=${jobId}`
          : `/api/strategies?jobId=${jobId}`;

        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to fetch strategies');

        const data = await res.json();
        setStrategies(data.strategies || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    if (jobId) {
      fetchStrategies();
      // Refresh every 5 seconds
      const interval = setInterval(fetchStrategies, 5000);
      return () => clearInterval(interval);
    }
  }, [jobId, agentType]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>High-Reward Strategies</CardTitle>
        <CardDescription>
          {agentType ? `${agentType} agent` : 'All agents'} •{' '}
          {strategies.length} strategies loaded
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {loading && (
            <p className="text-gray-500 text-sm">Loading strategies...</p>
          )}
          {error && (
            <p className="text-red-500 text-sm">Error: {error}</p>
          )}
          {!loading && strategies.length === 0 && (
            <p className="text-gray-500 text-sm">No strategies found yet.</p>
          )}
          {strategies.map((strategy, idx) => (
            <div
              key={idx}
              className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <Badge variant="default" className="capitalize">
                  {strategy.agent}
                </Badge>
                <span className="text-sm font-bold text-green-600">
                  {(strategy.reward || 0).toFixed(1)}/10
                </span>
              </div>
              <p className="text-xs text-gray-600 line-clamp-3">
                {strategy.output.substring(0, 150)}
                {strategy.output.length > 150 ? '...' : ''}
              </p>
              {strategy.timestamp && (
                <p className="text-xs text-gray-400 mt-2">
                  {new Date(strategy.timestamp).toLocaleString()}
                </p>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
