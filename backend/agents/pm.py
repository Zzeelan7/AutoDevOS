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
        """Generate ultra-detailed, developer-focused product specification"""
        
        task = f"""USER REQUEST: "{prompt}"

ROLE: You are a Senior Product Manager creating a specification that a developer will use to build a CUSTOMIZED website.

GOAL: Transform the vague request into a DETAILED, ACTIONABLE specification. Every detail matters.

========== SPECIFICATION FRAMEWORK ==========

Analyze the request and produce EXACTLY this structure:

1. PROJECT IDENTITY
   Project Name: [What should this business/project be called?]
   Business Category: [SaaS, Portfolio, E-commerce, Service, Agency, etc]
   Primary Goal: [What do you want users to DO? Sign up? Buy? Contact? Learn?]
   Target Audience: [Who are these users? What are they looking for?]
   Unique Value: [What makes this different/better?]

2. HOMEPAGE STRUCTURE (must include):
   A. Hero Section
      - Headline: [specific, compelling, NOT "Welcome to X" - tie to business goal]
      - Subheading/Description: [clarify what this is/does]
      - Primary CTA Button: [exact button text - be specific: "Start Free Trial" or "See Our Work" or "Learn More"]
   
   B. Features/Benefits Section
      - Feature 1: [title + 1-2 line description]
      - Feature 2: [title + 1-2 line description]
      - Feature 3: [title + 1-2 line description]
   
   C. Social Proof (if applicable)
      - Testimonial or stat to build trust
   
   D. Secondary CTA
      - Bottom CTA button: [exact text]

3. ADDITIONAL PAGES NEEDED
   List each page and what content goes there:
   - [Page name]: [Purpose + main content sections]
   - etc.

4. NAVIGATION MAP
   Top nav items: [list exact page names that should appear in navigation]
   Footer: [company info, links, contact method]

5. DESIGN DIRECTION
   Color Palette: Primary=[color], Accent=[color], Background=[color]
   Overall Style: [professional/modern/playful/minimal/bold/creative]
   Typography Feel: [clean moderntech? elegant? friendly startup? bold?]
   Visual Elements: [animations y/n, icons y/n, gradients y/n]

6. CONTENT TONE
   - How should text feel? [formal, friendly, conversational, confident, etc]
   - Key messaging themes: [list 2-3 main themes to emphasize]

7. INTERACTION DETAILS
   - Forms needed: [signup, contact, inquiry - describe briefly]
   - Navigation style: [top horizontal menu / hamburger mobile / sticky]
   - Animations/Effects: [smooth scrolling, fade-ins, hover effects - be specific]

========== CRITICAL INSTRUCTIONS ==========

- BE SPECIFIC: Don't say "features" - list actual features for THIS business
- BE ACTIONABLE: Write specs a developer can code from immediately
- REFLECT THE REQUEST: If user says "portfolio for photographers" - tailor EVERYTHING to photographers
- USE ACTUAL TEXT: Provide actual button labels, headlines, not placeholders
- PRIORITIZE PURPOSE: Focus on what the business actually does/wants

Generate the specification now. Be thorough and specific:"""

        spec = await self.think(task, {"user_prompt": prompt})
        return spec
