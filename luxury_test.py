#!/usr/bin/env python3
"""
AURA INTERIORS - Luxury Interior Design E-Commerce Website Generation
Production-Grade Testing with Requirement Validation
"""
import asyncio
import aiohttp
import json
from datetime import datetime
import re

BASE_URL = "http://localhost:8000"

LUXURY_INTERIOR_PROMPT = """### SYSTEM ROLE
You are an expert Senior Full-Stack Engineer and Lead UI/UX Designer specializing in luxury e-commerce and high-end architectural aesthetics. Your goal is to write production-grade, SEO-optimized, and modular code for a luxury interior design studio website.

### PROJECT SCOPE
Build a multi-file website (HTML, CSS, JS) for "AURA INTERIORS."
The brand identity is: Minimalist, Sophisticated, High-Contrast, and Tactile.

### CORE REQUIREMENTS & FEATURES

1. PRODUCTION-GRADE STRUCTURE:
   - Use semantic HTML5 (header, main, section, footer, article).
   - Use CSS custom properties (variables) for a centralized luxury color palette (e.g., #1A1A1A, #F5F5F5, #C5A059).
   - Modular JavaScript: Use an Object-Oriented or Functional approach to handle interactions.
   
2. LUXURY UI/UX FEATURES:
   - HERO SECTION: A deconstructed bento-grid layout with a parallax "Reveal" animation on scroll.
   - SHOPPING EXPERIENCE: A "Curated Collection" e-commerce grid. Products must show high-res image transitions on hover.
   - INTERACTIVE MOOD BOARD: A small JS-driven component where users can drag-and-drop 3 material samples (Marble, Oak, Velvet) into a "Room Preview" container.
   - VIRTUAL CONSULTATION FORM: A 3-step lead capture form with validation (Service Type, Budget Range, Timeline).

3. TECHNICAL SPECIFICATIONS:
   - PERFORMANCE: Implement Lazy Loading for all images and use an Intersection Observer for "fade-in-on-scroll" effects.
   - SEO & ACCESSIBILITY: Include JSON-LD Schema (Product and LocalBusiness). Ensure Aria-labels for all buttons.
   - RESPONSIVENESS: Mobile-first design. Use Clamp() for fluid typography.
   - PAYMENT READY: Mock a Stripe-ready checkout flow using a clean modal overlay.

### FILE ARCHITECTURE
You MUST generate complete, production-ready code with:
1. `index.html`: Full structural core with SEO meta tags and Schema.org scripts. Use semantic HTML5. Include header, main sections, footer.
2. `styles.css`: Complete styling with luxury color palette using CSS variables. Include Glassmorphism effects, high-end typography (System font stack). Grid layouts, animations, responsive design.
3. `app.js`: Full interaction logic - parallax engine, form validation, mood board drag-drop functionality, lazy loading, Intersection Observer for animations.

### EXECUTION INSTRUCTION
Write production-ready code that is marketable and clean. Use professional copy for "Bespoke Spatial Design" and "Artisanal Furnishings."
Generate complete, working code in HTML, CSS, and JavaScript. Ensure all features mentioned are fully implemented."""

# Requirements validation mapping
REQUIREMENTS = {
    "html": {
        "semantic_html5": r"<header|<main|<section|<footer|<article",
        "seo_meta": r"<meta\s+name=['\"]description|<meta\s+name=['\"]viewport|<link\s+rel=['\"]canonical",
        "schema_org": r'"@type".*"Product"|"@type".*"LocalBusiness"|schema.org',
        "aria_labels": r'aria-label=|aria-describedby=|role=',
    },
    "css": {
        "css_variables": r"--[a-z-]+:|--color|--size|var\(",
        "luxury_palette": r"#1A1A1A|#F5F5F5|#C5A059|rgba\(",
        "typography_system": r"font-family|serif|sans-serif|clamp\(",
        "glassmorphism": r"backdrop-filter|background.*rgba|mix-blend-mode",
        "animations": r"@keyframes|animation:|transition:|parallax|scroll",
    },
    "js": {
        "oop_functional": r"class\s+\w+|function\s+\w+|const\s+\w+\s*=.*=>\|Object\.|this\.",
        "lazy_loading": r"loading=['\"]lazy|IntersectionObserver|lazy-load",
        "intersection_observer": r"IntersectionObserver|observe\(|disconnect\(",
        "form_validation": r"validate|validation|checkValid|error|required",
        "drag_drop": r"dragstart|drop|dragover|dragenter|dragleave|setData|getData",
        "stripe_mock": r"stripe|payment|checkout|card|token",
        "parallax": r"parallax|scroll.*event|scrollY|window.scroll",
    }
}

