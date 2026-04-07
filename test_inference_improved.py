"""
Focused inference test to evaluate score improvement with better prompts and gpt-4-turbo
"""

import asyncio
import json
import os
import sys
from typing import Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from backend.openenv_env import WebsiteGenerationEnv, Action


# Configuration
API_KEY = os.getenv("OPENAI_API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

# Test configuration
TEST_TASKS = ["simple_landing_page", "portfolio_website", "responsive_ecommerce"]
MAX_STEPS_PER_TASK = 3


async def run_single_task_inference(task_id: str, max_steps: int = 3) -> Dict:
    """Run inference for a single task and return results."""
    
    if not API_KEY:
        print('[ERROR] OPENAI_API_KEY environment variable not set', file=sys.stderr)
        return {"task": task_id, "error": "No API key"}
    
    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    
    try:
        env = WebsiteGenerationEnv(task_type=task_id)
        reset_result = await env.reset()
        
        task_description = env.task_specs["description"]
        rewards = []
        last_feedback: Dict[str, float] = {}
        
        print(f"\n{'='*70}")
        print(f"TASK: {task_id}")
        print(f"{'='*70}")
        print(f"Description: {task_description}\n")
        
        for step_num in range(1, max_steps + 1):
            if reset_result.observation.done:
                break
            
            print(f"[STEP {step_num}/{max_steps}] Generating code...")
            
            # Build the prompt
            system_prompt = f"""You are an expert web developer tasked with creating production-quality HTML/CSS/JavaScript code.

TASK: {task_description}

CRITICAL SCORING RUBRIC (Higher scores = better):
Your code will be scored on these weighted criteria:
  1. CODE_QUALITY (20%): Valid, clean, well-structured code
     - Valid HTML: DOCTYPE, meta tags, semantic structure (header, nav, main, footer, section, article)
     - Valid CSS: proper selectors, flexbox/grid layouts, zero unused styles
     - Valid JS: proper functions, event listeners, DOM manipulation
  
  2. PERFORMANCE (20%): Efficiency and optimization
     - Keep total code < 20KB
     - No excessive whitespace, inline styles only when necessary
     - Separate CSS and JS from HTML
  
  3. ACCESSIBILITY (15%): WCAG compliance
     - ALL images must have descriptive alt="" text
     - Use semantic HTML tags (header, nav, main, footer, section, article)
     - Proper heading hierarchy (h1 → h2 → h3)
     - Form labels must be associated with inputs via <label> tags
     - Include ARIA attributes (aria-label, aria-live, role) where appropriate
  
  4. DESIGN (30%): Visual appeal and UX
     - Responsive design with @media queries for mobile/tablet/desktop
     - Color scheme with at least 2-3 complementary colors
     - Professional typography (font-size variations, font-weight)
     - Proper spacing (margins, padding) creating visual hierarchy
     - At least 3 distinct sections with clear layout (header, content, footer)
  
  5. FUNCTIONALITY (15%): Interactive features
     - Include buttons with onclick handlers or event listeners
     - Form elements (input, textarea, select) with proper handling
     - Navigation links that work
     - JavaScript interactivity (at least 2 features)

RESPONSE FORMAT (MUST BE VALID JSON):
{{
  "html": "<complete HTML code>",
  "css": "<complete CSS code>",
  "js": "<complete JavaScript code>",
  "reasoning": "<brief explanation>"
}}"""
            
            if step_num == 1:
                user_prompt = """FIRST ITERATION: Create the website from scratch.

FOCUS ON:
1. Valid HTML structure with semantic tags
2. Professional styling with responsive design
3. Interactivity with JavaScript
4. Accessibility features (alt text, labels, ARIA)
5. Visual appeal with colors and spacing

Target score: 0.85+"""
            else:
                user_prompt = f"ITERATION {step_num}/3\n\n"
                user_prompt += "IMPROVE: Based on feedback, enhance the code.\n\n"
                
                if last_feedback:
                    user_prompt += "SCORES FROM PREVIOUS ITERATION:\n"
                    for dim, score in last_feedback.items():
                        status = "✓" if score >= 0.8 else "⚠" if score >= 0.6 else "✗"
                        user_prompt += f"  {status} {dim}: {score:.2f}/1.0\n"
                    
                    # Find weakest area
                    weakest = min(last_feedback.items(), key=lambda x: x[1])
                    user_prompt += f"\nFOCUS: Improve {weakest[0]} (currently {weakest[1]:.2f})\n"
                
                user_prompt += "\nProvide COMPLETE updated HTML, CSS, and JavaScript in JSON format."
            
            try:
                # Call OpenAI API
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    max_tokens=4096,
                    temperature=0.7,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                
                response_text = response.choices[0].message.content
                if response_text is None:
                    response_text = ""
                
                # Parse JSON from response
                try:
                    start_idx = response_text.find("{")
                    end_idx = response_text.rfind("}") + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        parsed = json.loads(json_str)
                    else:
                        parsed = {"html": "", "css": "", "js": "", "reasoning": "Parse error"}
                except json.JSONDecodeError:
                    parsed = {"html": "", "css": "", "js": "", "reasoning": "JSON parse failed"}
                
                # Execute action in environment
                action = Action(
                    html=parsed.get("html", ""),
                    css=parsed.get("css", ""),
                    js=parsed.get("js", ""),
                    reasoning=parsed.get("reasoning", ""),
                )
                
                result = await env.step(action)
                reward = result.reward
                
                rewards.append(reward.total_score)
                last_feedback = {
                    "code_quality": reward.code_quality,
                    "performance": reward.performance,
                    "accessibility": reward.accessibility,
                    "design": reward.design,
                    "functionality": reward.functionality,
                }
                
                print(f"  Score: {reward.total_score:.3f}")
                print(f"    HTML Quality: {reward.code_quality:.3f}")
                print(f"    Performance:  {reward.performance:.3f}")
                print(f"    Accessibility: {reward.accessibility:.3f}")
                print(f"    Design:       {reward.design:.3f}")
                print(f"    Functionality: {reward.functionality:.3f}")
                
                if result.done:
                    print(f"  [DONE]")
                    break
                    
            except (APIError, RateLimitError, APIConnectionError) as exc:
                print(f"  [ERROR] API request failed: {exc}")
                break
        
        # Calculate final score
        final_score = sum(rewards) / len(rewards) if rewards else 0.0
        success = final_score >= 0.80
        
        return {
            "task": task_id,
            "final_score": round(final_score, 3),
            "rewards": [round(r, 3) for r in rewards],
            "success": success,
            "num_steps": len(rewards),
        }
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return {"task": task_id, "error": str(e)}


async def main():
    """Run inference on all test tasks."""
    
    model_to_test = MODEL_NAME
    print(f"\n{'='*70}")
    print(f"INFERENCE TEST: {model_to_test}")
    print(f"Target: Improve from 0.70 to 0.8-0.9")
    print(f"{'='*70}\n")
    
    results = []
    
    for task_id in TEST_TASKS:
        result = await run_single_task_inference(task_id, max_steps=MAX_STEPS_PER_TASK)
        results.append(result)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*70}\n")
    
    for result in results:
        if "error" in result:
            print(f"❌ {result['task']}: ERROR - {result['error']}")
        else:
            status = "✅ PASS" if result['success'] else "⚠️  PARTIAL"
            print(f"{status} {result['task']:30s}: {result['final_score']:.3f} (steps: {result['num_steps']})")
    
    # Overall score
    successful_scores = [r["final_score"] for r in results if "final_score" in r]
    if successful_scores:
        overall = sum(successful_scores) / len(successful_scores)
        print(f"\nOverall Average: {overall:.3f}")
        if overall >= 0.80:
            print("✅ TARGET ACHIEVED: Average >= 0.80")
        elif overall >= 0.75:
            print("⚠️  PARTIAL SUCCESS: Average >= 0.75")
        else:
            print("❌ NEEDS IMPROVEMENT: Average < 0.75")


if __name__ == "__main__":
    asyncio.run(main())
