"""Product Manager Agent - Generates product specifications"""
from agents.base import BaseAgent
import json


class PMAgent(BaseAgent):
    """Product Manager Agent - Creates detailed product spec from business idea"""

    def __init__(self, redis_client, job_id: str, rl_engine=None):
        super().__init__(
            name="pm",
            role_description=(
                "You are the Product Manager at AutoDevOS. Given a business idea, produce a "
                "concise product spec including: target users, core value proposition, key pages "
                "needed (homepage, about, features, CTA), and content requirements. Be specific "
                "and actionable. Max 300 words."
            ),
            redis_client=redis_client,
            job_id=job_id,
            rl_engine=rl_engine,
        )

    async def generate_spec(self, prompt: str) -> str:
        """Generate product specification from business prompt"""
        task = f"Business idea: {prompt}\n\nCreate a concise product spec."
        spec = await self.think(task, {"prompt": prompt})
        return spec
