#!/usr/bin/env python3
"""Test GitHub Models API integration"""

import os
import sys
import asyncio
from pathlib import Path

# Add hf-autodevos-space to path
sys.path.insert(0, str(Path(__file__).parent / "hf-autodevos-space"))

from app import GenerationEngine

async def test_github_models():
    """Test GitHub Models endpoint"""
    token = os.getenv("GITHUB_TOKEN", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    
    print("[Test] Testing GitHub Models Integration")
    print(f"[Test] GITHUB_TOKEN: {token[:20]}..." if token else "[Test] GITHUB_TOKEN: NOT SET")
    print(f"[Test] OPENAI_API_KEY: {openai_key[:10]}..." if openai_key else "[Test] OPENAI_API_KEY: NOT SET")
    print()
    
    # Initialize engine
    engine = GenerationEngine()
    
    # Test with simple prompt
    prompt = "Create a dark blue website with white text and a gradient background"
    
    print(f"[Test] Prompt: {prompt}")
    print("[Test] Calling GitHub Models...")
    print()
    
    result = await engine._try_github(prompt)
    
    print(f"[Test] Status: {result.get('status')}")
    print(f"[Test] Message: {result.get('message', 'N/A')}")
    
    if result.get("status") == "completed":
        html = result.get("html", "")
        css = result.get("css", "")
        js = result.get("js", "")
        print(f"[Test] ✅ SUCCESS!")
        print(f"[Test] HTML size: {len(html)} chars")
        print(f"[Test] CSS size: {len(css)} chars")
        print(f"[Test] JS size: {len(js)} chars")
        print()
        print("[Test] HTML sample:")
        print(html[:200] + "..." if len(html) > 200 else html)
    else:
        print(f"[Test] ❌ FAILED: {result.get('message')}")
        print()
        print("[Test] Debugging info:")
        print(f"  - Check token is valid at: https://github.com/settings/tokens")
        print(f"  - Token must have 'models' scope (Read-only)")
        print(f"  - Endpoint: https://models.github.ai/inference")
        print(f"  - Model: gpt-4o")

if __name__ == "__main__":
    asyncio.run(test_github_models())
