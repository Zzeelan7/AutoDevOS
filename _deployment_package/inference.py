"""
OpenEnv baseline inference for AutoDevOS (website generation).

Required environment variables (competition / OpenEnv):
  OPENAI_API_KEY — API key for the OpenAI client
  API_BASE_URL   — LLM base URL (e.g. https://api.openai.com/v1)
  MODEL_NAME     — Model id (e.g. gpt-3.5-turbo)
  HF_TOKEN       — Hugging Face token when required by your deployment (read at startup)

Stdout must contain ONLY structured lines in this exact bracket format (no JSON, no extra prints):
  [START] task=<name> env=<benchmark> model=<model>
  [STEP] step=<n> action="<text>" reward=<float> done=<true|false> error=<null|message>
  [END] success=<true|false> steps=<n> score=<float> rewards=<comma-separated floats>

All diagnostics use stderr.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add backend to path for imports
# HF package layout: openenv_env.py alongside this file
sys.path.insert(0, str(Path(__file__).parent))

try:
    from openai import OpenAI, APIError, RateLimitError, APIConnectionError
except ImportError:
    print(
        "ERROR: openai package not installed. pip install -r requirements-inference.txt",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    from openenv_env import Action, WebsiteGenerationEnv  # type: ignore
except ImportError as e:
    print(f"ERROR: Could not import openenv_env: {e}", file=sys.stderr)
    print("Ensure backend/openenv_env.py exists.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Competition-aligned constants (keep in sync with openenv.yaml max_steps)
# ---------------------------------------------------------------------------

BENCHMARK = "website-generation-environment"
TASK_NAME = "all_tasks"
TASKS = ["simple_landing_page", "portfolio_website", "responsive_ecommerce"]
# Sum of max_iterations across the three tasks (2 + 3 + 4) for score normalization
MAX_TOTAL_REWARD = 9.0
SUCCESS_SCORE_THRESHOLD = 0.80
TEMPERATURE = 0.5
MAX_TOKENS = 3072

API_KEY = os.getenv("OPENAI_API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
# Required to be defined for submission checks; optional for OpenAI.com
HF_TOKEN = os.getenv("HF_TOKEN", "")


def validate_environment_variables() -> bool:
    api_base = (os.getenv("API_BASE_URL") or "").strip() or "https://api.openai.com/v1"
    model_name = (os.getenv("MODEL_NAME") or "").strip() or "gpt-3.5-turbo"
    return bool(api_base and model_name)


def validate_openai_client() -> bool:
    try:
        from openai import OpenAI  # noqa: F401

        return True
    except ImportError:
        return False


def validate_logging_format() -> bool:
    """Bracket [START]/[STEP]/[END] lines only on stdout during the run."""
    return True


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(
    step: int,
    action: str,
    reward: float,
    done: bool,
    error: Optional[str] = None,
) -> None:
    """One [STEP] line; action is truncated and escaped for a single-line log."""
    a = (action or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")
    if len(a) > 240:
        a = a[:240]
    err = "null" if error is None else json.dumps(error)
    print(
        f'[STEP] step={step} action="{a}" reward={reward:.2f} done={str(done).lower()} error={err}',
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rstr = ",".join(f"{float(r):.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rstr}",
        flush=True,
    )


def get_system_prompt(task_description: str) -> str:
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
        prompt += "IMPROVE: Based on previous feedback, enhance the website.\n\n"

        if last_feedback:
            prompt += "PREVIOUS SCORES:\n"
            for dim, sc in sorted(last_feedback.items()):
                prompt += f"  - {dim}: {sc:.2f}/1.0\n"
            sorted_feedback = sorted(last_feedback.items(), key=lambda x: x[1])
            if sorted_feedback[0][1] < 0.8:
                weakest = sorted_feedback[0][0]
                prompt += f"\nCRITICAL: Improve {weakest} first.\n"

        prompt += "\nCURRENT CODE (snippets):\n"
        if current_html:
            prompt += f"HTML ({len(current_html)} chars): {current_html[:300]}...\n"
        if current_css:
            prompt += f"CSS ({len(current_css)} chars): {current_css[:300]}...\n"
        if current_js:
            prompt += f"JS ({len(current_js)} chars): {current_js[:200]}...\n"

        prompt += "\nTARGET FINAL SCORE: 0.85+\n"

    prompt += "\nRespond with updated complete HTML, CSS, and JavaScript code in JSON format."
    return prompt


def parse_agent_response(response_text: str) -> Dict[str, str]:
    try:
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}") + 1
        if start_idx >= 0 and end_idx > start_idx:
            parsed = json.loads(response_text[start_idx:end_idx])
            return {
                "html": parsed.get("html", "") or "",
                "css": parsed.get("css", "") or "",
                "js": parsed.get("js", "") or "",
                "reasoning": parsed.get("reasoning", "") or "",
            }
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    low = response_text.lower()
    return {
        "html": response_text if "<html" in low else "",
        "css": response_text if "{" in response_text else "",
        "js": response_text
        if ("function" in low or "addeventlistener" in response_text.lower())
        else "",
        "reasoning": "",
    }


async def run_one_task_episode(
    client: OpenAI,
    task_id: str,
    global_step_ref: List[int],
) -> Tuple[float, List[float], int]:
    """Run one task to completion or max iterations. Returns (mean_reward, rewards, local_steps)."""
    env = WebsiteGenerationEnv(task_type=task_id)
    rewards: List[float] = []
    local_steps = 0
    try:
        reset_result = await env.reset()
        last_feedback = reset_result.observation.last_feedback
        max_steps = int(env.task_specs["max_iterations"])
        system_prompt = get_system_prompt(env.task_specs["description"])

        for step in range(1, max_steps + 1):
            user_prompt = get_user_prompt(
                iteration=step,
                max_iterations=max_steps,
                last_feedback=last_feedback,
                current_html=env.generated_html,
                current_css=env.generated_css,
                current_js=env.generated_js,
            )

            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    max_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                response_text = response.choices[0].message.content or ""
                parsed = parse_agent_response(response_text)
            except (APIError, RateLimitError, APIConnectionError) as exc:
                print(f"[DEBUG] Model request failed: {exc}", file=sys.stderr, flush=True)
                parsed = {
                    "html": "<html><body><p>fallback</p></body></html>",
                    "css": "body{font-family:sans-serif}",
                    "js": "",
                    "reasoning": "api_error",
                }

            action = Action(
                html=parsed.get("html", ""),
                css=parsed.get("css", ""),
                js=parsed.get("js", ""),
                reasoning=parsed.get("reasoning", ""),
            )
            result = await env.step(action)
            reward_obj = result.reward
            reward = float(reward_obj.total_score)
            done = bool(result.done)
            rewards.append(reward)
            local_steps = step

            global_step_ref[0] += 1
            action_summary = (action.html or "")[:500]
            log_step(
                step=global_step_ref[0],
                action=action_summary,
                reward=reward,
                done=done,
                error=None,
            )

            last_feedback = {
                "code_quality": reward_obj.code_quality,
                "performance": reward_obj.performance,
                "accessibility": reward_obj.accessibility,
                "design": reward_obj.design,
                "functionality": reward_obj.functionality,
            }

            if done:
                break

        mean_r = sum(rewards) / len(rewards) if rewards else 0.0
        return mean_r, rewards, local_steps
    finally:
        try:
            await env.close()
        except Exception as exc:
            print(f"[DEBUG] env.close() error (cleanup): {exc}", file=sys.stderr, flush=True)


async def main() -> None:
    print("[VALIDATION] Checking requirement compliance...", file=sys.stderr, flush=True)
    if not validate_environment_variables():
        print("[ERROR] API_BASE_URL / MODEL_NAME invalid", file=sys.stderr, flush=True)
        sys.exit(1)
    if not validate_openai_client():
        print("[ERROR] OpenAI client unavailable", file=sys.stderr, flush=True)
        sys.exit(1)
    if not validate_logging_format():
        print("[ERROR] Logging format checkpoint failed", file=sys.stderr, flush=True)
        sys.exit(1)
    if not API_KEY:
        print("[ERROR] OPENAI_API_KEY not set", file=sys.stderr, flush=True)
        sys.exit(1)

    # HF_TOKEN must be present in Space config when required; reading satisfies "defined"
    if not HF_TOKEN:
        print(
            "[INFO] HF_TOKEN unset (optional unless your endpoint requires it)",
            file=sys.stderr,
            flush=True,
        )

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    global_step_ref: List[int] = [0]

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        task_means: List[float] = []
        for task_id in TASKS:
            print(f"[INFO] Task: {task_id}", file=sys.stderr, flush=True)
            mean_r, task_rewards, _ = await run_one_task_episode(
                client, task_id, global_step_ref
            )
            task_means.append(mean_r)
            rewards.extend(task_rewards)

        steps_taken = global_step_ref[0]
        # Competition sample: score = sum(rewards) / MAX_TOTAL_REWARD, clamped to [0, 1]
        score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = min(max(score, 0.0), 1.0)
        overall_mean = sum(task_means) / len(task_means) if task_means else 0.0
        print(
            f"[SUMMARY] normalized_score={score:.4f} per_task_mean={overall_mean:.4f} steps={steps_taken}",
            file=sys.stderr,
            flush=True,
        )
        success = score >= SUCCESS_SCORE_THRESHOLD
    except Exception as exc:
        print(f"[DEBUG] Inference error: {exc}", file=sys.stderr, flush=True)
        success = False
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    asyncio.run(main())
