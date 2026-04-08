import os
import json
import httpx
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime


class OpenAIClient:
    """Client for OpenAI GPT API with streaming support"""

    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", model)
        self.base_url = "https://api.openai.com/v1"
        self.timeout = 60

    async def generate(
        self,
        prompt: str,
        stream: bool = True,
        temperature: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """Generate text using OpenAI API with streaming"""
        if not self.api_key:
            print("⚠️  OpenAI API key not configured", flush=True)
            yield self._get_fallback_response(prompt)
            return

        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": stream,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    if response.status_code == 429:
                        # Quota exceeded - don't retry, signal to use fallback
                        raise Exception("OpenAI quota exceeded - falling back to Ollama")
                    elif response.status_code != 200:
                        error_text = await response.aread()
                        raise Exception(f"OpenAI API error {response.status_code}: {error_text.decode()}")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            if data_str:
                                try:
                                    chunk = json.loads(data_str)
                                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                                except json.JSONDecodeError:
                                    pass
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                print(f"⚠️  OpenAI quota exceeded - using Ollama fallback", flush=True)
            else:
                print(f"❌ OpenAI error: {e}", flush=True)
            # Signal that fallback should be used
            raise

    def _get_fallback_response(self, prompt: str) -> str:
        """Simple fallback response"""
        return "# Generated Response\nThis is a fallback response. LLM service is currently unavailable."


class OllamaClient:
    """Client for Ollama LLM API (free, local) with retry logic and optimization"""

    def __init__(self, base_url: str = None, model: str = "deepseek-coder:6.7b-instruct-q4_K_M"):
        default_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        self.base_url = base_url or default_url
        self.model = os.getenv("OLLAMA_MODEL", model)
        self.timeout = 180  # Increased for longer code generation
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds, will exponentially backoff

    async def generate(
        self,
        prompt: str,
        stream: bool = True,
        temperature: float = 0.7,  # Increased from 0.5 for better reasoning
        top_p: float = 0.9,  # Increased from 0.85 for more diverse output
        num_predict: int = 800,  # Increased from 256 for complete code generation
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
        """Generate high-quality fallback responses when LLM services unavailable"""
        prompt_lower = prompt.lower()

        # If this is a code-generation task, return strict JSON expected by developer agent.
        if "index.html" in prompt_lower or "output valid json" in prompt_lower or "script.js" in prompt_lower:
            return json.dumps(
                {
                    "index.html": "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>Generated Website</title><link rel=\"stylesheet\" href=\"style.css\"></head><body><header><h1>Generated Website</h1></header><main><section><h2>Custom website draft</h2><p>This draft was generated from fallback mode because the model provider was unavailable.</p><button class=\"cta\">Get Started</button></section></main><script src=\"script.js\"></script></body></html>",
                    "style.css": "*{margin:0;padding:0;box-sizing:border-box}body{font-family:Segoe UI,Arial,sans-serif;padding:2rem;line-height:1.6}.cta{margin-top:1rem;padding:.7rem 1.2rem;border:0;border-radius:8px;background:#0f172a;color:#fff;cursor:pointer}",
                    "script.js": "document.querySelectorAll('.cta').forEach((b)=>b.addEventListener('click',()=>console.log('CTA clicked')));",
                }
            )
        
        # Portfolio Website
        if "portfolio" in prompt_lower or "showcase" in prompt_lower:
            return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Portfolio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0a0e27; color: #e0e0e0; }
        nav { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem 2rem; position: sticky; top: 0; }
        nav a { color: white; margin: 0 1rem; text-decoration: none; }
        .hero { padding: 80px 20px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .hero h1 { font-size: 3em; margin-bottom: 0.5rem; }
        .hero p { font-size: 1.3em; margin-bottom: 2rem; }
        .projects { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; padding: 4rem 2rem; max-width: 1200px; margin: 0 auto; }
        .project { background: #1a1f3a; padding: 2rem; border-radius: 10px; border-left: 4px solid #667eea; }
        .project h3 { color: #667eea; margin-bottom: 1rem; }
        .project img { width: 100%; max-height: 200px; object-fit: cover; border-radius: 5px; margin-bottom: 1rem; }
        footer { background: #0a0e27; border-top: 1px solid #333; padding: 2rem; text-align: center; }
    </style>
</head>
<body>
    <nav>
        <a href="#home">Home</a>
        <a href="#projects">Projects</a>
        <a href="#about">About</a>
        <a href="#contact">Contact</a>
    </nav>
    <div class="hero">
        <h1>John Doe</h1>
        <p>Full Stack Designer & Developer</p>
    </div>
    <div class="projects">
        <div class="project">
            <h3>Project 1: Web Application</h3>
            <p>A modern web app built with React and Node.js</p>
        </div>
        <div class="project">
            <h3>Project 2: Mobile Design</h3>
            <p>Beautiful UI/UX design for iOS and Android</p>
        </div>
        <div class="project">
            <h3>Project 3: Brand Identity</h3>
            <p>Complete branding solution for startups</p>
        </div>
    </div>
    <footer>
        <p>&copy; 2024 Portfolio. All rights reserved.</p>
    </footer>
</body>
</html>"""
        
        # SaaS Landing Page
        elif "saas" in prompt_lower or "pricing" in prompt_lower or "landing" in prompt_lower:
            return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern SaaS Product</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: white; color: #333; }
        nav { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: white; position: sticky; top: 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .logo { font-weight: bold; font-size: 1.5em; color: #667eea; }
        .hero { padding: 100px 20px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .hero h1 { font-size: 3rem; margin-bottom: 1rem; }
        .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; padding: 4rem 2rem; max-width: 1200px; margin: 0 auto; }
        .feature { padding: 2rem; background: #f5f5f5; border-radius: 10px; text-align: center; }
        .feature h3 { color: #667eea; margin-bottom: 1rem; }
        .pricing { padding: 4rem 2rem; background: #f9f9f9; text-align: center; }
        .pricing-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; max-width: 1200px; margin: 2rem auto; }
        .plan { background: white; padding: 2rem; border-radius: 10px; border: 2px solid #ddd; }
        .plan.popular { border-color: #667eea; box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2); }
        button { background: #667eea; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }
        button:hover { background: #764ba2; }
        footer { background: #333; color: white; padding: 2rem; text-align: center; }
    </style>
</head>
<body>
    <nav>
        <div class="logo">SaaS Product</div>
        <div>
            <a href="#" style="margin: 0 1rem; color: #333; text-decoration: none;">Features</a>
            <a href="#" style="margin: 0 1rem; color: #333; text-decoration: none;">Pricing</a>
            <button>Sign Up</button>
        </div>
    </nav>
    <section class="hero">
        <h1>Grow Your Business Faster</h1>
        <p style="font-size: 1.2em; margin-bottom: 2rem;">The all-in-one platform for modern teams</p>
        <button style="background: white; color: #667eea;">Get Started Free</button>
    </section>
    <section class="features">
        <div class="feature">
            <h3>⚡ Fast</h3>
            <p>Lightning-quick performance that scales with your needs</p>
        </div>
        <div class="feature">
            <h3>🔒 Secure</h3>
            <p>Enterprise-grade security and compliance standards</p>
        </div>
        <div class="feature">
            <h3>📊 Analytics</h3>
            <p>Deep insights into your business metrics</p>
        </div>
    </section>
    <section class="pricing">
        <h2>Simple, Transparent Pricing</h2>
        <div class="pricing-grid">
            <div class="plan">
                <h3>Starter</h3>
                <p style="font-size: 2em; color: #667eea; margin: 1rem 0;">$29<span style="font-size: 0.5em;">/mo</span></p>
                <p>Perfect for small teams</p>
                <button style="margin-top: 1rem; width: 100%;">Choose Plan</button>
            </div>
            <div class="plan popular">
                <h3>Pro</h3>
                <p style="font-size: 2em; color: #667eea; margin: 1rem 0;">$79<span style="font-size: 0.5em;">/mo</span></p>
                <p style="color: #667eea; font-weight: bold;">Most Popular</p>
                <button style="margin-top: 1rem; width: 100%;">Choose Plan</button>
            </div>
            <div class="plan">
                <h3>Enterprise</h3>
                <p style="font-size: 2em; color: #667eea; margin: 1rem 0;">Custom</p>
                <p>For large organizations</p>
                <button style="margin-top: 1rem; width: 100%;">Contact Sales</button>
            </div>
        </div>
    </section>
    <footer>
        <p>&copy; 2024 SaaS Product. All rights reserved.</p>
    </footer>
</body>
</html>"""
        
        # Contact Form Website
        elif "contact" in prompt_lower or "form" in prompt_lower:
            return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 3rem; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 500px; }
        h1 { color: #333; margin-bottom: 2rem; text-align: center; }
        form { display: flex; flex-direction: column; }
        input, textarea { padding: 12px; margin-bottom: 1rem; border: 1px solid #ddd; border-radius: 5px; font-size: 1em; font-family: inherit; }
        input:focus, textarea:focus { outline: none; border-color: #667eea; box-shadow: 0 0 5px rgba(102, 126, 234, 0.3); }
        textarea { resize: vertical; min-height: 150px; }
        button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px; border: none; border-radius: 5px; font-size: 1em; cursor: pointer; font-weight: bold; }
        button:hover { opacity: 0.9; }
        .form-group { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; color: #333; font-weight: 500; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Get In Touch</h1>
        <form onsubmit="return validateForm(event)">
            <div class="form-group">
                <label>Name</label>
                <input type="text" name="name" required placeholder="Your full name">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required placeholder="your@email.com">
            </div>
            <div class="form-group">
                <label>Subject</label>
                <input type="text" name="subject" required placeholder="What is this about?">
            </div>
            <div class="form-group">
                <label>Message</label>
                <textarea name="message" required placeholder="Your message here..."></textarea>
            </div>
            <button type="submit">Send Message</button>
        </form>
    </div>
    <script>
        function validateForm(event) {
            event.preventDefault();
            const name = document.querySelector('input[name="name"]').value.trim();
            const email = document.querySelector('input[name="email"]').value.trim();
            const message = document.querySelector('textarea[name="message"]').value.trim();
            
            if (!name) { alert('Please enter your name'); return false; }
            if (!email) { alert('Please enter your email'); return false; }
            if (!message) { alert('Please enter a message'); return false; }
            
            alert('Thank you! Your message has been sent.');
            event.target.reset();
            return false;
        }
    </script>
</body>
</html>"""
        
        # Blog Website
        elif "blog" in prompt_lower or "article" in prompt_lower:
            return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tech Blog</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Georgia', serif; background: #f5f5f5; color: #333; }
        header { background: #2c3e50; color: white; padding: 2rem; text-align: center; }
        header h1 { margin-bottom: 0.5rem; }
        nav { background: #34495e; padding: 1rem; }
        nav a { color: white; margin: 0 1rem; text-decoration: none; }
        .container { max-width: 800px; margin: 2rem auto; }
        .post { background: white; padding: 2rem; margin-bottom: 2rem; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .post-title { color: #2c3e50; margin-bottom: 0.5rem; }
        .post-meta { color: #7f8c8d; font-size: 0.9em; margin-bottom: 1rem; }
        .post-content { line-height: 1.6; color: #555; }
        .post-content p { margin-bottom: 1rem; }
        footer { background: #2c3e50; color: white; padding: 2rem; text-align: center; margin-top: 3rem; }
    </style>
</head>
<body>
    <header>
        <h1>Tech Blog</h1>
        <p>Insights on web development and technology</p>
    </header>
    <nav>
        <a href="#home">Home</a>
        <a href="#posts">Posts</a>
        <a href="#about">About</a>
    </nav>
    <div class="container">
        <article class="post">
            <h2 class="post-title">Getting Started with Web Development</h2>
            <div class="post-meta">Posted on April 8, 2024 | By Author Name</div>
            <div class="post-content">
                <p>Web development is an exciting field that combines creativity with technical skills. In this post, we'll explore the fundamentals of building modern web applications.</p>
                <p>The first step is learning HTML, CSS, and JavaScript. These three technologies form the foundation of web development and all modern websites use some combination of these.</p>
                <p>Next, you'll want to explore frameworks like React, Vue, or Angular for building dynamic user interfaces. These tools make it easier to build complex applications efficiently.</p>
            </div>
        </article>
        <article class="post">
            <h2 class="post-title">Best Practices in Web Design</h2>
            <div class="post-meta">Posted on April 5, 2024 | By Author Name</div>
            <div class="post-content">
                <p>Good web design goes beyond just making things look pretty. It's about creating an intuitive user experience that guides visitors to their goals.</p>
                <p>Key principles include responsive design, clear typography, and consistent branding. Always prioritize user experience over trendy design choices.</p>
            </div>
        </article>
    </div>
    <footer>
        <p>&copy; 2024 Tech Blog. All rights reserved.</p>
    </footer>
</body>
</html>"""
        
        # Default fallback
        else:
            return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Website</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; padding: 3rem; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); text-align: center; }
        h1 { color: #333; margin-bottom: 1rem; }
        p { color: #666; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to Your Website</h1>
        <p>This is a placeholder website generated by AutoDevOS. The system is running in fallback mode with pre-built templates.</p>
        <p>When LLM services become available, websites will be fully customized based on your requirements.</p>
    </div>
</body>
</html>"""


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
        self.openai = OpenAIClient()     # Paid API - limited quota
        self.ollama = OllamaClient()     # Free local LLM with smart fallback

    def _choose_model_for_task(self, task: str) -> str:
        """
        Smart task routing: Route different tasks to optimal models.
        
        Returns:
        - "deepseek" for code generation (default best for coding)
        - "reasoning" for complex analysis/explanation
        - "template" for fallback/template-based responses
        """
        task_lower = task.lower()
        
        # Code generation tasks → DeepSeek (optimized for coding)
        code_keywords = ["generate", "code", "html", "css", "javascript", "create", "build", "write", "function"]
        if any(kw in task_lower for kw in code_keywords):
            return "deepseek"  # Optimized for code
        
        # Reasoning/analysis tasks → Mistral-like reasoning
        reasoning_keywords = ["analyze", "explain", "review", "assess", "evaluate", "compare", "suggest", "recommend"]
        if any(kw in task_lower for kw in reasoning_keywords):
            return "reasoning"  # For reasoning tasks
        
        # Default to DeepSeek (good for most tasks)
        return "deepseek"

    async def think(self, task: str, context: Dict[str, Any] = None) -> str:
        """
        Main thinking method with smart model routing:
        1. Choose optimal model based on task type
        2. Fetch high-reward past strategies from RL engine
        3. Build prompt with role + task + context + past strategies
        4. Call model with streaming
        5. Emit each chunk as agent_log WebSocket event
        6. Return full response
        """
        context = context or {}
        model_choice = self._choose_model_for_task(task)

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

        # Generate response with streaming - try OpenAI first, fallback to Ollama with smart generation
        full_response = ""
        token_buffer = ""
        is_first_chunk = True
        
        # Define client priority order: OpenAI → Ollama (with smart fallback mode)
        clients_to_try = []
        if os.getenv("OPENAI_API_KEY"):
            clients_to_try.append(("OpenAI", self.openai))
        clients_to_try.append(("Ollama", self.ollama))
        
        llm_success = False
        last_error = None
        
        for client_name, llm_client in clients_to_try:
            try:
                print(f"🤖 Attempting {client_name} for agent {self.name}...", flush=True)
                async for chunk in llm_client.generate(prompt, stream=True):
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
                
                llm_success = True
                print(f"✅ {client_name} succeeded for agent {self.name}", flush=True)
                break  # Success, exit the retry loop
                
            except Exception as e:
                last_error = str(e)
                print(f"⚠️  {client_name} failed: {e}", flush=True)
                continue  # Try next client in priority chain
        
        # If all clients failed, use the provided error response
        if not llm_success:
            error_msg = f"All LLM clients failed: {last_error}"
            print(f"❌ {error_msg}", flush=True)
            await self.emit("agent_log", f"Error generating response: {last_error}")
            full_response = f"# Error\nFailed to generate response: {last_error}"

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
