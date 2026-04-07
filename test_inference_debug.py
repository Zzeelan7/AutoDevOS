"""
Debug script to test inference and identify scoring issues.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.openenv_env import WebsiteGenerationEnv, Action, TaskType


async def test_grading():
    """Test the grading system with sample HTML/CSS/JS."""
    
    env = WebsiteGenerationEnv(task_type="simple_landing_page")
    await env.reset()
    
    # Test 1: Minimal code (should score low)
    print("=" * 60)
    print("TEST 1: Minimal Code (Expected: ~0.4-0.5)")
    print("=" * 60)
    
    action1 = Action(
        html="<html><h1>Hello</h1></html>",
        css="",
        js=""
    )
    result1 = await env.step(action1)
    reward1 = result1.reward
    
    print(f"Score: {reward1.total_score:.3f}")
    print(f"  - HTML: {reward1.code_quality:.3f}")
    print(f"  - Performance: {reward1.performance:.3f}")
    print(f"  - Accessibility: {reward1.accessibility:.3f}")
    print(f"  - Design: {reward1.design:.3f}")
    print(f"  - Functionality: {reward1.functionality:.3f}")
    print()
    
    # Test 2: Better code (should score higher)
    print("=" * 60)
    print("TEST 2: Good Code (Expected: ~0.7-0.8)")
    print("=" * 60)
    
    env2 = WebsiteGenerationEnv(task_type="simple_landing_page")
    await env2.reset()
    
    action2 = Action(
        html="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Landing Page</title>
</head>
<body>
    <header>
        <nav>
            <a href="#home">Home</a>
            <a href="#about">About</a>
        </nav>
    </header>
    <main>
        <section class="hero">
            <h1>Welcome</h1>
            <p>This is a landing page</p>
            <button class="cta">Get Started</button>
        </section>
        <section class="features">
            <h2>Features</h2>
            <article>Feature 1</article>
            <article>Feature 2</article>
        </section>
    </main>
    <footer>
        <p>&copy; 2024</p>
    </footer>
</body>
</html>""",
        css="""* {
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
    color: #333;
}

header {
    background-color: #207a7a;
    color: white;
    padding: 20px;
}

nav a {
    color: white;
    margin-right: 20px;
    text-decoration: none;
}

.hero {
    text-align: center;
    padding: 100px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.hero h1 {
    font-size: 48px;
    margin-bottom: 20px;
}

.hero button {
    padding: 12px 30px;
    font-size: 16px;
    background-color: white;
    border: none;
    cursor: pointer;
    border-radius: 5px;
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 32px;
    }
    nav a {
        margin-right: 10px;
    }
}

.features {
    padding: 50px 20px;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

footer {
    background-color: #333;
    color: white;
    text-align: center;
    padding: 20px;
}""",
        js="""document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded');
    
    const button = document.querySelector('.cta');
    if (button) {
        button.addEventListener('click', function() {
            alert('Button clicked!');
        });
    }
    
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Clicked:', this.textContent);
        });
    });
});"""
    )
    result2 = await env2.step(action2)
    reward2 = result2.reward
    
    print(f"Score: {reward2.total_score:.3f}")
    print(f"  - HTML: {reward2.code_quality:.3f}")
    print(f"  - Performance: {reward2.performance:.3f}")
    print(f"  - Accessibility: {reward2.accessibility:.3f}")
    print(f"  - Design: {reward2.design:.3f}")
    print(f"  - Functionality: {reward2.functionality:.3f}")
    print()
    
    # Test 3: Premium code (should score 0.85+)
    print("=" * 60)
    print("TEST 3: Premium Code (Expected: 0.85+)")
    print("=" * 60)
    
    env3 = WebsiteGenerationEnv(task_type="portfolio_website")
    await env3.reset()
    
    action3 = Action(
        html="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Professional Portfolio</title>
</head>
<body>
    <header>
        <nav class="navbar">
            <div class="logo">John Doe</div>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#projects">Projects</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="home" class="hero">
            <h1>Full Stack Developer</h1>
            <p>Building amazing web experiences</p>
        </section>
        <section id="projects" class="projects">
            <h2>Featured Projects</h2>
            <article class="project">
                <img src="project1.jpg" alt="Project 1 screenshot">
                <h3>Project One</h3>
                <p>Description of project one</p>
                <a href="#">View Project</a>
            </article>
            <article class="project">
                <img src="project2.jpg" alt="Project 2 screenshot">
                <h3>Project Two</h3>
                <p>Description of project two</p>
                <a href="#">View Project</a>
            </article>
            <article class="project">
                <img src="project3.jpg" alt="Project 3 screenshot">
                <h3>Project Three</h3>
                <p>Description of project three</p>
                <a href="#">View Project</a>
            </article>
        </section>
        <section id="about" class="about">
            <h2>About Me</h2>
            <p>I'm a passionate developer with expertise in modern web technologies.</p>
        </section>
        <section id="contact" class="contact">
            <h2>Get In Touch</h2>
            <form>
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required>
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
                <label for="message">Message:</label>
                <textarea id="message" name="message" required></textarea>
                <button type="submit">Send</button>
            </form>
        </section>
    </main>
    <footer>
        <p>&copy; 2024 John Doe. All rights reserved.</p>
    </footer>
</body>
</html>""",
        css="""* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f4f4f4;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
}

