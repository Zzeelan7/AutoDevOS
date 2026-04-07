import { useEffect, useState, useCallback, useRef } from 'react';

export interface JobEvent {
  type: 'agent_log' | 'meeting_message' | 'reward' | 'strategy_stored' | 'iteration_complete';
  agent?: string;
  message?: string;
  reward?: Record<string, number>;
  iteration?: number;
  timestamp: number;
}

export interface JobState {
  jobId: string;
  status: 'running' | 'completed' | 'error' | 'idle';
  events: JobEvent[];
  currentIteration: number;
  totalReward: number;
  isConnected: boolean;
}

export function useJobStream(jobId: string) {
  const [state, setState] = useState<JobState>({
    jobId,
    status: 'idle',
    events: [],
    currentIteration: 0,
    totalReward: 0,
    isConnected: false,
  });

  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/${jobId}`;
      
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setState((prev) => ({ ...prev, isConnected: true }));
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleEvent(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.current.onclose = () => {
        setState((prev) => ({ ...prev, isConnected: false }));
      };

      ws.current.onerror = (err) => {
        console.error('WebSocket error:', err);
        setState((prev) => ({ ...prev, status: 'error' }));
      };
    };

    const handleEvent = (data: any) => {
      const event: JobEvent = {
        type: data.type,
        agent: data.agent,
        message: data.message,
        reward: data.reward,
        iteration: data.iteration,
        timestamp: Date.now(),
      };

      setState((prev) => {
        const newState = {
          ...prev,
          events: [...prev.events, event],
        };

        // Update iteration count
        if (event.type === 'iteration_complete' && event.iteration) {
          newState.currentIteration = event.iteration;
        }

        // Update total reward
        if (event.type === 'reward' && event.reward) {
          const total = Object.values(event.reward).reduce((sum, val) => sum + (val || 0), 0);
          newState.totalReward = total / Object.keys(event.reward).length; // Average
        }

        // Update job status
        if (data.status) {
          newState.status = data.status;
        }

        return newState;
      });
    };

    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [jobId]);

  const clearEvents = useCallback(() => {
    setState((prev) => ({ ...prev, events: [] }));
  }, []);

  return { ...state, clearEvents };
}
