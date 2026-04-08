'use client';

import { useEffect, useState } from 'react';
import { Zap, Brain, Code, AlertCircle } from 'lucide-react';

interface DebugWindow {
  title: string;
  content: string;
  type: 'info' | 'success' | 'error' | 'process';
}

interface PuterGlobal {
  ai: {
    chat: (
      message: string,
      options: { model: string; stream?: boolean }
    ) => Promise<any>;
  };
  print: (content: string) => void;
}

declare global {
  interface Window {
    puter: PuterGlobal;
  }
}

export default function DebugDashboard() {
  const [prompt, setPrompt] = useState('');
  const [debugWindows, setDebugWindows] = useState<DebugWindow[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [puterAvailable, setPuterAvailable] = useState(false);

  useEffect(() => {
    // Check if Puter.js is available
    const checkPuter = setInterval(() => {
      if (typeof window !== 'undefined' && window.puter && window.puter.ai && window.puter.ai.chat) {
        setPuterAvailable(true);
        clearInterval(checkPuter);
      }
    }, 500);

    // Clear interval after 10 seconds (stop checking)
    setTimeout(() => clearInterval(checkPuter), 10000);

    return () => clearInterval(checkPuter);
  }, []);

  const addDebugWindow = (title: string, content: string, type: 'info' | 'success' | 'error' | 'process' = 'info') => {
    setDebugWindows((prev) => [...prev, { title, content, type }]);
  };

  const updateLastWindow = (content: string) => {
    setDebugWindows((prev) => {
      const updated = [...prev];
      if (updated.length > 0) {
        updated[updated.length - 1].content += '\n' + content;
      }
      return updated;
    });
  };

  const improvePromptWithPuter = async () => {
    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    setIsLoading(true);
    setDebugWindows([]);

    try {
      // Check if Puter.js is available
      if (!window.puter || !window.puter.ai || !window.puter.ai.chat) {
        throw new Error('Puter.js not available. Please check your internet connection.');
      }

      // Window 1: Show original prompt
      addDebugWindow('📝 Original Prompt', prompt, 'info');

      // Window 2: Prompt Improvement
      addDebugWindow('🔍 Analyzing & Improving Prompt', 'Connecting to Puter AI (Claude)...', 'process');

      const improvementPrompt = `You are an expert business analyst and technical strategist. 
A user wants an AI website generator to build a website for:
"${prompt}"

Please provide:
1. A detailed description of this business/tool
2. Key features and requirements
3. Target audience
4. Technical stack recommendations
5. Agent role assignments (PM, Architect, Developer, QA, Security specialist, SEO specialist, Tech debt reviewer)

Format your response as a structured improvement document that can guide AI agents to build the perfect website.`;

      try {
        const response = await Promise.race([
          window.puter.ai.chat(improvementPrompt, {
            model: 'claude-sonnet-4-6',
          }),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Request timeout - Puter.js API not responding')), 30000)
          ),
        ]);

        const improvedPrompt = response.message.content[0].text;
        setDebugWindows((prev) => [
          ...prev.slice(0, -1),
          { title: '🔍 Improved Prompt Analysis', content: improvedPrompt, type: 'success' },
        ]);

        // Window 3: Generate PM Spec
        addDebugWindow('📋 PM Agent - Generating Product Spec', 'Generating specifications...', 'process');
        const pmPrompt = `Based on this improved analysis:
${improvedPrompt}

Generate a detailed product specification (no more than 5 sentences) that covers:
- Main value proposition
- Key features (3-4)
- Success metrics`;

        const pmResponse = await Promise.race([
          window.puter.ai.chat(pmPrompt, { model: 'claude-sonnet-4-6' }),
          new Promise((_, reject) => setTimeout(() => reject(new Error('PM Agent timeout')), 30000)),
        ]);
        updateLastWindow(pmResponse.message.content[0].text);

        // Window 4: Generate Architecture
        addDebugWindow('🏗️ Architect Agent - Designing Structure', 'Designing file structure...', 'process');
        const archPrompt = `Based on this specification:
${pmResponse.message.content[0].text}

Design the website architecture with:
- File structure (HTML, CSS, JS files)
- Component hierarchy
- Data flow diagram
Keep it concise.`;

        const archResponse = await Promise.race([
          window.puter.ai.chat(archPrompt, { model: 'claude-sonnet-4-6' }),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Architect Agent timeout')), 30000)),
        ]);
        updateLastWindow(archResponse.message.content[0].text);

        // Window 5: Generate Code
        addDebugWindow('💻 Developer Agent - Writing Code', 'Generating production code...', 'process');
        const devPrompt = `Based on this architecture:
${archResponse.message.content[0].text}

Generate the complete HTML/CSS/JavaScript code for a modern, professional website. Include:
- Beautiful UI with gradients
- Responsive design
- Interactive elements
- Professional styling

Provide the full code as a single HTML file. Start with <!DOCTYPE html>`;

        const devResponse = await Promise.race([
          window.puter.ai.chat(devPrompt, { model: 'claude-sonnet-4-6' }),
          new Promise((_, reject) => setTimeout(() => reject(new Error('Developer Agent timeout')), 45000)),
        ]);
        const generatedCode = devResponse.message.content[0].text;
        updateLastWindow(generatedCode.substring(0, 500) + '...');

        // Window 6: Create job in backend
        addDebugWindow('🚀 Backend Integration', 'Creating job in backend...', 'process');

        const jobResponse = await fetch('http://localhost:8000/api/jobs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: prompt }),
        });

        if (jobResponse.ok) {
          const jobData = await jobResponse.json();
          setJobId(jobData.jobId);
          updateLastWindow(`✅ Job created successfully!\nJob ID: ${jobData.jobId}\nStatus: ${jobData.status}`);
        } else {
          throw new Error('Failed to create job on backend');
        }

        setDebugWindows((prev) =>
          prev.map((w) =>
            w.title === '💻 Developer Agent - Writing Code'
              ? { ...w, type: 'success', content: 'Code generation complete!\n\n' + generatedCode.substring(0, 300) + '...' }
              : w
          )
        );

        setIsLoading(false);
      } catch (puterError) {
        throw new Error(`Puter.js API Error: ${puterError}`);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      addDebugWindow('❌ Error', `${errorMsg}\n\nTroubleshooting:\n• Check internet connection\n• Puter.js may be blocked by firewall\n• Try refreshing the page\n• Check browser console for details`, 'error');
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Brain className="w-10 h-10 text-cyan-400" />
            AutoDevOS Debug Dashboard
          </h1>
          <p className="text-gray-400">Real-time agent work and prompt improvement with Puter.js AI</p>
        </div>

        {/* Puter.js Status Indicator */}
        <div className={`glass border rounded-xl p-4 mb-8 flex items-center gap-3 ${
          puterAvailable 
            ? 'border-emerald-500/30 bg-emerald-500/5' 
            : 'border-yellow-500/30 bg-yellow-500/5'
        }`}>
          <div className={`w-3 h-3 rounded-full ${puterAvailable ? 'bg-emerald-500 animate-pulse' : 'bg-yellow-500 animate-pulse'}`} />
          <span className={`font-medium ${puterAvailable ? 'text-emerald-400' : 'text-yellow-400'}`}>
            {puterAvailable 
              ? '✓ Puter.js AI Connection Active - Ready to generate websites'
              : '⏳ Puter.js AI Loading... (requires internet connection)'
            }
          </span>
        </div>

        {/* Prompt Input */}
        <div className="glass border-white/10 p-8 rounded-xl mb-8">
          <label className="block text-sm font-semibold text-gray-300 mb-3">
            Enter Your Website Concept
          </label>
          <div className="flex gap-3">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., 'a SaaS tool for freelancing', 'a portfolio website for designers', 'an AI writing assistant'"
              className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20 resize-none"
              rows={3}
            />
            <button
              onClick={improvePromptWithPuter}
              disabled={isLoading || !prompt.trim() || !puterAvailable}
              className="button-primary px-6 self-end disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              title={!puterAvailable ? 'Puter.js is connecting... this may require internet access' : ''}
            >
              {isLoading ? (
                <>
                  <span className="animate-spin">⚙️</span> Processing
                </>
              ) : !puterAvailable ? (
                <>
                  <AlertCircle className="w-5 h-5" /> Connecting...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" /> Analyze with AI
                </>
              )}
            </button>
          </div>
        </div>

        {/* Debug Windows Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {debugWindows.map((window, idx) => (
            <div
              key={idx}
              className={`glass rounded-xl border overflow-hidden flex flex-col max-h-96 ${
                window.type === 'error'
                  ? 'border-red-500/30 bg-red-500/5'
                  : window.type === 'success'
                  ? 'border-emerald-500/30 bg-emerald-500/5'
                  : window.type === 'process'
                  ? 'border-cyan-500/30 bg-cyan-500/5'
                  : 'border-white/10'
              }`}
            >
              <div className="bg-gradient-to-r from-slate-800 to-slate-900 border-b border-white/10 p-4 flex items-center gap-2">
                {window.type === 'error' && <AlertCircle className="w-5 h-5 text-red-400" />}
                {window.type === 'success' && <span className="text-emerald-400">✓</span>}
                {window.type === 'process' && <span className="animate-spin">⚙️</span>}
                <h3 className="font-semibold text-white flex-1">{window.title}</h3>
              </div>
              <div className="flex-1 overflow-y-auto p-4">
                <pre className="text-xs text-gray-300 whitespace-pre-wrap break-words font-mono">
                  {window.content}
                </pre>
              </div>
            </div>
          ))}
        </div>

        {/* Job Status */}
        {jobId && (
          <div className="mt-8 glass border-cyan-500/30 bg-cyan-500/5 p-6 rounded-xl">
            <div className="flex items-center gap-3 mb-4">
              <Code className="w-6 h-6 text-cyan-400" />
              <h3 className="text-lg font-semibold text-white">Job Created Successfully!</h3>
            </div>
            <p className="text-gray-300 mb-4">Job ID: <span className="font-mono text-cyan-400">{jobId}</span></p>
            <a
              href={`/dashboard/${jobId}`}
              className="button-primary inline-flex items-center gap-2"
            >
              <Zap className="w-4 h-4" />
              View Job Progress
            </a>
          </div>
        )}

        {/* Info */}
        {debugWindows.length === 0 && !isLoading && (
          <div className="glass border-white/10 p-8 rounded-xl text-center text-gray-400">
            <Brain className="w-16 h-16 text-cyan-400/20 mx-auto mb-4" />
            <p>Enter a concept and click "Analyze with AI" to see the agent workflow in real-time</p>
            <p className="text-sm mt-2">Powered by Puter.js - Free Claude AI</p>
          </div>
        )}

        {/* Troubleshooting Section */}
        {!puterAvailable && debugWindows.length === 0 && (
          <div className="glass border-indigo-500/30 bg-indigo-500/5 rounded-xl p-6 mt-8">
            <h2 className="text-lg font-semibold text-indigo-400 mb-4">🔧 Troubleshooting Guide</h2>
            <div className="space-y-2 text-sm text-gray-300">
              <p><strong>Why is Puter.js not connecting?</strong></p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>AutoDevOS is running in a Docker container without internet access</li>
                <li>Puter.js requires external connectivity to reach api.puter.com</li>
                <li>Your firewall may be blocking WebSocket connections</li>
              </ul>
              <p className="mt-4"><strong>How to fix:</strong></p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>Ensure your Docker container has internet access</li>
                <li>Check your firewall settings for WebSocket blocking</li>
                <li>Try refreshing the page (F5 or Cmd+R)</li>
                <li>Open browser dev tools (F12) to check console for errors</li>
                <li>The system will work in offline mode if Puter.js doesn't load</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