nav ul {
    list-style: none;
    display: flex;
    gap: 2rem;
}

nav a {
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
}

nav a:hover {
    opacity: 0.8;
}

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 100px 2rem;
    text-align: center;
    margin-top: 0;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero p {
    font-size: 1.2rem;
}

.projects {
    max-width: 1200px;
    margin: 3rem auto;
    padding: 0 2rem;
}

.projects h2 {
    text-align: center;
    margin-bottom: 2rem;
    font-size: 2rem;
}

.projects {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.project {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.3s, box-shadow 0.3s;
}

.project:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 12px rgba(0,0,0,0.15);
}

.project img {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.project h3 {
    padding: 1rem;
    font-size: 1.3rem;
}

.project p {
    padding: 0 1rem;
    color: #666;
    font-size: 0.9rem;
}

.project a {
    display: inline-block;
    padding: 0.5rem 1rem;
    margin: 1rem;
    background-color: #667eea;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.project a:hover {
    background-color: #764ba2;
}

.about {
    background: white;
    padding: 3rem 2rem;
    margin: 2rem auto;
    max-width: 1200px;
    text-align: center;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.contact {
    background: white;
    padding: 3rem 2rem;
    margin: 2rem auto 3rem;
    max-width: 1200px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.contact form {
    display: flex;
    flex-direction: column;
    max-width: 600px;
    margin: 0 auto;
}

.contact label {
    margin-top: 1rem;
    font-weight: bold;
}

.contact input,
.contact textarea {
    padding: 0.5rem;
    margin-top: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: inherit;
}

.contact button {
    margin-top: 1rem;
    padding: 0.75rem;
    background-color: #667eea;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.3s;
}

.contact button:hover {
    background-color: #764ba2;
}

footer {
    background-color: #333;
    color: white;
    text-align: center;
    padding: 2rem;
}

@media (max-width: 768px) {
    .hero h1 {
        font-size: 2rem;
    }
    
    nav ul {
        gap: 1rem;
        flex-direction: column;
    }
    
    .navbar {
        flex-direction: column;
        gap: 1rem;
    }
    
    .projects {
        grid-template-columns: 1fr;
    }
}""",
        js="""document.addEventListener('DOMContentLoaded', function() {
    console.log('Portfolio loaded');
    
    // Smooth scrolling for nav links
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const id = this.getAttribute('href');
            const element = document.querySelector(id);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Form handling
    const form = document.querySelector('.contact form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            console.log('Form submitted:', { name, email });
            alert('Thanks for reaching out! I will get back to you soon.');
            form.reset();
        });
    }
    
    // Highlight nav item on scroll
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('main section');
        const navItems = document.querySelectorAll('nav a');
        
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === '#' + current) {
                item.classList.add('active');
            }
        });
    });
});"""
    )
    result3 = await env3.step(action3)
    reward3 = result3.reward
    
    print(f"Score: {reward3.total_score:.3f}")
    print(f"  - HTML: {reward3.code_quality:.3f}")
    print(f"  - Performance: {reward3.performance:.3f}")
    print(f"  - Accessibility: {reward3.accessibility:.3f}")
    print(f"  - Design: {reward3.design:.3f}")
    print(f"  - Functionality: {reward3.functionality:.3f}")
    print()
    
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print(f"Gap from 0.70 to 0.85: {0.85 - 0.70:.2f}")
    print(f"Test 1 gap: {0.85 - (reward1.total_score if reward1 else 0):.3f}")
    print(f"Test 2 gap: {0.85 - (reward2.total_score if reward2 else 0):.3f}")
    print(f"Test 3 gap: {0.90 - (reward3.total_score if reward3 else 0):.3f}")


if __name__ == "__main__":
    asyncio.run(test_grading())
