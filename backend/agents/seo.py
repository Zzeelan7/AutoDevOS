"""SEO Agent - Analyzes Lighthouse scores and SEO recommendations"""
from agents.base import BaseAgent
import json
import re


class SEOAgent(BaseAgent):
    """SEO and Data Intelligence Specialist"""

    def __init__(self, redis_client, job_id: str, rl_engine=None):
        super().__init__(
            name="seo",
            role_description=(
                "You are the SEO and Data Intelligence specialist at AutoDevOS. Given Lighthouse "
                "scores and the generated site, suggest improvements for: meta tags, Open Graph "
                "tags, page title, heading hierarchy, image optimization, structured data, and "
                "page load speed. Output JSON with: current_lighthouse_score (number), "
                "recommendations (list, prioritized by impact)."
            ),
            redis_client=redis_client,
            job_id=job_id,
            rl_engine=rl_engine,
        )

    async def analyze_seo(self, codebase: dict, lighthouse_results: dict) -> dict:
        """Analyze SEO and Lighthouse metrics"""
        task = (
            f"SEO Analysis:\n"
            f"Lighthouse score: {lighthouse_results.get('lighthouse_score', 75)}\n"
            f"Performance: {lighthouse_results.get('performance', 75)}\n"
            f"SEO: {lighthouse_results.get('seo', 75)}\n"
            f"Accessibility: {lighthouse_results.get('accessibility', 75)}\n\n"
            "Provide SEO recommendations for meta tags, Open Graph, structured data, "
            "performance. Output JSON: {\"current_lighthouse_score\": X, \"recommendations\": [...]}"
        )

        seo_report = await self.think(task, {"codebase": codebase, "lighthouse": lighthouse_results})

        # Try to parse JSON
        try:
            json_match = re.search(r"\{.*\}", seo_report, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback SEO report
        return {
            "current_lighthouse_score": lighthouse_results.get("lighthouse_score", 75),
            "recommendations": [
                "Add comprehensive meta tags: description, keywords, og:title, og:description, og:image",
                "Implement structured data (schema.org) for organization",
                "Optimize images: use WebP format with PNG fallback",
                "Implement mobile-first responsive design",
                "Add breadcrumb navigation for better UX",
                "Create XML sitemap and robots.txt",
                "Add canonical tags to prevent duplicate content",
                "Lazy-load defer off-screen images",
                "Minify resources to improve Core Web Vitals",
                "Add social media meta tags for better sharing",
            ],
        }
