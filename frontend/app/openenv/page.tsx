'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap, Target } from 'lucide-react';

interface OpenEnvTask {
  task_id: string;
  description: string;
  difficulty: string;
  constraints: {
    max_iterations: number;
    target_reward: number;
  };
}

export default function OpenEnvTasksPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<OpenEnvTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creatingTask, setCreatingTask] = useState<string | null>(null);

  // Fetch available OpenEnv tasks
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        const res = await fetch('http://localhost:8000/api/openenv/tasks');
        if (res.ok) {
          const data = await res.json();
          setTasks(data.tasks);
        } else {
          setError('Failed to load tasks');
        }
      } catch (err) {
        setError('Failed to fetch OpenEnv tasks');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const handleCreateJobFromTask = async (taskId: string) => {
    try {
      setCreatingTask(taskId);
      setError(null);

      const res = await fetch('http://localhost:8000/api/jobs/from-task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: taskId }),
      });

      if (!res.ok) {
        throw new Error('Failed to create job');
      }

      const { jobId } = await res.json();
      router.push(`/dashboard/${jobId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setCreatingTask(null);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="border-b border-slate-700 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-6 h-6 text-blue-400" />
            <h1 className="text-3xl font-bold text-white">OpenEnv Tasks</h1>
          </div>
          <p className="text-slate-400">Benchmark evaluation tasks for AI-powered website generation</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        {/* Navigation */}
        <div className="mb-8">
          <Link href="/" className="text-blue-400 hover:text-blue-300 transition-colors">
            ← Back to Home
          </Link>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-slate-400">Loading OpenEnv tasks...</p>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-400">No tasks available</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {tasks.map((task) => (
              <Card key={task.task_id} className="bg-white shadow-lg hover:shadow-xl transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg capitalize">
                        {task.task_id.replace(/_/g, ' ')}
                      </CardTitle>
                      <CardDescription className="mt-2">
                        {task.description}
                      </CardDescription>
                    </div>
                  </div>
                  
                  {/* Difficulty Badge */}
                  <div className="mt-3">
                    <Badge className={getDifficultyColor(task.difficulty)}>
                      {task.difficulty.toUpperCase()}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent>
                  {/* Constraints */}
                  <div className="space-y-2 mb-6 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Max Iterations:</span>
                      <span className="font-semibold">{task.constraints.max_iterations}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Target Reward:</span>
                      <span className="font-semibold">{(task.constraints.target_reward * 100).toFixed(0)}%</span>
                    </div>
                  </div>

                  {/* Create Button */}
                  <Button
                    onClick={() => handleCreateJobFromTask(task.task_id)}
                    disabled={creatingTask === task.task_id}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {creatingTask === task.task_id ? 'Creating...' : 'Create Job'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Info Section */}
        <div className="mt-16 bg-slate-800 rounded-lg p-8 border border-slate-700">
          <h2 className="text-xl font-bold text-white mb-4">About OpenEnv Tasks</h2>
          <p className="text-slate-300 mb-4">
            OpenEnv tasks are standardized benchmarks for evaluating AI agents' ability to generate websites. 
            Each task comes with specific requirements and constraints.
          </p>
          <ul className="text-slate-300 space-y-2">
            <li>✓ <strong>EASY</strong> - Simple landing pages, quick turnaround (1-2 iterations)</li>
            <li>✓ <strong>MEDIUM</strong> - Professional portfolios, standard features (2-3 iterations)</li>
            <li>✓ <strong>HARD</strong> - Complex e-commerce sites, extensive features (3-4 iterations)</li>
          </ul>
        </div>
      </div>
    </main>
  );
}