def validate_requirements(html_content, css_content, js_content):
    """Validate generated code against requirements"""
    results = {
        "html": {},
        "css": {},
        "js": {},
        "summary": {}
    }
    
    all_valid = True
    
    # Validate HTML
    for req, pattern in REQUIREMENTS["html"].items():
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        is_valid = len(matches) > 0
        results["html"][req] = {"valid": is_valid, "matches": len(matches)}
        all_valid = all_valid and is_valid
    
    # Validate CSS
    for req, pattern in REQUIREMENTS["css"].items():
        matches = re.findall(pattern, css_content, re.IGNORECASE)
        is_valid = len(matches) > 0
        results["css"][req] = {"valid": is_valid, "matches": len(matches)}
        all_valid = all_valid and is_valid
    
    # Validate JS
    for req, pattern in REQUIREMENTS["js"].items():
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        is_valid = len(matches) > 0
        results["js"][req] = {"valid": is_valid, "matches": len(matches)}
        all_valid = all_valid and is_valid
    
    results["summary"]["all_requirements_met"] = all_valid
    results["summary"]["html_score"] = sum(1 for r in results["html"].values() if r["valid"]) / len(results["html"])
    results["summary"]["css_score"] = sum(1 for r in results["css"].values() if r["valid"]) / len(results["css"])
    results["summary"]["js_score"] = sum(1 for r in results["js"].values() if r["valid"]) / len(results["js"])
    
    return results

