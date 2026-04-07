'use client';

import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Loader, ChevronRight, AlertCircle, CheckCircle, Zap } from 'lucide-react';

interface JobData {
  jobId: string;
  prompt: string;
  status: string;
  iterations: number;
  current_iteration: number;
  overall_reward: number;
  created_at: string;
}

interface EventData {
  type: string;
  agent?: string;
  message?: string;
  content?: string;
  reward?: number;
  timestamp?: string;
}

export default function JobDashboard() {
  const params = useParams();
  const jobId = params.jobId as string;
  const [job, setJob] = useState<JobData | null>(null);
  const [events, setEvents] = useState<EventData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Fetch job details
  useEffect(() => {
    const fetchJob = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/jobs/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          setJob(data);
        } else {
          setError('Failed to load job');
        }
      } catch (err) {
        setError('Failed to fetch job details');
      } finally {
        setLoading(false);
      }
    };

    fetchJob();
    
    // Poll for job updates
    const interval = setInterval(fetchJob, 2000);
    return () => clearInterval(interval);
  }, [jobId]);

  // Fetch website preview when job is completed or at intervals
  useEffect(() => {
    const fetchPreview = async () => {
      if (!jobId) return;
      
      try {
        const res = await fetch(`http://localhost:8000/api/jobs/${jobId}/preview`);
        if (res.ok) {
          setPreviewUrl(`http://localhost:8000/api/jobs/${jobId}/preview`);
        } else {
          setPreviewUrl(null);
        }
      } catch (err) {
        setPreviewUrl(null);
      }
    };

    const interval = setInterval(fetchPreview, 5000);
    fetchPreview();
    
    return () => clearInterval(interval);
  }, [jobId]);

  // WebSocket connection
  useEffect(() => {
    const wsUrl = `ws://localhost:8000/ws/${jobId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setWsConnected(true);
    };

    ws.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data);
        setEvents((prev) => [...prev, event]);
      } catch (err) {
        console.error('Failed to parse event:', err);
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [jobId]);

  const calculateProgress = () => {
    if (!job) return 0;
    
    const agentNames = ['pm', 'architect', 'developer', 'qa', 'security', 'tech_debt', 'seo', 'boss'];
    const executedAgents = new Set(
      events.filter(e => e.agent && agentNames.includes(e.agent)).map(e => e.agent)
    );
    
    const iterationProgress = (job.current_iteration - 1) * 100 / (job.iterations || 3);
    const agentInIterationProgress = (executedAgents.size / agentNames.length) * (100 / (job.iterations || 3));
    const eventWeight = Math.min(events.length * 2, 15);
    
    let progress = iterationProgress + agentInIterationProgress + eventWeight;
    
    if (job.status === 'completed') return 100;
    if (job.status === 'error') return Math.min(progress, 100);
    
    return Math.min(progress, 95);
  };

  const getProgressStage = () => {
    if (!job) return 'Initializing...';
    
    const agentNames = ['pm', 'architect', 'developer', 'qa', 'security', 'tech_debt', 'seo', 'boss'];
    const lastAgentEvent = events
      .filter(e => e.agent && agentNames.includes(e.agent))
      .pop();
    
    const rewardEvents = events.filter(e => e.type === 'reward');
    const lastReward = rewardEvents.length > 0 ? rewardEvents[rewardEvents.length - 1].reward : null;
    
    if (lastAgentEvent) {
      const agentLabel = lastAgentEvent.agent?.split('_').pop()?.toUpperCase() || 'UNKNOWN';
      return `${agentLabel} Agent${lastReward ? ` — Score: ${lastReward.toFixed(1)}/10` : ''}`;
    }
    
    return job.status === 'queued' ? 'Queued — Waiting to start...' : job.status;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader className="w-12 h-12 text-cyan-400 animate-spin mx-auto mb-4" />
              <p className="text-gray-300">Loading job details...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const progress = calculateProgress();
  const progressStage = getProgressStage();

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
        <div className="max-w-6xl mx-auto">
          <Link href="/" className="text-cyan-400 hover:text-cyan-300 flex items-center gap-2 mb-6">
            <ChevronRight className="w-4 h-4 rotate-180" />
            Back to home
          </Link>
          <div className="glass border-red-500/50 p-8 rounded-xl">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-8 h-8 text-red-400" />
              <div>
                <h2 className="text-lg font-semibold text-red-300">Error</h2>
                <p className="text-gray-400">{error}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="text-cyan-400 hover:text-cyan-300 flex items-center gap-2 mb-4 text-sm">
            <ChevronRight className="w-4 h-4 rotate-180" />
            Back to home
          </Link>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">Generation Status</h1>
              <p className="text-gray-400 font-mono text-sm">{jobId}</p>
            </div>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-6">
          {/* Progress Card */}
          <div className="md:col-span-2 glass border-white/10 p-8 rounded-xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-white">Build Progress</h2>
              <span className={`text-2xl font-bold ${progress === 100 ? 'text-emerald-400' : 'text-cyan-400'}`}>
                {Math.round(progress)}%
              </span>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="relative w-full h-3 bg-white/5 rounded-full overflow-hidden border border-white/10">
                <div
                  className={`h-full transition-all duration-300 rounded-full ${
                    job?.status === 'completed'
                      ? 'bg-gradient-to-r from-emerald-500 to-emerald-400'
                      : job?.status === 'error'
                      ? 'bg-gradient-to-r from-red-500 to-red-400'
                      : 'bg-gradient-to-r from-cyan-500 to-blue-500'
                  }`}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Status Badges */}
            <div className="flex items-center gap-3 flex-wrap">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                job?.status === 'running'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                  : job?.status === 'completed'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : job?.status === 'error'
                  ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                  : 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
              }`}>
                {job?.status === 'running' ? '🔄' : job?.status === 'completed' ? '✅' : job?.status === 'error' ? '❌' : '⏳'} {' '}
                {job?.status.charAt(0).toUpperCase() + job?.status.slice(1)}
              </div>

              <div className={`px-3 py-1 rounded-full text-sm font-medium border ${
                wsConnected
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                  : 'bg-gray-500/20 text-gray-300 border-gray-500/30'
              }`}>
                {wsConnected ? '🟢' : '🔴'} WebSocket
              </div>

              <div className="px-3 py-1 rounded-full text-sm font-medium bg-blue-500/20 text-blue-300 border border-blue-500/30">
                {events.length} events
              </div>
            </div>

            {/* Stage Info */}
            <div className="mt-6 pt-6 border-t border-white/10">
              <p className="text-xs text-gray-500 mb-2">CURRENT STAGE</p>
              <p className="text-lg font-semibold text-white">{progressStage}</p>
              <div className="mt-4 grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-xs text-gray-500">Iteration</p>
                  <p className="text-lg font-bold text-cyan-400">{job?.current_iteration}/{job?.iterations}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Reward</p>
                  <p className="text-lg font-bold text-emerald-400">{job?.overall_reward?.toFixed(2) || '0'}/10</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Started</p>
                  <p className="text-lg font-bold text-gray-300">
                    {job?.created_at ? new Date(job.created_at).toLocaleTimeString() : '—'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Info Card */}
          <div className="glass border-white/10 p-6 rounded-xl flex flex-col">
            <h3 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wide">Description</h3>
            <p className="text-sm text-gray-300 leading-relaxed mb-6 flex-grow">
              {job?.prompt}
            </p>
            
            {previewUrl && (
              <a
                href={previewUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="button-primary w-full text-center justify-center text-sm"
              >
                👀 Preview Website
              </a>
            )}
          </div>
        </div>

        {/* Events Log */}
        <div className="glass border-white/10 p-8 rounded-xl">
          <h2 className="text-lg font-semibold text-white mb-4">Event Log</h2>
          <div className="space-y-3 max-h-96 overflow-y-auto scrollbar-hidden">
            {events.length === 0 ? (
              <div className="text-center py-8">
                <Loader className="w-8 h-8 text-cyan-400/30 animate-spin mx-auto mb-2" />
                <p className="text-gray-500 text-sm">Waiting for agent events...</p>
              </div>
            ) : (
              [...events].reverse().map((event, idx) => (
                <div
                  key={events.length - 1 - idx}
                  className="p-4 bg-white/5 rounded-lg border border-white/10 hover:border-white/20 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0">
                      {event.type === 'reward' && <span className="text-emerald-400">⭐</span>}
                      {event.type === 'agent_log' && <span className="text-cyan-400">●</span>}
                      {event.type === 'error' && <span className="text-red-400">✕</span>}
                      {event.type === 'job_started' && <span className="text-blue-400">▶</span>}
                      {event.type === 'job_completed' && <span className="text-emerald-400">✓</span>}
                    </div>
                    <div className="flex-grow min-w-0 text-sm">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="font-mono text-xs text-gray-500">{event.type}</span>
                        {event.agent && (
                          <span className="px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded text-xs">
                            {event.agent}
                          </span>
                        )}
                        {event.reward && (
                          <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded text-xs">
                            {event.reward.toFixed(1)}/10
                          </span>
                        )}
                      </div>
                      {event.content && (
                        <p className="text-gray-300 text-sm leading-relaxed break-words">
                          {event.content.substring(0, 200)}
                          {event.content.length > 200 ? '...' : ''}
                        </p>
                      )}
                      {event.message && (
                        <p className="text-gray-400 text-xs">{event.message}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Preview Section */}
        {previewUrl && (
          <div className="glass border-white/10 p-8 rounded-xl mt-6">
            <h2 className="text-lg font-semibold text-white mb-4">Website Preview</h2>
            <div className="bg-white/5 rounded-lg overflow-hidden border border-white/10">
              <iframe
                src={previewUrl}
                className="w-full h-96 md:h-screen border-0"
                title="Generated website preview"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
