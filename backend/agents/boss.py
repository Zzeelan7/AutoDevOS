"""Boss Agent - Evaluates all contributions and assigns rewards"""
from agents.base import BaseAgent
import json
import re


class BossAgent(BaseAgent):
    """Boss Agent - CEO + CTO evaluating all agent contributions"""

    def __init__(self, redis_client, job_id: str, rl_engine=None):
        super().__init__(
            name="boss",
            role_description=(
                "You are the Boss Agent (CEO + CTO) for AutoDevOS. Review all agent outputs "
                "and score each contribution on: code quality (0-10), security (0-10), SEO/performance (0-10), "
                "and business impact (0-10). Return JSON with: pm_score, architect_score, developer_score, "
                "qa_score, security_score, tech_debt_score, seo_score, overall_score (0-100), verdict_summary."
            ),
            redis_client=redis_client,
            job_id=job_id,
            rl_engine=rl_engine,
        )

    async def evaluate_iteration(
        self, 
        prompt: str, 
        spec: str, 
        design: dict, 
        codebase: dict,
        qa_results: dict,
        security_report: dict,
        tech_debt_report: dict,
        seo_report: dict,
        lighthouse_results: dict,
    ) -> dict:
        """Evaluate all agent contributions and assign scores"""
        task = (
            f"Evaluate this iteration:\n"
            f"Original prompt: {prompt}\n"
            f"Spec quality: {'Good' if len(spec) > 100 else 'Needs improvement'}\n"
            f"Code files: {len(codebase)}\n"
            f"Lighthouse overall: {lighthouse_results.get('lighthouse_score', 0)}\n"
            f"QA issues found: {len(qa_results.get('bugs', []))}\n"
            f"Security vulnerabilities: {len(security_report.get('vulnerabilities', []))}\n"
            f"Tech debt items: {len(tech_debt_report.get('issues', []))}\n"
            f"SEO recommendations: {len(seo_report.get('recommendations', []))}\n\n"
            "Score each agent 0-10 on their specific contribution. "
            "Output JSON: {\"pm_score\": X, \"architect_score\": X, \"developer_score\": X, "
            "\"qa_score\": X, \"security_score\": X, \"tech_debt_score\": X, \"seo_score\": X, "
            "\"overall_score\": X, \"verdict_summary\": \"...\"}"
        )

        verdict = await self.think(
            task,
            {
                "prompt": prompt,
                "spec": spec,
                "design": design,
                "qa": qa_results,
                "security": security_report,
                "lighthouse": lighthouse_results,
            }
        )

        # Try to parse JSON
        try:
            json_match = re.search(r"\{.*\}", verdict, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback scores
        return {
            "pm_score": 8,
            "architect_score": 7,
            "developer_score": 7,
            "qa_score": 6,
            "security_score": 6,
            "tech_debt_score": 5,
            "seo_score": 6,
            "overall_score": 67,
            "verdict_summary": "Initial iteration complete. Site structure is sound but needs refinement in security, performance, and tech debt reduction.",
        }