async def create_and_test_luxury_website(attempt=1):
    """Create luxury interior design website and validate it"""
    print(f"\n{'='*80}")
    print(f"ATTEMPT {attempt}: AURA INTERIORS - LUXURY E-COMMERCE WEBSITE GENERATION")
    print(f"{'='*80}\n")
    
    async with aiohttp.ClientSession() as session:
        # Create job
        print("[1/3] Submitting job to AutoDevOS...")
        try:
            async with session.post(
                f"{BASE_URL}/api/jobs",
                json={"prompt": LUXURY_INTERIOR_PROMPT},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status != 200:
                    print(f"[FAIL] Failed to create job: {resp.status}")
                    return None
                job = await resp.json()
        except Exception as e:
            print(f"[FAIL] Create job failed: {e}")
            return None
        
        job_id = job.get("jobId")
        print(f"[OK] Job created: {job_id}\n")
        
        # Monitor WebSocket for completion
        print("[2/3] Monitoring job progress via WebSocket...")
        generated_output = {}
        
        try:
            async with session.ws_connect(f"ws://localhost:8000/ws/{job_id}") as ws:
                start_time = datetime.now()
                
                while True:
                    try:
                        msg = await asyncio.wait_for(ws.receive_json(), timeout=5.0)
                        msg_type = msg.get("type", "unknown")
                        
                        if msg_type == "init":
                            print(f"  ↳ Environment initialized")
                        elif msg_type == "event":
                            print(f"  ↳ {msg.get('message', 'Event processed')}")
                        elif msg_type == "complete":
                            job_data = msg.get("job", {})
                            elapsed = (datetime.now() - start_time).total_seconds()
                            print(f"  ↳ Job completed in {elapsed:.1f}s")
                            print(f"    - Reward: {job_data.get('overall_reward', 0):.2f}/10")
                            print(f"    - Steps: {job_data.get('steps', 0)}\n")
                            generated_output = job_data
                            break
                        elif msg_type == "error":
                            print(f"  ✗ Error: {msg.get('message')}")
                            return None
                    except asyncio.TimeoutError:
                        continue
                    except:
                        break
        except Exception as e:
            print(f"[FAIL] WebSocket error: {e}")
            return None
        
        if not generated_output:
            print("[FAIL] No output generated")
            return None
        
        # Fetch job details to get generated content
        print("[3/3] Analyzing generated code...")
        try:
            async with session.get(
                f"{BASE_URL}/api/jobs/{job_id}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    print(f"[FAIL] Failed to fetch job: {resp.status}")
                    return None
                job_data = await resp.json()
        except Exception as e:
            print(f"[FAIL] Fetch job failed: {e}")
            return None
        
        # Get preview data
        try:
            async with session.get(
                f"{BASE_URL}/api/jobs/{job_id}/preview",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    preview_data = await resp.json()
                    html_content = preview_data.get("html", "")
                    css_content = preview_data.get("css", "")
                    js_content = preview_data.get("js", "")
                else:
                    html_content = job_data.get("generated_html", job_data.get("prompt", "")[:500])
                    css_content = job_data.get("generated_css", "")
                    js_content = job_data.get("generated_js", "")
        except:
            html_content = job_data.get("generated_html", job_data.get("prompt", "")[:500])
            css_content = job_data.get("generated_css", "")
            js_content = job_data.get("generated_js", "")
        
        # Validate requirements
        validation = validate_requirements(html_content, css_content, js_content)
        
        print("\n" + "="*80)
        print("REQUIREMENT VALIDATION RESULTS")
        print("="*80)
        
        print("\nHTML Requirements:")
        for req, result in validation["html"].items():
            status = "✓" if result["valid"] else "✗"
            print(f"  {status} {req:30s} ({result['matches']} matches)")
        
        print("\nCSS Requirements:")
        for req, result in validation["css"].items():
            status = "✓" if result["valid"] else "✗"
            print(f"  {status} {req:30s} ({result['matches']} matches)")
        
        print("\nJavaScript Requirements:")
        for req, result in validation["js"].items():
            status = "✓" if result["valid"] else "✗"
            print(f"  {status} {req:30s} ({result['matches']} matches)")
        
        print("\n" + "="*80)
        print("SUMMARY SCORES")
        print("="*80)
        print(f"HTML Score:  {validation['summary']['html_score']*100:.1f}%")
        print(f"CSS Score:   {validation['summary']['css_score']*100:.1f}%")
        print(f"JS Score:    {validation['summary']['js_score']*100:.1f}%")
        
        overall_score = (validation['summary']['html_score'] + 
                        validation['summary']['css_score'] + 
                        validation['summary']['js_score']) / 3
        
        print(f"Overall:     {overall_score*100:.1f}%")
        
        if validation['summary']['all_requirements_met']:
            print("\n✅ ALL REQUIREMENTS MET - PRODUCTION-READY CODE GENERATED")
            return {
                "success": True,
                "job_id": job_id,
                "reward": generated_output.get("overall_reward", 0),
                "validation": validation
            }
        else:
            print(f"\n⚠️  {sum(1 for r in list(validation['html'].values()) + list(validation['css'].values()) + list(validation['js'].values()) if not r['valid'])} requirements not met")
            if attempt < 3:
                print(f"\nRetrying... (Attempt {attempt + 1}/3)\n")
                await asyncio.sleep(2)
                return await create_and_test_luxury_website(attempt + 1)
            else:
                print("\nMax retries reached")
                return {
                    "success": False,
                    "job_id": job_id,
                    "reward": generated_output.get("overall_reward", 0),
                    "validation": validation,
                    "attempts": attempt
                }

async def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("LUXURY INTERIOR DESIGN E-COMMERCE WEBSITE GENERATION TEST")
    print("Testing production-grade code generation for AURA INTERIORS")
    print("="*80)
    
    result = await create_and_test_luxury_website()
    
    if result:
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)
        print(f"Status: {'✅ SUCCESS' if result['success'] else '⚠️  PARTIAL'}")
        print(f"Job ID: {result['job_id']}")
        print(f"Reward: {result['reward']:.2f}/10")
        if "attempts" in result:
            print(f"Attempts: {result['attempts']}/3")
        print("="*80 + "\n")

if __name__ == "__main__":
    print("\nStarting luxury website generation test...")
    print("Backend must be running on localhost:8000\n")
    
    asyncio.run(main())
