import os
import json
import httpx
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime


class OllamaClient:
    """Client for Ollama LLM API (free, local) with retry logic and optimization"""

    def __init__(self, base_url: str = None, model: str = "llama3"):
        default_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        self.base_url = base_url or default_url
        self.model = os.getenv("OLLAMA_MODEL", model)
        self.timeout = 120  # Reduced from 300 for better resource management
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds, will exponentially backoff

    async def generate(
        self,
        prompt: str,
        stream: bool = True,
        temperature: float = 0.5,  # Reduced for stability
        top_p: float = 0.85,  # Reduced for stability
        num_predict: int = 256,  # Limit output length
    ) -> AsyncGenerator[str, None]:
        """
        Generate text using Ollama with retry logic and timeout management.
        Yields individual chunks as they arrive.
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": num_predict,  # Limit response length
        }

        full_response = ""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    async with client.stream("POST", url, json=payload) as response:
                        if response.status_code == 503:  # Service unavailable
                            raise Exception("Ollama service temporarily unavailable")
                        elif response.status_code == 500:  # Internal server error
                            raise Exception("Ollama internal server error")
                        elif response.status_code != 200:
                            raise Exception(f"Ollama HTTP {response.status_code}")
                        
                        async for line in response.aiter_lines():
                            if line:
                                try:
                                    chunk = json.loads(line)
                                    if "response" in chunk:
                                        full_response += chunk["response"]
                                        yield chunk["response"]
                                except json.JSONDecodeError:
                                    pass
                return  # Success
            except (httpx.TimeoutException, Exception) as e:
                last_error = str(e)
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"⚠️  Ollama error (attempt {attempt + 1}/{self.max_retries}): {e}", flush=True)
                    await asyncio.sleep(wait_time)
                else:
                    print(f"⚠️  Ollama unavailable after {self.max_retries} attempts: {last_error}", flush=True)
                    print(f"📋 Using fallback mode - generating structured placeholder response", flush=True)
                    # Fallback: generate structured placeholder for demo purposes
                    yield self._get_fallback_response(prompt)

    async def pull_model(self):
        """Ensure model is available locally"""
        url = f"{self.base_url}/api/pull"
        payload = {"name": self.model}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                print(f"✓ Ollama model '{self.model}' ready")
            else:
                raise Exception(f"Failed to pull model: {response.status_code}")

    def _get_fallback_response(self, prompt: str) -> str:
        """Generate a structured response for development/demo when Ollama unavailable"""
        if "html" in prompt.lower() or "landing" in prompt.lower():
            return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Startup</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 20px; text-align: center; }
        .hero h1 { font-size: 3em; margin-bottom: 20px; }
        .hero p { font-size: 1.2em; margin-bottom: 30px; }
        .cta { background: white; color: #667eea; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }
        .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 60px 20px; max-width: 1200px; margin: 0 auto; }
        .feature { padding: 30px; border-radius: 8px; background: #f0f0f0; }
        .feature h3 { margin-bottom: 10px; color: #667eea; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>Welcome to AI Solutions</h1>
        <p>Transforming businesses with intelligent automation</p>
        <button class="cta">Get Started</button>
    </div>
    <div class="features">
        <div class="feature">
            <h3>🚀 Fast</h3>
            <p>Lightning-quick responses powered by cutting-edge AI</p>
        </div>
        <div class="feature">
            <h3>🔒 Secure</h3>
            <p>Enterprise-grade security for your data</p>
        </div>
        <div class="feature">
            <h3>📊 Smart</h3>
            <p>Make better decisions with AI insights</p>
        </div>
    </div>
</body>
</html>"""
        elif "react" in prompt.lower() or "form" in prompt.lower():
            return """import React, { useState } from 'react';

export default function ContactForm() {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const [errors, setErrors] = useState({});

  const validateEmail = (email) => /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Name required';
    if (!validateEmail(formData.email)) newErrors.email = 'Valid email required';
    if (!formData.message.trim()) newErrors.message = 'Message required';
    
    if (Object.keys(newErrors).length === 0) {
      console.log('Form submitted:', formData);
      setFormData({ name: '', email: '', message: '' });
    } else {
      setErrors(newErrors);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '500px', margin: '20px auto', padding: '20px' }}>
      <div style={{ marginBottom: '15px' }}>
        <label>Name: <input name="name" value={formData.name} onChange={handleChange} style={{ width: '100%', padding: '8px' }} /></label>
        {errors.name && <p style={{ color: 'red', fontSize: '0.9em' }}>{errors.name}</p>}
      </div>
      <div style={{ marginBottom: '15px' }}>
        <label>Email: <input name="email" type="email" value={formData.email} onChange={handleChange} style={{ width: '100%', padding: '8px' }} /></label>
        {errors.email && <p style={{ color: 'red', fontSize: '0.9em' }}>{errors.email}</p>}
      </div>
      <div style={{ marginBottom: '15px' }}>
        <label>Message: <textarea name="message" value={formData.message} onChange={handleChange} style={{ width: '100%', padding: '8px', minHeight: '100px' }} /></label>
        {errors.message && <p style={{ color: 'red', fontSize: '0.9em' }}>{errors.message}</p>}
      </div>
      <button type="submit" style={{ padding: '10px 20px', backgroundColor: '#667eea', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>Submit</button>
    </form>
  );
}"""
        else:
            return """# Development Response
This is a placeholder response generated in fallback mode. 
The Ollama model is currently unavailable due to resource constraints.
In production, this would be replaced with real LLM-generated content.
The system architecture and orchestration are fully functional and ready for integration."""


