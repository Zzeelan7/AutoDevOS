"""Tech Debt Agent - Identifies refactoring opportunities"""
from agents.base import BaseAgent
import json
import re


class TechDebtAgent(BaseAgent):
    """Tech Debt Engineer - Reviews code for optimization opportunities"""

    def __init__(self, redis_client, job_id: str, rl_engine=None):
        super().__init__(
            name="tech_debt",
            role_description=(
                "You are the Tech Debt Engineer at AutoDevOS. Review the codebase for: "
                "redundant CSS, inline styles that should be classes, repeated HTML patterns "
                "that should be components, and opportunities to improve load performance. "
                "Output JSON with: issues (list) and refactoring_suggestions (list)."
            ),
            redis_client=redis_client,
            job_id=job_id,
            rl_engine=rl_engine,
        )

    async def review_tech_debt(self, codebase: dict) -> dict:
        """Review code for technical debt and refactoring opportunities"""
        task = (
            f"Review for technical debt:\n"
            f"Files: {', '.join(codebase.keys())}\n"
            f"Total lines: {sum(len(v.split(chr(10))) for v in codebase.values())}\n\n"
            "Identify: code duplication, redundant styles, inline styles, performance issues, "
            "missing optimization. Output JSON: {\"issues\": [...], \"refactoring_suggestions\": [...]}"
        )

        debt_report = await self.think(task, {"codebase": codebase})

        # Try to parse JSON
        try:
            json_match = re.search(r"\{.*\}", debt_report, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback tech debt report
        return {
            "issues": [
                "Inline styles in HTML should be moved to CSS",
                "Repeated button styles could be a reusable class",
                "CSS has no optimization applied",
            ],
            "refactoring_suggestions": [
                "Create utility classes for common padding/margins",
                "Extract reusable component patterns (cards, buttons)",
                "Minify CSS and JavaScript for production",
                "Use CSS variables for repeated colors and spacing",
                "Consider lazy-loading for images",
                "Compress images before deployment",
            ],
        }
