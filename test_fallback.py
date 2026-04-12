#!/usr/bin/env python3
"""Quick test of GitHub model fallback"""
import asyncio
import sys
import os

os.chdir(r'c:\Users\zzeel\OneDrive\Desktop\AutoDevOS\hf-autodevos-space')
sys.path.insert(0, r'c:\Users\zzeel\OneDrive\Desktop\AutoDevOS\hf-autodevos-space')

from app import GenerationEngine

async def test():
    engine = GenerationEngine()
    
    print("Testing GitHub Models with fallback...")
    print("="*60)
    
    result = await engine._try_github("Create a simple website with blue background")
    
    if result['status'] == 'completed':
        print(f"\n✅ SUCCESS!")
        print(f"HTML: {len(result['html'])} chars")
        print(f"CSS: {len(result['css'])} chars")
        print(f"JS: {len(result['js'])} chars")
    else:
        print(f"\n❌ FAILED: {result['message']}")

asyncio.run(test())
