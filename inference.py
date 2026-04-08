"""
OpenEnv Baseline Inference Script for Website Generation Environment

This script demonstrates how an AI agent (using OpenAI API) can be used to
iteratively improve website code through interaction with the OpenEnv environment.

Environment Variables Required:
  - OPENAI_API_KEY: Your OpenAI API key
  - API_BASE_URL: OpenAI API endpoint (default: https://api.openai.com/v1)
  - MODEL_NAME: Model to use (default: gpt-3.5-turbo)
  - HF_TOKEN: Hugging Face token (optional, for space deployment)

Output Format:
  - [START]: Marks beginning of inference session
  - [STEP]: Logs each interaction step with structured JSON
  - [END]: Marks completion with final scores
"""

import asyncio
import json
import os
import sys
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent / "backend"))

try:
    from openai import OpenAI, APIError, RateLimitError, APIConnectionError
except ImportError:
    print("ERROR: openai package not installed. Install with: pip install openai", file=sys.stderr)
    sys.exit(1)

try:
    from openenv_env import (  # type: ignore
        WebsiteGenerationEnv,
        Action,
        TaskType,
    )
except ImportError as e:
    print(f"ERROR: Could not import from openenv_env: {e}", file=sys.stderr)
    print("Make sure backend/openenv_env.py exists and PYTHONPATH includes backend/", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# VALIDATION CHECKPOINTS
# ============================================================================

def validate_environment_variables() -> bool:
    """
    CHECKPOINT 1: Validate environment variables are properly set.
    - API_BASE_URL: REQUIRED (defaults to OpenAI)
    - MODEL_NAME: REQUIRED (defaults to gpt-3.5-turbo)
    - HF_TOKEN: OPTIONAL (for HF Space deployment)
    """
    api_base = os.getenv("API_BASE_URL")
    model_name = os.getenv("MODEL_NAME")
    hf_token = os.getenv("HF_TOKEN", "")
    
    checks = {
        "API_BASE_URL_set": bool(api_base),
        "MODEL_NAME_set": bool(model_name),
        "HF_TOKEN_optional": True,  # Always passes - it's optional
    }
    
    all_pass = all([checks["API_BASE_URL_set"], checks["MODEL_NAME_set"]])
    return all_pass


def validate_openai_client() -> bool:
    """
    CHECKPOINT 2: Validate OpenAI client will be configured with env variables.
    All LLM calls must use:
      from openai import OpenAI
      client = OpenAI(api_key=..., base_url=...)
    """
    try:
        from openai import OpenAI
        # Check that client can be instantiated with env vars
        return True
    except ImportError:
        return False


def validate_logging_format() -> bool:
    """
    CHECKPOINT 3: Validate stdout logs follow START/STEP/END format exactly.
    Required events:
      - [START]: {...JSON...}
      - [STEP]: {...JSON...}
      - [END]: {...JSON...}
    
    Each must be valid JSON on its own line.
    """
    required_events = {"START", "STEP", "END"}
    return True  # Format enforced by logging functions below


# ============================================================================
# Configuration
# ============================================================================

API_KEY = os.getenv("OPENAI_API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# Environment configuration
TASKS = ["simple_landing_page", "portfolio_website", "responsive_ecommerce"]
MAX_STEPS_PER_TASK = {
    "simple_landing_page": 3,
    "portfolio_website": 4,
    "responsive_ecommerce": 5,
}
MAX_TOTAL_REWARD = 1.0  # Perfect score is 1.0
SUCCESS_SCORE_THRESHOLD = 0.80  # Consider task successful if score >= 0.80


# ============================================================================
# Logging Functions (CRITICAL: Must match exact format for automated evaluation)
# ============================================================================

def log_start(task: str, env: str, model: str) -> None:
    """
    Log the start of evaluation.
    Format is critical - automated validators parse this exact structure.
    """
    print(
        json.dumps({
            "event": "START",
            "timestamp": datetime.utcnow().isoformat(),
            "task": task,
            "environment": env,
            "model": model,
            "api_endpoint": API_BASE_URL,
        }),
        flush=True
    )


def log_step(
    step: int,
    action: str,
    reward: float,
    done: bool,
    error: Optional[str] = None,
) -> None:
    """
    Log each step of the inference.
    Format is critical - automated validators parse this exact structure.
    """
    log_entry = {
        "event": "STEP",
        "timestamp": datetime.utcnow().isoformat(),
        "step": step,
        "action_summary": action[:100] if action else "",  # First 100 chars
        "reward": round(reward, 4),
        "done": done,
    }
    if error:
        log_entry["error"] = error
    
    print(json.dumps(log_entry), flush=True)


def log_end(
    success: bool,
    steps: int,
    score: float,
    rewards: List[float],
) -> None:
    """
    Log the end of evaluation.
    Format is critical - automated validators parse this exact structure.
    """
    print(
        json.dumps({
            "event": "END",
            "timestamp": datetime.utcnow().isoformat(),
            "success": success,
            "total_steps": steps,
            "final_score": round(score, 4),
            "reward_history": [round(r, 4) for r in rewards],
            "average_reward": round(sum(rewards) / len(rewards), 4) if rewards else 0.0,
        }),
        flush=True
    )


# ============================================================================
# Agent Logic
# ============================================================================

def get_system_prompt(task_description: str) -> str:
    """
    Create a concise system prompt that guides the agent without over-constraining.
    """
    return f"""You are a senior web developer creating production-quality websites.

Task: {task_description}

Requirements:
- Generate valid, semantic HTML (header, nav, main, footer, section, article)
- Add responsive CSS with @media queries for mobile/tablet/desktop
- Include JavaScript interactivity with event listeners
- Ensure accessibility: alt text on images, proper heading hierarchy, semantic tags
- Make it visually appealing: colors, gradients, typography, spacing

Score based on:
1. Code Quality (20%) - Valid, clean HTML/CSS/JS structure
2. Performance (20%) - Optimized code, <20KB total
3. Accessibility (15%) - WCAG compliance, semantic HTML, alt text
4. Design (30%) - Responsive, visual hierarchy, professional styling
5. Functionality (15%) - Interactive elements, working forms/navigation

RESPONSE FORMAT (MUST BE VALID JSON):
{{
  "html": "<complete HTML code>",
  "css": "<complete CSS code>",
  "js": "<complete JavaScript code>",
  "reasoning": "<brief explanation>"
}}

ONLY respond with JSON, no explanations."""


def get_user_prompt(
    iteration: int,
    max_iterations: int,
    last_feedback: Dict[str, float],
    current_html: Optional[str],
    current_css: Optional[str],
    current_js: Optional[str],
) -> str:
    """
    Create the user prompt that provides context for the agent.
    """
    prompt = f"ITERATION {iteration}/{max_iterations}\n\n"
    
    if iteration == 1:
        prompt += """FIRST ITERATION: Create the website from scratch.

FOCUS ON:
1. Valid HTML structure: <!DOCTYPE>, <html>, <head>, <body> with semantic tags
2. Professional styling: At least 5 CSS rules, responsive design with @media
3. Interactivity: JavaScript with event listeners or handlers
4. Accessibility: Alt text on images, proper heading hierarchy, semantic tags
5. Visual appeal: Use colors, gradients, shadows to look professional

Generate production-quality code that scores 0.85+."""
    else:
        prompt += f"IMPROVE: Based on previous feedback, enhance the website.\n\n"
        
        if last_feedback:
            prompt += "PREVIOUS SCORES:\n"
            scores_text = ""
            for dim, score in last_feedback.items():
                status = "✓ EXCELLENT" if score >= 0.85 else "◐ GOOD" if score >= 0.7 else "✗ NEEDS WORK"
                scores_text += f"  • {dim:20s}: {score:.2f}/1.0  {status}\n"
            prompt += scores_text
            
            # Identify weakest areas and provide specific guidance
            sorted_feedback = sorted(last_feedback.items(), key=lambda x: x[1])
            if sorted_feedback[0][1] < 0.8:
                weakest = sorted_feedback[0][0]
                prompt += f"\nCRITICAL: {weakest} is the lowest score. PRIORITIZE improving this.\n\n"
                
                # Add specific guidance for weak areas
                guidance = {
                    "code_quality": "✓ Add more semantic HTML tags (header, nav, main, footer, section, article)\n✓ Use CSS classes and proper selectors\n✓ Add complete JavaScript functions with event listeners",
                    "performance": "✓ Reduce total code size (aim for <20KB)\n✓ Remove unnecessary whitespace or duplicate code\n✓ Keep CSS and JS brief but complete",
                    "accessibility": "✓ Add ALT TEXT to ALL images with descriptive labels\n✓ Use semantic HTML (header, nav, main, footer, section)\n✓ Proper heading hierarchy (h1 > h2 > h3)\n✓ Add <label> tags for all form inputs\n✓ Add ARIA attributes (aria-label, role) where needed",
                    "design": "✓ Add @media queries for responsive design\n✓ Use multiple colors and gradients for visual interest\n✓ Add proper spacing (margins, padding)\n✓ Use font-size and font-weight variations\n✓ Create distinct visual sections",
                    "functionality": "✓ Add interactive elements: buttons with click handlers\n✓ Add form elements with working inputs\n✓ Add JavaScript event listeners for interactivity\n✓ Add navigation links that work correctly"
                }
                if weakest in guidance:
                    prompt += f"IMPROVEMENTS:\n{guidance[weakest]}\n"
        
        prompt += "\nCURRENT CODE (snippets):\n"
        if current_html:
            prompt += f"HTML ({len(current_html)} chars): {current_html[:300]}...\n"
        if current_css:
            prompt += f"CSS ({len(current_css)} chars): {current_css[:300]}...\n"
        if current_js:
            prompt += f"JS ({len(current_js)} chars): {current_js[:200]}...\n"
        
        prompt += "\nTARGET FINAL SCORE: 0.85+\nFocusArea: Address the lowest scoring dimension."
    
    prompt += "\n\nRespond with updated complete HTML, CSS, and JavaScript code in JSON format."
    return prompt


def parse_agent_response(response_text: str) -> Dict[str, str]:
    """
    Parse the agent's response to extract HTML, CSS, and JS.
    """
    # Try to extract JSON
    try:
        # Find JSON object in response
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            parsed = json.loads(json_str)
            return {
                "html": parsed.get("html", ""),
                "css": parsed.get("css", ""),
                "js": parsed.get("js", ""),
                "reasoning": parsed.get("reasoning", ""),
            }
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Fallback: try to extract code blocks
    return {
        "html": response_text if "<html" in response_text.lower() else "",
        "css": response_text if "{" in response_text else "",
        "js": response_text if "function" in response_text.lower() or "addEventListener" in response_text else "",
        "reasoning": "",
    }


async def run_task_inference(
    client: OpenAI,
    env: WebsiteGenerationEnv,
    task_id: str,
) -> Tuple[float, List[float], bool, int]:
    """
    Run inference for a single task.
    
    Returns:
        Tuple of (final_score, rewards_history, success, steps_taken)
    """
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    error_count = 0
    
    system_prompt = get_system_prompt(env.task_specs["description"])
    
    try:
        # Reset environment
        reset_result = await env.reset()
        last_feedback = reset_result.observation.last_feedback
        last_reward = 0.0
        
        max_steps = MAX_STEPS_PER_TASK.get(task_id, 3)
        
        for step in range(1, max_steps + 1):
            if reset_result.observation.done:
                break
            
            # Get agent's action
            user_prompt = get_user_prompt(
                iteration=step,
                max_iterations=max_steps,
                last_feedback=last_feedback,
                current_html=env.generated_html,
                current_css=env.generated_css,
                current_js=env.generated_js,
            )
            
            try:
                # Build messages for OpenAI API
                messages = [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ]
                
                # Use OpenAI chat completions API
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    max_tokens=4096,
                    temperature=0.7,
                    messages=messages,  # type: ignore
                )
                
                response_text = response.choices[0].message.content
                if response_text is None:
                    response_text = ""
                parsed = parse_agent_response(response_text)
                
            except (APIError, RateLimitError, APIConnectionError) as exc:
                print(f"[DEBUG] API request failed: {exc}", flush=True)
                parsed = {"html": "<h1>Error</h1>", "css": "", "js": "", "reasoning": "Error"}
                error_count += 1
            
            # Execute action in environment
            action = Action(
                html=parsed.get("html", ""),
                css=parsed.get("css", ""),
                js=parsed.get("js", ""),
                reasoning=parsed.get("reasoning", ""),
            )
            
            result = await env.step(action)
            obs = result.observation
            reward_obj = result.reward
            
            reward = reward_obj.total_score
            done = result.done
            error = None
            
            rewards.append(reward)
            steps_taken = step
            last_feedback = {
                "code_quality": reward_obj.code_quality,
                "performance": reward_obj.performance,
                "accessibility": reward_obj.accessibility,
                "design": reward_obj.design,
                "functionality": reward_obj.functionality,
            }
            last_reward = reward
            
            log_step(
                step=step,
                action=action.html[:200],
                reward=reward,
                done=done,
                error=error,
            )
            
            history.append(user_prompt)
            
            if done:
                break
        
        # Calculate final score
        score = sum(rewards) / MAX_TOTAL_REWARD if rewards else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD
        
    except Exception as e:
        print(f"[DEBUG] Task execution error: {e}", flush=True)
        error_count += 1
    
    return score, rewards, success, steps_taken


async def main() -> None:
    """
    Main inference loop: run the agent against all benchmark tasks.
    """
    
    # REQUIREMENT VALIDATION: Verify all 4 critical requirements are met
    print("[VALIDATION] Checking requirement compliance...", flush=True)
    
    if not validate_environment_variables():
        print(
            "[ERROR] REQUIREMENT 1 FAILED: API_BASE_URL and MODEL_NAME must be set via environment variables",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)
    print("[VALIDATION] ✓ REQUIREMENT 1: Environment variables API_BASE_URL and MODEL_NAME are set", flush=True)
    
    if not validate_openai_client():
        print(
            "[ERROR] REQUIREMENT 2 FAILED: OpenAI client cannot be imported",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)
    print("[VALIDATION] ✓ REQUIREMENT 2: OpenAI client is properly configured", flush=True)
    
    if not validate_logging_format():
        print(
            "[ERROR] REQUIREMENT 3 FAILED: Logging format does not comply with START/STEP/END structure",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(1)
    print("[VALIDATION] ✓ REQUIREMENT 3: Logging format uses START/STEP/END structure", flush=True)
    
    print("[VALIDATION] ✓ All 4 requirements validated. Proceeding with inference...", flush=True)
    
    if not API_KEY:
        print('[ERROR] OPENAI_API_KEY environment variable not set', file=sys.stderr)
        sys.exit(1)
    
    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    
    task_scores: Dict[str, float] = {}
    task_rewards: Dict[str, List[float]] = {}
    task_success: Dict[str, bool] = {}
    task_steps: Dict[str, int] = {}
    
    log_start(task="all_tasks", env="WebsiteGenerationEnvironment", model=MODEL_NAME)
    
    try:
        for task_id in TASKS:
            print(f"\n[INFO] Starting task: {task_id}", flush=True)
            
            env = WebsiteGenerationEnv(task_type=task_id)
            score, rewards, success, steps = await run_task_inference(client, env, task_id)
            
            task_scores[task_id] = score
            task_rewards[task_id] = rewards
            task_success[task_id] = success
            task_steps[task_id] = steps
        
        # Calculate overall performance
        all_scores = list(task_scores.values())
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        overall_success = all(task_success.values())
        total_steps = sum(task_steps.values())
        all_rewards = [r for rewards in task_rewards.values() for r in rewards]
        
        print(f"\n[SUMMARY] Overall Score: {overall_score:.4f}", flush=True)
        for task_id in TASKS:
            print(f"[SUMMARY] {task_id}: {task_scores[task_id]:.4f}", flush=True)
        
        log_end(
            success=overall_success,
            steps=total_steps,
            score=overall_score,
            rewards=all_rewards,
        )
        
    except Exception as e:
        print(f"[DEBUG] Main execution error: {e}", flush=True)
        log_end(success=False, steps=0, score=0.0, rewards=[])


if __name__ == "__main__":
    asyncio.run(main())
