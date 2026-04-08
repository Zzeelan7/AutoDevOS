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
      case 'degraded':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'running':
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30';
      case 'error':
      case 'failed':
        return 'bg-red-500/20 text-red-300 border-red-500/30';
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 relative overflow-hidden text-white">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-36 left-1/2 -translate-x-1/2 w-[48rem] h-[48rem] bg-cyan-500/10 rounded-full blur-3xl animate-pulse-subtle"></div>
        <div className="absolute top-20 -left-32 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse-subtle" style={{ animationDelay: '1s' }}></div>
        <div className="absolute -bottom-28 -right-32 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse-subtle" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="hidden lg:block fixed left-0 top-0 bottom-0 w-14 border-r border-white/10 z-30" />
      <div className="hidden lg:block fixed right-0 top-0 bottom-0 w-14 border-l border-white/10 z-30" />

      <div className="relative z-40">
        <header className="sticky top-0 backdrop-blur-xl border-b border-white/10">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-4 flex items-center justify-between">
            <button onClick={() => scrollTo('hero')} className="flex items-center gap-3 text-left">
              <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">AutoDevOS</h1>
                <p className="text-xs text-gray-400 tracking-wide">AUTONOMOUS WEBSITE STUDIO</p>
              </div>
            </button>

            <nav className="hidden md:flex items-center gap-8 text-xs tracking-[0.14em] text-gray-300 font-semibold">
              <button onClick={() => scrollTo('hero')} className="hover:text-cyan-300 transition-colors">HOME</button>
              <button onClick={() => scrollTo('features')} className="hover:text-cyan-300 transition-colors">FEATURES</button>
              <button onClick={() => scrollTo('recent')} className="hover:text-cyan-300 transition-colors">RECENT</button>
            </nav>

            <div className="flex items-center gap-2">
              <Link href="/openenv">
                <Button className="bg-cyan-600/20 border border-cyan-500/50 text-cyan-300 hover:bg-cyan-600/30">
                  OpenEnv
                </Button>
              </Link>
            </div>
          </div>
        </header>

        <section id="hero" className="max-w-6xl mx-auto px-4 sm:px-6 md:px-8 pt-16 pb-12 md:pt-24 md:pb-16">
          <div className="text-center animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-6">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span className="text-sm text-gray-300">Prompt. Build. Iterate. Ship.</span>
            </div>

            <h2 className="text-4xl md:text-6xl font-bold mb-6 leading-[1.05] max-w-4xl mx-auto">
              Turn raw ideas into
              <br />
              <span className="text-gradient">beautiful production websites</span>
            </h2>

            <p className="text-base md:text-lg text-gray-300/90 max-w-3xl mx-auto mb-10 leading-relaxed">
              Give one clear prompt and let the AI team architect structure, generate code, and improve quality.
              Built for business websites, landing pages, portfolios, and SaaS launches.
            </p>
          </div>

          <div className="max-w-3xl mx-auto animate-slide-in" style={{ animationDelay: '0.1s' }}>
            <Card className="glass border-white/10 shadow-2xl">
              <CardContent className="p-6 md:p-8">
                <form onSubmit={handleSubmit} className="space-y-4">
                  <textarea
                    id="prompt-input"
                    name="prompt"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Example: Create a luxury interior design studio website with services, project gallery, testimonials, and consultation booking."
                    className="input-modern min-h-36 resize-none font-medium"
                    disabled={loading}
                    autoComplete="off"
                  />

                  <div className="text-xs text-gray-500 flex justify-between">
                    <span>{prompt.length} characters</span>
                    <span className={prompt.length > 500 ? 'text-yellow-400' : 'text-gray-500'}>
                      {prompt.length > 500 ? 'Detailed prompt detected' : 'Max 1000 chars'}
                    </span>
                  </div>

                  {error && (
                    <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-sm flex items-start gap-3">
                      <span>⚠</span>
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
                        <span>Generating website...</span>
                      </>
                    ) : (
                      <>
                        <Rocket className="w-5 h-5" />
                        <span>Generate Attractive Website</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </section>

        <section id="features" className="max-w-6xl mx-auto px-4 sm:px-6 md:px-8 pb-12 md:pb-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 animate-slide-in" style={{ animationDelay: '0.2s' }}>
            <div className="glass-subtle p-6 rounded-xl border border-white/10 hover:border-cyan-500/40 transition-all hover:-translate-y-1">
              <div className="p-3 rounded-lg bg-cyan-500/10 w-fit mb-4">
                <Code className="w-6 h-6 text-cyan-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Structured Build Pipeline</h3>
              <p className="text-sm text-gray-300/85">PM, architect, and developer agents coordinate to produce code with clear intent.</p>
            </div>

            <div className="glass-subtle p-6 rounded-xl border border-white/10 hover:border-blue-500/40 transition-all hover:-translate-y-1">
              <div className="p-3 rounded-lg bg-blue-500/10 w-fit mb-4">
                <Palette className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Modern Visual Language</h3>
              <p className="text-sm text-gray-300/85">Balanced spacing, strong hierarchy, and responsive composition across devices.</p>
            </div>

            <div className="glass-subtle p-6 rounded-xl border border-white/10 hover:border-purple-500/40 transition-all hover:-translate-y-1">
              <div className="p-3 rounded-lg bg-purple-500/10 w-fit mb-4">
                <Sparkles className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Transparent Quality Status</h3>
              <p className="text-sm text-gray-300/85">Completed vs degraded runs are clearly labeled so you can trust output quality.</p>
            </div>
          </div>
        </section>

        <section id="recent" className="max-w-5xl mx-auto px-4 sm:px-6 md:px-8 pb-20">
          {!jobsLoading && jobs.length > 0 && (
            <div className="animate-slide-in" style={{ animationDelay: '0.3s' }}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Recent Websites</h3>
                <span className="text-xs tracking-wide text-gray-400">CLICK TO OPEN DASHBOARD</span>
              </div>

              <div className="space-y-3">
                {jobs.map((job) => (
                  <Card
                    key={job.jobId}
                    className="glass cursor-pointer border-white/10 hover:border-cyan-500/50 transition-all"
                    onClick={() => router.push(`/dashboard/${job.jobId}`)}
                  >
                    <CardContent className="p-4 flex items-center justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <span className="font-mono text-sm text-cyan-400">{job.jobId}</span>
                          <Badge className={`${getStatusColor(job.status)} border`} variant="secondary">
                            {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                          </Badge>
                          {job.overall_reward && (
                            <Badge variant="outline" className="text-emerald-400 border-emerald-500/30">
                              Score {job.overall_reward.toFixed(1)}/10
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-300/85 line-clamp-1">{job.prompt}</p>
                        <p className="text-xs text-gray-500 mt-1">{new Date(job.created_at).toLocaleDateString()}</p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-500 flex-shrink-0" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </section>

        <footer className="border-t border-white/10">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 md:px-8 py-8 text-center text-gray-500 text-sm">
            <p>AutoDevOS © 2026 • Design-forward AI website generation</p>
          </div>
        </footer>
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
