#!/usr/bin/env python3
"""Test complex prompt generation"""
import asyncio
import aiohttp
import json
import time

async def test_complex_generation():
    """Test with the AURA INTERIORS luxury prompt"""
    
    prompt = """### SYSTEM ROLE You are an expert Senior Full-Stack Engineer and Lead UI/UX Designer specializing in luxury e-commerce and high-end architectural aesthetics. Your goal is to write production-grade, SEO-optimized, and modular code for a luxury interior design studio website. ### PROJECT SCOPE Build a multi-file website (HTML, CSS, JS) for "AURA INTERIORS." The brand identity is: Minimalist, Sophisticated, High-Contrast, and Tactile. ### CORE REQUIREMENTS & FEATURES 1. PRODUCTION-GRADE STRUCTURE: Use semantic HTML5 and CSS custom properties for a luxury color palette. 2. LUXURY UI/UX FEATURES: Hero section with parallax scroll. 3. TECHNICAL SPECS: Lazy loading, SEO with JSON-LD, mobile-first responsive design."""
    
    print("[TEST] Creating complex job...")
    print(f"[PROMPT] Length: {len(prompt)} chars")
    
    async with aiohttp.ClientSession() as session:
        # 1. Create job
        res = await session.post(
            "http://127.0.0.1:8000/api/jobs",
            json={"prompt": prompt}
        )
        
        job_id = (await res.json()).get("jobId")
        print(f"[OK] Job: {job_id}")
        
        # 2. Connect WebSocket and stream events
        uri = f"ws://127.0.0.1:8000/ws/{job_id}"
        
        try:
            async with session.ws_connect(uri, timeout=aiohttp.ClientTimeout(total=300)) as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        event = json.loads(msg.data)
                        
                        if event.get("type") == "event":
                            print(f"[EVENT] {event.get('message', '')}")
                        elif event.get("type") == "error":
                            print(f"[ERROR] {event.get('message', '')}")
                            break
                        elif event.get("type") == "complete":
                            print(f"[COMPLETE] Success!")
                            job = event.get("job", {})
                            print(f"         Reward: {job.get('overall_reward', 0):.2f}/10")
                            
                            # Get preview
                            preview_res = await session.get(
                                f"http://127.0.0.1:8000/api/jobs/{job_id}/preview"
                            )
                            if preview_res.status == 200:
                                preview = await preview_res.json()
                                html_len = len(preview.get("html", ""))
                                css_len = len(preview.get("css", ""))
                                js_len = len(preview.get("js", ""))
                                print(f"         Generated: HTML={html_len}, CSS={css_len}, JS={js_len} chars")
                                if html_len > 100:
                                    print(f"         HTML Preview: {preview['html'][:150]}...")
                            break
        except asyncio.TimeoutError:
            print("[ERROR] WebSocket timeout - generation taking too long")

if __name__ == "__main__":
    print("[TEST] Complex AURA INTERIORS Generation Test\n")
    asyncio.run(test_complex_generation())
    print("\n[DONE]")
