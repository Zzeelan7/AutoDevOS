#!/usr/bin/env python3
"""
Production-Grade Website Generation Testing
Tests AutoDevOS with realistic prompts and production-level requirements
"""
import asyncio
import aiohttp
import json
from datetime import datetime
import uuid

BASE_URL = "http://localhost:8000"

# Production-grade website prompts
PROMPTS = [
    {
        "name": "SaaS Landing Page",
        "prompt": """Create a modern SaaS landing page for an AI-powered analytics platform called "DataFlow".
        
Requirements:
- Hero section with gradient background and CTA buttons
- Feature grid (6 features) with icons and descriptions
- Pricing table with 3 tiers (Starter, Professional, Enterprise)
- Social proof section with customer testimonials
- Live chat widget integration code
- Email subscription footer
- Navigation with smooth scrolling
- Responsive design for mobile/tablet/desktop
- Dark mode with accent colors (cyan/purple)
- Performance optimized (lazy loading images)
Additional: Include JavaScript for smooth animations, form validation, and tab switching for pricing"""
    },
    {
        "name": "E-Commerce Product Showcase",
        "prompt": """Create a premium e-commerce product showcase site for luxury sneakers brand "AirElite".

Requirements:
- Product grid with 12 items (with hover zoom effects)
- Product detail modal with image gallery (main + 4 thumbnails)
- Shopping cart functionality (add to cart, update quantities, remove)
- Product filters (price range, brand, size, color)
- Sort options (newest, popular, price low-high)
- User reviews section with star ratings
- Wishlist heart icons with toggle functionality
- Mini cart display in header showing item count
- Checkout flow (cart review, shipping, payment)
- Customer testimonials carousel
Additional: Include working JavaScript for cart logic, real-time product updates, and smooth transitions"""
    },
    {
        "name": "Creative Agency Portfolio",
        "prompt": """Create an interactive creative agency portfolio website for "Nexus Creative Studio".

Requirements:
- Header with animated logo and navigation menu
- Full-screen hero banner with parallax scrolling
- Portfolio grid with 12 projects showing:
  * Project image with hover overlay
  * Category tags (web, branding, video)
  * Project title and description
  * "View Case Study" button
- Case study modal popup showing:
  * Large project images
  * Project brief and objectives
  * Results metrics
  * Technologies used
- Team member profiles section with:
  * Member photos
  * Name, role, bio
  * Social links
  * Hover effects
- Process/methodology timeline section
- Contact form with validation
- Footer with newsletter signup
Additional: Include animations on scroll, image galleries with lightbox, smooth page transitions"""
    },
    {
        "name": "SaaS Documentation Hub",
        "prompt": """Create a comprehensive documentation hub for "CloudAPI" platform.

Requirements:
- Sticky sidebar navigation with collapsed/expanded states
- Search functionality (with live results as you type)
- Main content area with:
  * Table of contents for each doc
  * Code syntax highlighting
  * Copy code button on snippets
- API reference section with:
  * Endpoint definitions
  * Request/response examples
  * Parameter types and descriptions
- Interactive code examples with:
  * Multiple language tabs (Python, JavaScript, cURL)
  * Live output area
- Getting started guide with step-by-step instructions
- FAQ accordion section
- Breadcrumb navigation
- Dark theme with syntax highlighting
- Mobile-responsive documentation view
Additional: Include working tab switching, smooth search filtering, copy-to-clipboard functionality, code execution simulation"""
    },
    {
        "name": "Real Estate Platform",
        "prompt": """Create a real estate listing and search platform called "PropertyHub".

Requirements:
- Advanced property search with filters:
  * Location (with map integration)
  * Price range slider
  * Property type (apartment, house, commercial)
  * Beds, baths, area size
  * Amenities checkboxes
- Property listing cards showing:
  * High-quality image carousel
  * Price, location, key details
  * Favorite/heart toggle
  * Rating/reviews
- Property detail page with:
  * Full image gallery
  * Virtual tour button
  * Property description
  * Floor plan image
  * Agent contact information
  * Similar listings recommendations
- Map view integration (showing markers)
- Saved properties/favorites list
- Agent profile pages
- Contact form
- Mobile app-like responsive design
Additional: Include working filters, smooth image transitions, favorites persistence, form validation"""
    },
    {
        "name": "AI Chat Application UI",
        "prompt": """Create a modern AI chat application interface called "MindChat".

Requirements:
- Chat conversation list sidebar with:
  * Search conversations
  * New chat button
  * Conversation history with timestamps
  * Delete/archive options
  * Active conversation highlight
- Main chat area with:
  * Conversation header with AI name and status indicator
  * Message history (user vs AI messages with different styles)
  * Timestamps and read receipts
  * Typing indicator animation
- Message input area with:
  * Text input field
  * Send button
  * File upload button
  * Emoji picker
  * Voice input button (visual)
- Settings panel with:
  * Theme switcher (light/dark)
  * Font size adjustment
  * Display options
- Conversation context panel showing:
  * Current model
  * Temperature/parameters
  * Token usage
- Responsive mobile layout with collapsible sidebar
Additional: Include working message sending, smooth animations, typing indicators, emoji support, responsive tab handling"""
    }
]

