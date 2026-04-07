import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface RewardMetricsProps {
  rewards?: Record<string, number>;
  totalReward?: number;
  currentIteration?: number;
}

const AGENT_DISPLAY_NAMES: Record<string, string> = {
  'pm': 'PM',
  'architect': 'Architect',
  'developer': 'Developer',
  'qa': 'QA',
  'security': 'Security',
  'tech_debt': 'Tech Debt',
  'seo': 'SEO',
  'boss': 'Boss',
};

export function RewardMetrics({ rewards = {}, totalReward = 0, currentIteration = 0 }: RewardMetricsProps) {
  const sortedRewards = Object.entries(rewards)
    .map(([agent, score]) => ({
      agent,
      score: score as number,
      displayName: AGENT_DISPLAY_NAMES[agent] || agent,
    }))
    .sort((a, b) => b.score - a.score);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>Performance Scores</span>
          <span className="text-2xl font-bold text-blue-600">
            {(totalReward || 0).toFixed(1)}/10
          </span>
        </CardTitle>
        <CardDescription>
          Iteration {currentIteration} • Boss Agent Evaluation
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {sortedRewards.length === 0 ? (
          <p className="text-gray-500 text-sm">Awaiting boss agent evaluation...</p>
        ) : (
          sortedRewards.map(({ agent, score, displayName }) => (
            <div key={agent} className="space-y-1">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">{displayName}</span>
                <span className={`text-sm font-bold ${getScoreColor(score)}`}>
                  {score.toFixed(1)}
                </span>
              </div>
              <Progress
                value={score * 10}
                max={100}
                className={`h-2 ${getScoreBarColor(score)}`}
              />
            </div>
          ))
        )}
        {sortedRewards.length > 0 && (
          <div className="pt-3 mt-3 border-t">
            <div className="text-xs text-gray-600">
              <div>✅ Excellent (8+): {sortedRewards.filter((r) => r.score >= 8).length}</div>
              <div>⚠️ Good (6-7): {sortedRewards.filter((r) => r.score >= 6 && r.score < 8).length}</div>
              <div>❌ Needs work (&lt;6): {sortedRewards.filter((r) => r.score < 6).length}</div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function getScoreColor(score: number): string {
  if (score >= 8) return 'text-green-600';
  if (score >= 6) return 'text-yellow-600';
  return 'text-red-600';
}

function getScoreBarColor(score: number): string {
  if (score >= 8) return 'bg-green-200';
  if (score >= 6) return 'bg-yellow-200';
  return 'bg-red-200';
}
