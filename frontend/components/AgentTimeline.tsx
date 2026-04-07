import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { JobEvent } from '@/hooks/useJobStream';

interface AgentTimelineProps {
  events: JobEvent[];
  currentAgent?: string;
}

const AGENT_COLORS: Record<string, string> = {
  'pm': 'bg-blue-100 text-blue-900',
  'architect': 'bg-purple-100 text-purple-900',
  'developer': 'bg-green-100 text-green-900',
  'qa': 'bg-yellow-100 text-yellow-900',
  'security': 'bg-red-100 text-red-900',
  'tech_debt': 'bg-orange-100 text-orange-900',
  'seo': 'bg-cyan-100 text-cyan-900',
  'boss': 'bg-pink-100 text-pink-900',
};

const EVENT_ICONS: Record<string, string> = {
  'agent_log': '🔄',
  'meeting_message': '💬',
  'reward': '🏆',
  'strategy_stored': '💾',
  'iteration_complete': '✅',
};

export function AgentTimeline({ events, currentAgent }: AgentTimelineProps) {
  const displayEvents = events.slice(-20); // Show latest 20 events

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Agent Activity Timeline</CardTitle>
        <CardDescription>Real-time agent execution flow</CardDescription>
      </CardHeader>
      <CardContent className="overflow-y-auto max-h-96">
        <div className="space-y-3">
          {displayEvents.length === 0 ? (
            <p className="text-gray-500 text-sm">Waiting for agent activity...</p>
          ) : (
            displayEvents.map((event, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg border-l-4 ${
                  event.agent ? AGENT_COLORS[event.agent] || 'bg-gray-100' : 'bg-gray-100'
                } ${currentAgent === event.agent ? 'ring-2 ring-offset-1 ring-yellow-300' : ''}`}
              >
                <div className="flex items-start gap-2">
                  <span className="text-lg">{EVENT_ICONS[event.type] || '•'}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      {event.agent && (
                        <Badge variant="secondary" className="capitalize text-xs">
                          {event.agent.replace('_', ' ')}
                        </Badge>
                      )}
                      {event.iteration !== undefined && (
                        <Badge variant="outline" className="text-xs">
                          Iteration {event.iteration}
                        </Badge>
                      )}
                      <span className="text-xs text-gray-500">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    {event.message && (
                      <p className="text-sm mt-1 break-words">{event.message}</p>
                    )}
                    {event.reward && (
                      <div className="text-xs text-gray-600 mt-1">
                        {Object.entries(event.reward).map(([agent, score]) => (
                          <div key={agent}>
                            {agent}: {(score as number).toFixed(1)}/10
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
