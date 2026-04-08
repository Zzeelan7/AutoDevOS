"""Developer Agent - Generates HTML, CSS, and JavaScript code"""
from agents.base import BaseAgent
import json
import re


class DeveloperAgent(BaseAgent):
    """Senior Frontend Developer - Generates actual website code"""

    def __init__(self, redis_client, job_id: str, rl_engine=None):
        super().__init__(
            name="developer",
            role_description=(
                "You are a Senior Frontend Developer at AutoDevOS. Your job is to write or "
                "improve the actual HTML, CSS, and JS code for the company website based on the "
                "spec and architect's design. Output ONLY a JSON object mapping filename to full "
                "file content. Make the site visually polished, responsive, and professional."
            ),
            redis_client=redis_client,
            job_id=job_id,
            rl_engine=rl_engine,
        )

    def _extract_profile(self, spec: str) -> dict:
        """Extract key content hints from spec to avoid generic fallback output."""
        profile = {
            "name": "Generated Website",
            "headline": "Build something your users actually want",
            "subheadline": "A tailored experience based on your prompt.",
            "cta": "Get Started",
            "features": [
                "Clear value proposition",
                "Responsive design",
                "Conversion-focused sections",
            ],
        }

        lines = [line.strip() for line in spec.splitlines() if line.strip()]
        for line in lines:
            lower = line.lower()
            if lower.startswith("project name") and ":" in line:
                profile["name"] = line.split(":", 1)[1].strip() or profile["name"]
            elif lower.startswith("business category") and ":" in line:
                category = line.split(":", 1)[1].strip()
                if category:
                    profile["name"] = f"{category.title()} Hub"
            elif "headline" in lower and ":" in line:
                profile["headline"] = line.split(":", 1)[1].strip() or profile["headline"]
            elif ("subheading" in lower or "description" in lower) and ":" in line:
                profile["subheadline"] = line.split(":", 1)[1].strip() or profile["subheadline"]
            elif ("cta" in lower or "button" in lower) and ":" in line:
                value = line.split(":", 1)[1].strip()
                if value:
                    profile["cta"] = value[:28]

        bullet_candidates = []
        for line in lines:
            if line.startswith("-") or line.startswith("*"):
                text = line.lstrip("-* ").strip()
                if text and len(text) > 5:
                    bullet_candidates.append(text)

        if bullet_candidates:
            profile["features"] = bullet_candidates[:3]

        return profile

    def _build_contextual_fallback(self, spec: str) -> dict:
        """Build a non-generic fallback website using inferred spec context."""
        p = self._extract_profile(spec)
        while len(p["features"]) < 3:
            p["features"].append("Tailored experience")
        return {
            "index.html": f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <meta name=\"autodevos-generation-mode\" content=\"degraded-fallback\">
    <meta name=\"description\" content=\"{p['name']} - custom generated website\">
    <title>{p['name']}</title>
    <link rel=\"stylesheet\" href=\"style.css\">
</head>
<body>
    <header class=\"topbar\">
        <h1>{p['name']}</h1>
        <nav>
            <a href=\"#home\">Home</a>
            <a href=\"#features\">Features</a>
            <a href=\"#contact\">Contact</a>
        </nav>
    </header>
    <main>
        <section id=\"home\" class=\"hero\">
            <h2>{p['headline']}</h2>
            <p>{p['subheadline']}</p>
            <button class=\"cta\">{p['cta']}</button>
        </section>
        <section id=\"features\" class=\"features\">
            <article><h3>{p['features'][0]}</h3></article>
            <article><h3>{p['features'][1]}</h3></article>
            <article><h3>{p['features'][2]}</h3></article>
        </section>
        <section id=\"contact\" class=\"contact\">
            <h2>Ready to move forward?</h2>
            <button class=\"cta\">{p['cta']}</button>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 {p['name']}. All rights reserved.</p>
    </footer>
    <script src=\"script.js\"></script>
</body>
</html>""",
            "style.css": """* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Segoe UI, Arial, sans-serif; color: #202124; background: #f8fafc; }
.topbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; background: #0f172a; color: #fff; }
.topbar nav { display: flex; gap: 1rem; }
.topbar a { color: #fff; text-decoration: none; }
.hero { padding: 4rem 1.5rem; text-align: center; background: linear-gradient(120deg, #0ea5e9, #2563eb); color: #fff; }
.hero p { margin: 1rem auto; max-width: 700px; }
.cta { border: 0; border-radius: 8px; background: #fff; color: #1d4ed8; padding: 0.8rem 1.4rem; font-weight: 700; cursor: pointer; }
.features { padding: 2rem 1.5rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }
.features article { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; }
.contact { padding: 2rem 1.5rem; text-align: center; }
footer { padding: 1.5rem; text-align: center; color: #475569; }
@media (max-width: 720px) { .topbar { flex-direction: column; gap: 0.75rem; } }""",
            "script.js": """document.querySelectorAll('a[href^="#"]').forEach((el) => {
  el.addEventListener('click', (e) => {
    e.preventDefault();
    const target = document.querySelector(el.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  });
});""",
        }

    async def generate_code(
        self, spec: str, design: dict, qa_results: str = "", security_report: str = "", seo_rec: str = ""
    ) -> dict:
        """Generate HTML/CSS/JS code for website with precision prompt"""
        improvements = []
        if qa_results:
            improvements.append(f"QA findings to address: {qa_results}")
        if security_report:
            improvements.append(f"Security fixes needed: {security_report}")
        if seo_rec:
            improvements.append(f"SEO improvements: {seo_rec}")

        # Build the ULTRA-PRECISE prompt
        task = f"""CRITICAL TASK: Generate production-ready website code based on these specifications.

__________ SPECIFICATION __________
{spec}

__________ DESIGN __________
{json.dumps(design, indent=2)}
"""
        
        if improvements:
            task += "\n__________ IMPROVEMENTS __________\n" + "\n".join(improvements)
        
        task += """

__________ YOUR INSTRUCTIONS (FOLLOW EXACTLY) __________

You are a Senior Frontend Developer with 10+ years of experience.

MOST IMPORTANT: 
- Every output character must be inside valid JSON object
- JSON structure: {{"index.html": "...full html...", "style.css": "...full css...", "script.js": "...full js..."}}
- NO explanations outside JSON - ONLY JSON

STEP 1: READ THE SPECIFICATION CAREFULLY
Extract ALL information:
- What is this business/website about?
- What are the specific pages needed?
- What content/text should appear (not generic)
- What buttons/CTAs are needed (specific labels)?
- What color/style is mentioned?

STEP 2: BUILD HTML FILE
✓ Start with <!DOCTYPE html>
✓ Include <meta charset="UTF-8"> and viewport
✓ Create semantic structure: header, nav, main, sections, footer
✓ Use specific text/content from specification (NOT "Your Company")
✓ Add actual button labels from spec
✓ Include proper IDs and classes
✓ Ensure all <img>, <a>, <button> tags properly closed
✓ Add proper form tags if mentioned in spec

STEP 3: BUILD CSS FILE  
✓ Start with reset: * { margin: 0; padding: 0; box-sizing: border-box; }
✓ Mobile-first: create mobile styles first, then media queries
✓ Include hover effects, transitions, animations
✓ Professional spacing and typography
✓ Colors mentioned in design
✓ Responsive grid layouts with flexbox/grid
✓ Smooth user experience

STEP 4: BUILD JAVASCRIPT FILE
✓ Smooth scroll for anchor links
✓ Form validation if forms exist
✓ Event handlers with error handling
✓ NO syntax errors - code must work
✓ Vanilla JS only - no frameworks

STEP 5: OUTPUT IMMEDIATELY
Format: {{"index.html": "<!DOCTYPE html>...", "style.css": "body {{ ... }}", "script.js": "// code..."}}
Start with { character immediately.
NO markdown, NO explanations, NO code fences.
Only valid JSON.

Generate the website now:"""

        code_text = await self.think(task, {"spec": spec, "design": design})

        # Extract JSON from response with multiple recovery strategies
        candidates = [code_text]
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", code_text, re.DOTALL)
        if fenced:
            candidates.append(fenced.group(1))

        start_idx = code_text.find("{")
        end_idx = code_text.rfind("}")
        if start_idx != -1 and end_idx > start_idx:
            candidates.append(code_text[start_idx:end_idx + 1])

        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict) and all(k in parsed for k in ["index.html", "style.css", "script.js"]):
                    # Ignore provider-level placeholder payloads and use spec-aware fallback instead.
                    if "model provider was unavailable" in parsed.get("index.html", "").lower():
                        continue
                    return parsed
            except (json.JSONDecodeError, TypeError):
                continue

        # LLM output was unusable (often due to provider failure). Return contextual fallback.
        return self._build_contextual_fallback(spec)
