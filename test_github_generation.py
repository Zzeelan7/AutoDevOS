#!/usr/bin/env python3
"""Test GitHub Models generation directly"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "hf-autodevos-space"))

from app import GenerationEngine

async def test_github_generation():
    """Force test GitHub Models"""
    engine = GenerationEngine()
    
    prompt = "Create a dark blue website with white text and gradient button"
    
    print("=" * 60)
    print("TESTING GITHUB MODELS GENERATION")
    print("=" * 60)
    print()
    print(f"Prompt: {prompt}")
    print()
    
    if not engine.github_token:
        print("❌ No GitHub token found")
        return
    
    print(f"Token: {engine.github_token[:20]}...")
    print()
    print("Calling GitHub Models...")
    print()
    
    result = await engine._try_github(prompt)
    
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message', 'N/A')}")
    print()
    
    if result.get('status') == 'completed':
        html = result.get('html', '')
        css = result.get('css', '')
        js = result.get('js', '')
        
        print("✅ SUCCESS! Website generated!")
        print()
        print(f"HTML size: {len(html)} chars")
        print(f"CSS size: {len(css)} chars")
        print(f"JS size: {len(js)} chars")
        print()
        print("-" * 60)
        print("GENERATED HTML:")
        print("-" * 60)
        print(html)
        print()
        print("-" * 60)
        print("GENERATED CSS:")
        print("-" * 60)
        print(css)
        print()
        if js:
            print("-" * 60)
            print("GENERATED JS:")
            print("-" * 60)
            print(js)
        
        # Show combined preview
        print()
        print("-" * 60)
        print("PREVIEW (Combined HTML + CSS):")
        print("-" * 60)
        preview = html
        if css and "<style>" not in preview:
            if "</head>" in preview:
                preview = preview.replace("</head>", f"<style>{css}</style></head>", 1)
            else:
                preview = f"<head><style>{css}</style></head>{preview}"
        if js and "<script>" not in preview:
            if "</body>" in preview:
                preview = preview.replace("</body>", f"<script>{js}</script></body>", 1)
            else:
                preview += f"<script>{js}</script>"
        print(preview)
    else:
        print(f"❌ FAILED: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(test_github_generation())
