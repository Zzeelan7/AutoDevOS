"""
LLM Code Generation Integration
Supports: Ollama DeepSeek Coder (local), OpenAI GPT (cloud), GitHub Marketplace Models (fallback)
"""
import os
import asyncio
from typing import Optional, Dict
import aiohttp
import json

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:latest"

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-3.5-turbo"

# GitHub Marketplace Models Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_MODEL = "gpt-4-turbo"  # Claude 3.5 Sonnet, GPT-4 Turbo available
GITHUB_API_ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"

class LLMCodeGenerator:
    """Generate production-grade HTML/CSS/JS code from prompts"""
    
    def __init__(self):
        self.ollama_available = False
        self.openai_available = bool(OPENAI_API_KEY)
        self.github_available = bool(GITHUB_TOKEN)
        self.openai_quota_exceeded = False
        self._check_ollama()
        
        print("[LLM] Backend Status:")
        print(f"  Ollama: {'Available' if self.ollama_available else 'Not Available'}")
        print(f"  OpenAI: {'Available' if self.openai_available else 'Not Available'}")
        print(f"  GitHub: {'Available' if self.github_available else 'Not Available'}")
    
    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            import requests
            resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                # Simply check if Ollama is running with ANY models
                # We'll use whatever model is configured (llama3, deepseek, etc)
                self.ollama_available = len(model_names) > 0
                if self.ollama_available:
                    print(f"[LLM] OK Ollama available")
                    print(f"      Available models: {model_names}")
                    print(f"      Using model: {OLLAMA_MODEL}")
                else:
                    print(f"[LLM] NOTE Ollama is running but no models found")
            else:
                self.ollama_available = False
                print(f"[LLM] NOTE Ollama returned status {resp.status_code}")
        except Exception as e:
            self.ollama_available = False
            # Handle both requests-specific and other exceptions
            if "ConnectionError" in type(e).__name__:
                print(f"[LLM] NOTE Cannot connect to Ollama at {OLLAMA_BASE_URL}")
            else:
                print(f"[LLM] NOTE Error checking Ollama: {e}")
    
    async def generate_code(self, prompt: str, code_type: str = "full") -> Dict[str, str]:
        """
        Generate production-grade code from prompt.
        Fallback order: Ollama → OpenAI → GitHub Marketplace
        
        Args:
            prompt: The design/feature requirements
            code_type: "full" (HTML+CSS+JS), "html", "css", "js"
        
        Returns:
            {"html": "...", "css": "...", "js": "..."}
        """
        
        # Always re-check Ollama availability (it might have started after module import)
        self._check_ollama()
        
        # Try Ollama first (free, local, fast)
        if self.ollama_available:
            print("[LLM] [OLLAMA] Generating with Ollama DeepSeek Coder...")
            try:
                code = await self._generate_with_ollama(prompt, code_type)
                if code and any(code.values()):  # Check if code blocks have content
                    print("[LLM] [OK] Ollama generation successful")
                    return code
                else:
                    print("[LLM] [WARN] Ollama returned empty code, trying OpenAI...")
            except Exception as e:
                print(f"[LLM] [ERROR] Ollama error: {e}, trying OpenAI...")
        
        # Try OpenAI (quota-aware with fallback)
        if self.openai_available and not self.openai_quota_exceeded:
            print("[LLM] [OPENAI] Generating with OpenAI GPT-3.5-turbo...")
            try:
                code = await self._generate_with_openai(prompt, code_type)
                if code and any(code.values()):
                    print("[LLM] [OK] OpenAI generation successful")
                    return code
                else:
                    print("[LLM] [WARN] OpenAI returned empty code")
            except Exception as e:
                error_str = str(e).lower()
                if "quota" in error_str or "rate" in error_str or "limit" in error_str:
                    print(f"[LLM] [QUOTA] OpenAI quota exceeded: {e}")
                    print("[LLM] Switching to GitHub Marketplace Models...")
                    self.openai_quota_exceeded = True
                else:
                    print(f"[LLM] [ERROR] OpenAI error: {e}")
        
        # Fallback to GitHub Marketplace Models (unlimited tier)
        if self.github_available or self.openai_quota_exceeded:
            print("[LLM] [GITHUB] Generating with GitHub Marketplace Models...")
            try:
                code = await self._generate_with_github(prompt, code_type)
                if code and any(code.values()):
                    print("[LLM] [OK] GitHub generation successful")
                    return code
                else:
                    print("[LLM] [WARN] GitHub returned empty code")
            except Exception as e:
                print(f"[LLM] [ERROR] GitHub error: {e}")
        
        # No fallback template - require real LLM output
        error_msg = "[LLM] [FAIL] ERROR: No LLM backends available!"
        print(error_msg)
        print(f"  Ollama available: {self.ollama_available}")
        print(f"  OpenAI available: {self.openai_available} (quota exceeded: {self.openai_quota_exceeded})")
        print(f"  GitHub available: {self.github_available}")
        raise RuntimeError(f"Code generation failed: No available LLM backends")
    
    async def _generate_with_ollama(self, prompt: str, code_type: str) -> Optional[Dict[str, str]]:
        """Generate code using local Ollama DeepSeek Coder"""
        try:
            generation_prompt = self._create_generation_prompt(prompt, code_type)
            print(f"[LLM] Ollama prompt length: {len(generation_prompt)} chars")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": generation_prompt,
                        "stream": False,
                        "temperature": 0.3,  # Lower for consistent code
                        "top_p": 0.9,
                    },
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        generated = result.get("response", "")
                        print(f"[LLM] Ollama response length: {len(generated)} chars")
                        
                        # Debug: print first 300 chars of response
                        if generated:
                            print(f"[LLM] Response preview: {generated[:300]}")
                        else:
                            print(f"[LLM] Empty response from Ollama!")
                        
                        parsed = self._parse_generated_code(generated, code_type)
                        print(f"[LLM] Parsed HTML: {len(parsed.get('html', ''))} chars")
                        print(f"[LLM] Parsed CSS: {len(parsed.get('css', ''))} chars")
                        print(f"[LLM] Parsed JS: {len(parsed.get('js', ''))} chars")
                        return parsed
                    else:
                        print(f"[LLM] Ollama error response: {resp.status}")
                        text = await resp.text()
                        print(f"[LLM] Response: {text[:200]}")
        except Exception as e:
            print(f"[LLM] Ollama exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    async def _generate_with_openai(self, prompt: str, code_type: str) -> Optional[Dict[str, str]]:
        """Generate code using OpenAI GPT"""
        try:
            if not OPENAI_API_KEY:
                print(f"[LLM] [WARN] OpenAI API key not set!")
                return None
                
            generation_prompt = self._create_generation_prompt(prompt, code_type)
            
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": OPENAI_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert web developer. Generate clean, production-ready code."
                            },
                            {
                                "role": "user",
                                "content": generation_prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4000
                    },
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        generated = result["choices"][0]["message"]["content"]
                        print(f"[LLM] OpenAI response length: {len(generated)} chars")
                        
                        if generated:
                            print(f"[LLM] Response preview: {generated[:300]}")
                        else:
                            print(f"[LLM] Empty response from OpenAI!")
                        
                        parsed = self._parse_generated_code(generated, code_type)
                        print(f"[LLM] Parsed HTML: {len(parsed.get('html', ''))} chars")
                        print(f"[LLM] Parsed CSS: {len(parsed.get('css', ''))} chars")
                        print(f"[LLM] Parsed JS: {len(parsed.get('js', ''))} chars")
                        return parsed
                    else:
                        print(f"[LLM] OpenAI error response: {resp.status}")
                        text = await resp.text()
                        print(f"[LLM] Response: {text[:300]}")
        except Exception as e:
            print(f"[LLM] OpenAI exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    async def _generate_with_github(self, prompt: str, code_type: str) -> Optional[Dict[str, str]]:
        """Generate code using GitHub Marketplace Models (unlimited quota)"""
        try:
            if not GITHUB_TOKEN:
                print(f"[LLM] [WARN] GitHub token not set!")
                return None
                
            generation_prompt = self._create_generation_prompt(prompt, code_type)
            
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    GITHUB_API_ENDPOINT,
                    json={
                        "model": GITHUB_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert web developer. Generate clean, production-ready HTML, CSS, and JavaScript code."
                            },
                            {
                                "role": "user",
                                "content": generation_prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4000
                    },
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        generated = result["choices"][0]["message"]["content"]
                        print(f"[LLM] GitHub response length: {len(generated)} chars")
                        
                        if generated:
                            print(f"[LLM] Response preview: {generated[:300]}")
                        else:
                            print(f"[LLM] Empty response from GitHub!")
                        
                        parsed = self._parse_generated_code(generated, code_type)
                        print(f"[LLM] Parsed HTML: {len(parsed.get('html', ''))} chars")
                        print(f"[LLM] Parsed CSS: {len(parsed.get('css', ''))} chars")
                        print(f"[LLM] Parsed JS: {len(parsed.get('js', ''))} chars")
                        return parsed
                    else:
                        print(f"[LLM] GitHub error response: {resp.status}")
                        text = await resp.text()
                        print(f"[LLM] Response: {text[:300]}")
                        
                        # Check for quota errors
                        if resp.status == 429:
                            raise RuntimeError("GitHub quota exceeded")
                        
        except Exception as e:
            print(f"[LLM] GitHub exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _create_generation_prompt(self, prompt: str, code_type: str) -> str:
        """Create the code generation prompt"""
        
        if code_type == "html":
            return f"""Generate ONLY valid, semantic HTML5 code for this requirement:
{prompt}

Return ONLY the HTML code, nothing else. Include proper meta tags, SEO, and accessibility (aria-labels)."""
        
        elif code_type == "css":
            return f"""Generate ONLY production-grade CSS code for this requirement:
{prompt}

Use CSS variables for colors, implement responsive design with @media queries, include animations and transitions.
Return ONLY the CSS code, nothing else."""
        
        elif code_type == "js":
            return f"""Generate ONLY clean, production-ready JavaScript code for this requirement:
{prompt}

Include proper error handling, modular structure (classes or functions), event listeners, and lazy loading.
Return ONLY the JavaScript code, nothing else."""
        
        else:  # full
            return f"""You are a Senior Full-Stack Engineer. Generate production-grade, marketable code.

REQUIREMENT:
{prompt}

Generate THREE separate code blocks:

```html
<!DOCTYPE html>
<html>
...complete semantic HTML5...
</html>
```

```css
/* complete production CSS with variables and responsive design */
```

```javascript
// complete production JavaScript with proper structure
```

Ensure:
- Semantic HTML5 (header, main, section, footer, article)
- CSS variables for luxury palette (#1A1A1A, #F5F5F5, #C5A059)
- Glassmorphism effects and animations
- IntersectionObserver for lazy loading
- Form validation and drag-drop if applicable
- Stripe-ready checkout mock if ecommerce
- Schema.org JSON-LD for SEO
- Mobile-first responsive design"""
    
    def _parse_generated_code(self, response: str, code_type: str) -> Dict[str, str]:
        """Parse code from LLM response"""
        result = {"html": "", "css": "", "js": ""}
        
        if code_type == "full":
            # Extract code blocks
            import re
            
            # Try to find code blocks with markdown formatting
            html_match = re.search(r"```html\n(.*?)\n```", response, re.DOTALL)
            css_match = re.search(r"```css\n(.*?)\n```", response, re.DOTALL)
            js_match = re.search(r"```(?:javascript|js)\n(.*?)\n```", response, re.DOTALL)
            
            result["html"] = html_match.group(1).strip() if html_match else ""
            result["css"] = css_match.group(1).strip() if css_match else ""
            result["js"] = js_match.group(1).strip() if js_match else ""
            
            # Debug output
            print(f"[LLM] Parse attempt:")
            print(f"      HTML found: {bool(html_match)} ({len(result['html'])} chars)")
            print(f"      CSS found: {bool(css_match)} ({len(result['css'])} chars)")
            print(f"      JS found: {bool(js_match)} ({len(result['js'])} chars)")
            
            # If any are missing, try alternative patterns
            if not html_match or not css_match or not js_match:
                print(f"[LLM] Some code blocks missing, trying alternative patterns...")
                # Try with different formats that might appear
                alt_html = re.search(r"```html(.*?)```", response, re.DOTALL)
                alt_css = re.search(r"```css(.*?)```", response, re.DOTALL)
                alt_js = re.search(r"```(?:javascript|js)(.*?)```", response, re.DOTALL)
                
                if alt_html and not html_match:
                    result["html"] = alt_html.group(1).strip()
                    print(f"[LLM] Found HTML with alt pattern")
                if alt_css and not css_match:
                    result["css"] = alt_css.group(1).strip()
                    print(f"[LLM] Found CSS with alt pattern")
                if alt_js and not js_match:
                    result["js"] = alt_js.group(1).strip()
                    print(f"[LLM] Found JS with alt pattern")
                    
        else:
            result[code_type] = response.strip()
        
        return result
    
# Initialize generator
code_generator = LLMCodeGenerator()

async def generate_production_code(prompt: str) -> Dict[str, str]:
    """Public API for code generation"""
    return await code_generator.generate_code(prompt, "full")
