"""Architect Agent - Designs file structure and technical decisions"""
from agents.base import BaseAgent
import json


class ArchitectAgent(BaseAgent):
    """Software Architect - Designs file structure and technical decisions"""

    def __init__(self, redis_client, job_id: str, rl_engine=None):
        super().__init__(
            name="architect",
            role_description=(
                "You are the Software Architect at AutoDevOS. Given a product spec, design the "
                "file structure for a static company website (HTML/CSS/JS). Output a JSON object "
                "mapping filename to a brief description of what each file contains. Include: "
                "index.html, style.css, and any JS needed. Keep it deployable as static files."
            ),
            redis_client=redis_client,
            job_id=job_id,
            rl_engine=rl_engine,
        )

    async def design_architecture(self, spec: str) -> dict:
        """Design file structure for website"""
        task = (
            f"Product spec:\n{spec}\n\n"
            "Output ONLY a JSON object mapping filename to description. "
            "Example format: {\"index.html\": \"Homepage...\", \"style.css\": \"Styling...\"}"
        )
        design_text = await self.think(task, {"spec": spec})

        # Try to parse JSON, with fallback
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r"\{.*\}", design_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback design
        return {
            "index.html": "Main homepage with hero section and features overview",
            "style.css": "Global styles, responsive design, colors, typography",
            "script.js": "Interactivity, form handling, smooth scrolling",
        }