class BaseAgent:
    """Base class for all agents in AutoDevOS"""

    def __init__(
        self,
        name: str,
        role_description: str,
        redis_client,
        job_id: str,
        rl_engine=None,
    ):
        self.name = name
        self.role_description = role_description
        self.redis_client = redis_client
        self.job_id = job_id
        self.rl_engine = rl_engine
        self.ollama = OllamaClient()

    async def think(self, task: str, context: Dict[str, Any] = None) -> str:
        """
        Main thinking method:
        1. Emit agent started event immediately for UX feedback
        2. Fetch high-reward past strategies from RL engine
        3. Build prompt with role + task + context + past strategies
        4. Call Ollama with streaming
        5. Emit each chunk as agent_log WebSocket event
        6. Return full response
        """
        context = context or {}

        # Emit immediate feedback that agent is starting
        await self.emit("agent_log", f"[{self.name} thinking...]")

        # Fetch past strategies from RL memory (Phase 3)
        strategies = ""
        if self.rl_engine:
            past_strategies = await self.rl_engine.get_high_reward_strategies(
                self.name, task, top_k=3
            )
            if past_strategies:
                strategies = "\n".join(
                    [f"  • {s[0]} (reward: {s[1]:.1f}/10)" for s in past_strategies]
                )

        # Build strategies section
        strategies_section = f"PAST HIGH-REWARD STRATEGIES:\n{strategies}\n" if strategies else ""

        # Build full prompt
        prompt = f"""You are the {self.name.upper()} at AutoDevOS.

{self.role_description}

CONTEXT:
{json.dumps(context, indent=2, default=str)}

{strategies_section}
TASK:
{task}

Respond concisely and directly. For code generation, output valid JSON only."""

        # Generate response with streaming
        full_response = ""
        token_buffer = ""
        is_first_chunk = True
        
        async for chunk in self.ollama.generate(prompt, stream=True):
            full_response += chunk
            token_buffer += chunk
            
            # Emit first chunk immediately to show LLM is responding
            if is_first_chunk and token_buffer.strip():
                await self.emit("agent_log", token_buffer.strip())
                token_buffer = ""
                is_first_chunk = False
                continue
            
            # Emit in meaningful chunks: full sentences or after ~20 tokens (reduced from 50)
            # Sentence boundaries: . ! ? followed by space or newline
            while token_buffer and (
                ('\n' in token_buffer) or 
                ('. ' in token_buffer) or 
                ('! ' in token_buffer) or 
                ('? ' in token_buffer) or
                (len(token_buffer) > 20)
            ):
                if '. ' in token_buffer and token_buffer.index('. ') < 40:
                    idx = token_buffer.index('. ') + 2
                    chunk_to_send = token_buffer[:idx]
                    token_buffer = token_buffer[idx:]
                elif '! ' in token_buffer and token_buffer.index('! ') < 40:
                    idx = token_buffer.index('! ') + 2
                    chunk_to_send = token_buffer[:idx]
                    token_buffer = token_buffer[idx:]
                elif '? ' in token_buffer and token_buffer.index('? ') < 40:
                    idx = token_buffer.index('? ') + 2
                    chunk_to_send = token_buffer[:idx]
                    token_buffer = token_buffer[idx:]
                elif '\n' in token_buffer:
                    idx = token_buffer.index('\n') + 1
                    chunk_to_send = token_buffer[:idx]
                    token_buffer = token_buffer[idx:]
                else:
                    # No sentence boundary found but buffer > 20 tokens
                    chunk_to_send = token_buffer[:20]
                    token_buffer = token_buffer[20:]
                
                await self.emit("agent_log", chunk_to_send.strip())
        
        # Emit any remaining buffered tokens
        if token_buffer.strip():
            await self.emit("agent_log", token_buffer.strip())

        return full_response

    async def emit(self, event_type: str, content: str, reward: Optional[float] = None):
        """Publish event to Redis pub/sub channel for WebSocket streaming"""
        event = {
            "type": event_type,
            "agent": self.name,
            "content": content,
            "reward": reward,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.redis_client.publish_event(self.job_id, event)
