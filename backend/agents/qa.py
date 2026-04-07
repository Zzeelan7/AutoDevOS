"""QA Agent - Tests and reviews generated code"""
from agents.base import BaseAgent
import json
import re


class QAAgent(BaseAgent):
    """QA Engineer - Reviews code and test results"""

    def __init__(self, redis_client, job_id: str, rl_engine=None):
        super().__init__(
            name="qa",
            role_description=(
                "You are the QA Engineer at AutoDevOS. Review the generated code and Lighthouse "
                "results. Identify: broken links, missing alt text, accessibility issues, layout "
                "bugs, and any JavaScript errors. Output a JSON with keys: bugs (list), "
                "severity (critical/major/minor each), and suggested_fixes (list)."
            ),
            redis_client=redis_client,
            job_id=job_id,
            rl_engine=rl_engine,
        )

    async def review_code(self, codebase: dict, lighthouse_results: dict) -> dict:
        """Review generated code and test results"""
        task = (
            f"Code files:\n{json.dumps({k: len(v) for k, v in codebase.items()}, indent=2)}\n\n"
            f"Lighthouse results:\n{json.dumps(lighthouse_results, indent=2)}\n\n"
            "Identify bugs, accessibility issues, and improvements. "
            "Output JSON: {\"bugs\": [...], \"severity\": {\"critical\": [...], \"major\": [...], \"minor\": [...]}, \"suggested_fixes\": [...]}"
        )

        review = await self.think(task, {"codebase": codebase, "lighthouse": lighthouse_results})

        # Try to parse JSON
        try:
            json_match = re.search(r"\{.*\}", review, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback review
        return {
            "bugs": ["Consider adding meta descriptions", "Add microdata for SEO"],
            "severity": {
                "critical": [],
                "major": ["Missing aria-labels on interactive elements"],
                "minor": ["Consider image optimization", "Add loading indicators"],
            },
            "suggested_fixes": [
                "Add alt text to all images",
                "Improve keyboard navigation",
                "Use semantic HTML5 tags",
                "Optimize performance for slower connections",
            ],
        }
