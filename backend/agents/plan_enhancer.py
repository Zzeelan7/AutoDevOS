"""Plan Enhancer Agent - Improves user prompts into comprehensive briefs"""
from agents.base import BaseAgent
import json


class PlanEnhancerAgent(BaseAgent):
    """Takes raw user prompt and creates a comprehensive project plan"""

    def __init__(self, redis_client, job_id: str, rl_engine=None):
        super().__init__(
            name="plan_enhancer",
            role_description=(
                "You are a Senior Product Strategist at AutoDevOS. Your role is to take a vague user prompt "
                "and create a COMPREHENSIVE, detailed project plan that will guide the entire development team. "
                "Transform the user's idea into a clear strategic brief with specific pages, features, target audience, "
                "design approach, content requirements, and technical considerations. Be thorough and specific."
            ),
            redis_client=redis_client,
            job_id=job_id,
            rl_engine=rl_engine,
        )

    async def enhance_prompt(self, user_prompt: str) -> str:
        """Transform vague prompt into comprehensive plan"""
        task = f"""User Request: "{user_prompt}"

Create a DETAILED PROJECT BRIEF that includes:

1. PROJECT VISION
   - What is this website about?
   - Who is the target audience?
   - What problems does it solve?

2. KEY PAGES & SECTIONS
   - List all pages needed (home, about, services, pricing, contact, etc)
   - Describe content for each page

3. FEATURES & FUNCTIONALITY
   - Interactive elements
   - Forms, buttons, navigation patterns
   - User interactions needed

4. DESIGN & BRANDING
   - Style: modern, minimal, colorful, professional, playful, etc
   - Color palette suggestions
   - Typography style
   - Mood/tone

5. TECHNICAL REQUIREMENTS
   - Performance needs
   - Accessibility requirements
   - Device support (mobile, tablet, desktop)

6. CONTENT STRATEGY
   - Key messages
   - CTAs (calls to action)
   - Social proof elements (testimonials, stats, trust badges)

7. SUCCESS METRICS
   - What makes this website successful?

Output a detailed markdown-formatted plan that a whole team can follow."""

        plan = await self.think(task, {"user_prompt": user_prompt})
        return plan
