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

    async def generate_code(
        self, spec: str, design: dict, qa_results: str = "", security_report: str = "", seo_rec: str = ""
    ) -> dict:
        """Generate HTML/CSS/JS code for website"""
        improvements = []
        if qa_results:
            improvements.append(f"QA findings to address: {qa_results}")
        if security_report:
            improvements.append(f"Security fixes needed: {security_report}")
        if seo_rec:
            improvements.append(f"SEO improvements: {seo_rec}")

        task = (
            f"Spec:\n{spec}\n\n"
            f"Design:\n{json.dumps(design, indent=2)}\n\n"
        )
        
        if improvements:
            improvements_text = "Improvements to apply:\n" + "\n".join(improvements) + "\n\n"
            task += improvements_text
        
        task += (
            "Output ONLY valid JSON with filename→content. Must include index.html, style.css, script.js. "
            "Make it modern, responsive, and production-ready."
        )

        code_text = await self.think(task, {"spec": spec, "design": design})

        # Extract JSON from response
        try:
            json_match = re.search(r"\{.*\}", code_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass

        # Fallback minimal website
        return {
            "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoDevOS Generated Site</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <nav class="navbar">
        <h1>Your Company</h1>
        <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#features">Features</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
    <main>
        <section id="home" class="hero">
            <h2>Welcome to Your Company</h2>
            <p>Transform your ideas into reality.</p>
            <button class="cta">Get Started</button>
        </section>
        <section id="features" class="features">
            <h2>Features</h2>
            <div class="feature-grid">
                <div class="feature"><h3>Feature 1</h3><p>Description here</p></div>
                <div class="feature"><h3>Feature 2</h3><p>Description here</p></div>
                <div class="feature"><h3>Feature 3</h3><p>Description here</p></div>
            </div>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 Your Company. All rights reserved.</p>
    </footer>
    <script src="script.js"></script>
</body>
</html>""",
            "style.css": """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
}

.navbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.navbar ul {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.navbar a {
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
}

.navbar a:hover {
    opacity: 0.8;
}

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 6rem 2rem;
    text-align: center;
}

.hero h2 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.cta {
    background: white;
    color: #667eea;
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
    margin-top: 1rem;
    transition: transform 0.3s;
}

.cta:hover {
    transform: scale(1.05);
}

.features {
    padding: 4rem 2rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.feature {
    padding: 2rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    transition: box-shadow 0.3s;
}

.feature:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 2rem;
}

@media (max-width: 768px) {
    .navbar {
        flex-direction: column;
        gap: 1rem;
    }
    
    .navbar ul {
        flex-direction: column;
        gap: 1rem;
    }
    
    .hero h2 {
        font-size: 2rem;
    }
}""",
            "script.js": """document.addEventListener('DOMContentLoaded', function() {
    console.log('Site loaded');
    
    const ctas = document.querySelectorAll('.cta, a[href*="#"]');
    ctas.forEach(cta => {
        cta.addEventListener('click', function(e) {
            if (this.href.includes('#')) {
                e.preventDefault();
                const target = this.getAttribute('href');
                if (target !== '#' && document.querySelector(target)) {
                    document.querySelector(target).scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});""",
        }
