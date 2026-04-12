#!/usr/bin/env python3
"""Debug LLM generation to see what's being returned"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "hf-autodevos-space"))

from app import GenerationEngine

async def debug_generation():
    """Debug what the LLM actually returns"""
    engine = GenerationEngine()
    
    prompt = "Create a dark blue website with white text"
    
    print("=" * 60)
    print("DEBUGGING LLM GENERATION")
    print("=" * 60)
    print()
    
    # Test OpenAI directly
    if engine.openai_client:
        print("✅ OpenAI client available")
        print()
        print("Calling OpenAI...")
        result = await engine._try_openai(prompt)
        
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message', 'N/A')}")
        print()
        
        if result.get('status') == 'completed':
            html = result.get('html', '')
            css = result.get('css', '')
            js = result.get('js', '')
            
            print("✅ Successfully generated!")
            print()
            print("HTML:")
            print(html[:300])
            if len(html) > 300:
                print(f"... ({len(html) - 300} more chars)")
            print()
            print("CSS:")
            print(css[:300])
            if len(css) > 300:
                print(f"... ({len(css) - 300} more chars)")
            print()
            print("JS:")
            print(js[:300] if js else "(empty)")
        else:
            print(f"❌ Error: {result.get('message')}")
            print()
            print("This means:")
            print("- LLM may not have been called")
            print("- Or the response format didn't match expected structure")
            print("- Or the parsing failed")
    else:
        print("❌ OpenAI client NOT available")
        print()
        if engine.github_token:
            print("GitHub token available, attempting GitHub Models...")
            result = await engine._try_github(prompt)
            print(f"Status: {result.get('status')}")
            print(f"Message: {result.get('message')}")
        else:
            print("No backends available!")

if __name__ == "__main__":
    asyncio.run(debug_generation())