async def create_job(session, prompt_data):
    """Create a new job"""
    try:
        async with session.post(
            f"{BASE_URL}/api/jobs",
            json={"prompt": prompt_data["prompt"]},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status == 200:
                job = await resp.json()
                return job
            else:
                print(f"[FAIL] Failed to create job: {resp.status}")
                return None
    except Exception as e:
        print(f"[ERROR] Create job failed: {e}")
        return None

async def monitor_websocket(job_id):
    """Monitor job progress via WebSocket"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(f"ws://localhost:8000/ws/{job_id}") as ws:
                events = []
                start_time = datetime.now()
                
                while True:
                    try:
                        msg = await asyncio.wait_for(ws.receive_json(), timeout=2.0)
                        msg_type = msg.get("type", "unknown")
                        
                        if msg_type == "init":
                            print(f"  ↳ Job initialized: {msg.get('job', {}).get('prompt', '')[:50]}...")
                        elif msg_type == "event":
                            events.append(msg)
                            print(f"  ↳ Event: {msg.get('message', 'unknown')}")
                        elif msg_type == "complete":
                            job = msg.get("job", {})
                            elapsed = (datetime.now() - start_time).total_seconds()
                            print(f"  ✓ COMPLETED in {elapsed:.1f}s")
                            print(f"    - Reward: {job.get('overall_reward', 0):.2f}/10")
                            print(f"    - Steps: {job.get('steps', 0)}")
                            return {"status": "completed", "events": len(events), "reward": job.get('overall_reward', 0)}
                        elif msg_type == "error":
                            print(f"  ✗ ERROR: {msg.get('message', 'unknown')}")
                            return {"status": "error", "message": msg.get('message')}
                    except asyncio.TimeoutError:
                        continue
                    except:
                        break
    except Exception as e:
        print(f"  ✗ WebSocket error: {e}")
        return {"status": "error", "message": str(e)}

async def run_production_tests():
    """Run all production website generation tests"""
    print("="*70)
    print("AUTODEVOS PRODUCTION-GRADE WEBSITE TESTING")
    print("="*70)
    print()
    
    async with aiohttp.ClientSession() as session:
        # Test API connectivity
        try:
            async with session.get(f"{BASE_URL}/health") as resp:
                if resp.status != 200:
                    print("[FAIL] Backend not responding")
                    return
        except:
            print("[FAIL] Cannot connect to backend at localhost:8000")
            return
        
        print("[OK] Backend server is running\n")
        
        results = []
        
        for i, prompt_data in enumerate(PROMPTS, 1):
            print(f"[{i}/{len(PROMPTS)}] {prompt_data['name']}")
            print("-" * 70)
            
            # Create job
            job = await create_job(session, prompt_data)
            if not job:
                print(f"[FAIL] Could not create job\n")
                continue
            
            job_id = job.get("jobId")
            print(f"Job ID: {job_id}")
            print(f"Status: {job.get('status')}")
            print()
            
            # Monitor progress
            result = await monitor_websocket(job_id)
            results.append({
                "name": prompt_data["name"],
                "job_id": job_id,
                **result
            })
            
            print()
            await asyncio.sleep(1)  # Small delay between jobs
        
        # Summary
        print("="*70)
        print("TEST RESULTS SUMMARY")
        print("="*70)
        
        completed = sum(1 for r in results if r.get("status") == "completed")
        total_reward = sum(r.get("reward", 0) for r in results if r.get("status") == "completed")
        
        for result in results:
            status_icon = "✓" if result.get("status") == "completed" else "✗"
            reward = f"{result.get('reward', 0):.2f}/10" if result.get("status") == "completed" else "N/A"
            print(f"{status_icon} {result['name']:40s} | Reward: {reward:7s}")
        
        print()
        print(f"Completed: {completed}/{len(results)}")
        print(f"Total Rewards: {total_reward:.2f}")
        print(f"Average Reward: {total_reward/completed:.2f}" if completed > 0 else "Average Reward: N/A")
        print("="*70)
        print()
        print("✅ PRODUCTION TESTING COMPLETE")
        print()
        print("Next Steps:")
        print("1. Visit http://localhost:3002 to see generated sites")
        print("2. Check job histories and rewards")
        print("3. Review WebSocket streaming performance")
        print("4. Validate responsive design on mobile")
        print()

if __name__ == "__main__":
    print("Starting production tests in 2 seconds...")
    print("Make sure backend (port 8000) and frontend (port 3002) are running\n")
    
    asyncio.run(run_production_tests())
