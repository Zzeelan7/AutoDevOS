'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader, ArrowRight, Zap, Sparkles, Code, Palette, Rocket } from 'lucide-react';

interface Job {
  jobId: string;
  prompt: string;
  status: string;
  created_at: string;
  overall_reward?: number;
}

function HomeContent() {
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch job history
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setJobsLoading(true);
        const res = await fetch('http://localhost:8000/api/jobs?limit=5');
        if (res.ok) {
          const data = await res.json();
          setJobs(data);
        }
      } catch (err) {
        console.error('Failed to fetch jobs:', err);
      } finally {
        setJobsLoading(false);
      }
    };

    fetchJobs();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    try {
      setLoading(true);
      setError(null);

      const res = await fetch('http://localhost:8000/api/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt.trim() }),
      });

      if (!res.ok) {
        throw new Error('Failed to create job');
      }

      const { jobId } = await res.json();
      setPrompt('');
      router.push(`/dashboard/${jobId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'running':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'error':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl animate-pulse-subtle"></div>
        <div className="absolute top-1/2 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse-subtle" style={{ animationDelay: '1s' }}></div>
        <div className="absolute -bottom-40 right-1/3 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse-subtle" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="border-b border-white/10 backdrop-blur-xl sticky top-0 z-40">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">AutoDevOS</h1>
                <p className="text-xs text-gray-400">AI Website Generator</p>
              </div>
            </div>
            <Link href="/openenv">
              <Button className="bg-cyan-600/20 border border-cyan-500/50 text-cyan-300 hover:bg-cyan-600/30">
                🎯 OpenEnv Tasks
              </Button>
            </Link>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 md:px-8 py-20">
          {/* Hero Section */}
          <div className="text-center mb-16 animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-6">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span className="text-sm text-gray-300">Powered by AI Agents</span>
            </div>
            
            <h2 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
              Build Your Website <br />
              <span className="text-gradient">with AI</span>
            </h2>
            
            <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-8">
              Describe your vision. AI agents autonomously design, build, and refine your website in minutes.
            </p>
          </div>

          {/* Input Section */}
          <div className="mb-12 animate-slide-in" style={{ animationDelay: '0.1s' }}>
            <Card className="glass border-white/10 shadow-2xl">
              <CardContent className="p-6 md:p-8">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="relative">
                    <textarea
                      id="prompt-input"
                      name="prompt"
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Describe your business idea, and our AI agents will build your website autonomously..."
                      className="input-modern min-h-32 resize-none font-medium"
                      disabled={loading}
                      autoComplete="off"
                    />
                    <div className="text-xs text-gray-500 mt-2 flex justify-between">
                      <span>{prompt.length} characters</span>
                      <span className={prompt.length > 500 ? 'text-yellow-400' : 'text-gray-500'}>
                        {prompt.length > 500 ? 'Getting detailed! 📝' : 'Max 1000 chars'}
                      </span>
                    </div>
                  </div>

                  {error && (
                    <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-start gap-3">
                      <span>⚠️</span>
                      <span>{error}</span>
                    </div>
                  )}

                  <Button
                    type="submit"
                    disabled={loading || !prompt.trim()}
                    className="button-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <Loader className="w-5 h-5 animate-spin" />
                        <span>Building your website...</span>
                      </>
                    ) : (
                      <>
                        <Rocket className="w-5 h-5" />
                        <span>Generate Website</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-16 animate-slide-in" style={{ animationDelay: '0.2s' }}>
            <div className="glass-subtle p-6 rounded-xl border border-white/10 hover:border-cyan-500/30 transition-colors">
              <div className="p-3 rounded-lg bg-cyan-500/10 w-fit mb-4">
                <Code className="w-6 h-6 text-cyan-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Smart Architecture</h3>
              <p className="text-sm text-gray-400">PM agents analyze and design optimal structure</p>
            </div>

            <div className="glass-subtle p-6 rounded-xl border border-white/10 hover:border-blue-500/30 transition-colors">
              <div className="p-3 rounded-lg bg-blue-500/10 w-fit mb-4">
                <Palette className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Modern Design</h3>
              <p className="text-sm text-gray-400">Beautiful UI/UX with responsive layouts</p>
            </div>

            <div className="glass-subtle p-6 rounded-xl border border-white/10 hover:border-purple-500/30 transition-colors">
              <div className="p-3 rounded-lg bg-purple-500/10 w-fit mb-4">
                <Sparkles className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Continuous Improvement</h3>
              <p className="text-sm text-gray-400">Iterative refinement with autonomous agents</p>
            </div>
          </div>

          {/* Recent Jobs */}
          {!jobsLoading && jobs.length > 0 && (
            <div className="animate-slide-in" style={{ animationDelay: '0.3s' }}>
              <h3 className="text-lg font-semibold text-white mb-4">Recent Websites</h3>
              <div className="space-y-3">
                {jobs.map((job) => (
                  <Card
                    key={job.jobId}
                    className="glass cursor-pointer border-white/10 hover:border-cyan-500/50 hover:bg-white/8 transition-all"
                    onClick={() => router.push(`/dashboard/${job.jobId}`)}
                  >
                    <CardContent className="p-4 flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <span className="font-mono text-sm text-cyan-400">{job.jobId}</span>
                          <Badge className={`${getStatusColor(job.status)} border`} variant="secondary">
                            {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                          </Badge>
                          {job.overall_reward && (
                            <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">
                              ⭐ {job.overall_reward.toFixed(1)}/10
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-400 line-clamp-1">{job.prompt}</p>
                        <p className="text-xs text-gray-600 mt-1">
                          {new Date(job.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-500 ml-4 flex-shrink-0" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-white/10 mt-20">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-8 text-center text-gray-500 text-sm">
            <p>AutoDevOS © 2024 • Building the future of web development with AI</p>
          </div>
        </div>
      </div>
    </main>
  );
}

export default function Home() {
  return (
    <ErrorBoundary>
      <HomeContent />
    </ErrorBoundary>
  );
}
