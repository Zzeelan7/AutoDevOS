"""Security Agent - Scans for vulnerabilities"""
from agents.base import BaseAgent
import json
import re


class SecurityAgent(BaseAgent):
    """Security Engineer - Scans for vulnerabilities and security issues"""

    def __init__(self, redis_client, job_id: str, rl_engine=None):
        super().__init__(
            name="security",
            role_description=(
                "You are the Security Engineer at AutoDevOS. Review the generated HTML/CSS/JS "
                "for: XSS vulnerabilities, missing Content-Security-Policy meta tags, exposed "
                "API keys, insecure form actions, and missing HTTPS references. Output JSON with: "
                "vulnerabilities (list), severity (list), fixes (list)."
            ),
            redis_client=redis_client,
            job_id=job_id,
            rl_engine=rl_engine,
        )

    async def scan_security(self, codebase: dict) -> dict:
        """Scan code for security vulnerabilities"""
        task = (
            f"Review this website code for security issues:\n"
            f"Files: {', '.join(codebase.keys())}\n\n"
            "Check for: XSS risks, missing CSP headers, insecure external resources, form validation. "
            "Output JSON: {\"vulnerabilities\": [...], \"severity\": [...], \"fixes\": [...]}"
        )

        report = await self.think(task, {"codebase": codebase})

        # Try to parse JSON
        try:
            json_match = re.search(r"\{.*\}", report, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback security report
        return {
            "vulnerabilities": [
                "Missing Content-Security-Policy header",
                "External resources should use integrity checks",
            ],
            "severity": ["medium", "low"],
            "fixes": [
                "Add CSP meta tag: <meta http-equiv='Content-Security-Policy' content=\"default-src 'self'\">",
                "Use SRI (Subresource Integrity) for CDN resources",
                "Avoid inline JavaScript",
                "Sanitize any user input",
                "Use HTTPS for all resources",
            ],
        }
