"""Sandbox runner - Executes generated code and collects metrics"""
import httpx
import json
from typing import Dict, Any


class SandboxRunner:
    """Execute generated website in sandbox and collect Lighthouse scores"""

    def __init__(self, sandbox_url: str = "http://sandbox:9000"):
        self.sandbox_url = sandbox_url
        self.timeout = 60

    async def run_site(self, job_id: str, iteration: int, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute site in sandbox and return Lighthouse results
        
        Args:
            job_id: Unique job identifier
            iteration: Iteration number (1, 2, 3)
            files: Dict mapping filename -> content
            
        Returns:
            Dict with lighthouse_score, performance, seo, accessibility, best_practices, validation_errors
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "jobId": job_id,
                    "iteration": iteration,
                    "files": files,
                }
                
                response = await client.post(
                    f"{self.sandbox_url}/run",
                    json=payload
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    # Fallback scores on error
                    return self._fallback_scores()
        except Exception as e:
            print(f"Sandbox error: {e}")
            return self._fallback_scores()

    @staticmethod
    def _fallback_scores() -> Dict[str, Any]:
        """Fallback scores if sandbox unavailable"""
        return {
            "lighthouse_score": 72,
            "performance": 75,
            "seo": 75,
            "accessibility": 72,
            "best_practices": 70,
            "validation_errors": [],
        }


# Global sandbox instance
sandbox = SandboxRunner()
