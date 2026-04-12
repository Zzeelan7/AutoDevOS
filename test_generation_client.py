import asyncio
import os
import sys
import json
sys.path.insert(0, r'c:\Users\zzeel\OneDrive\Desktop\AutoDevOS\hf-autodevos-space')

# Set token
os.environ['GITHUB_TOKEN'] = 'GITHUB_TOKEN_PLACEHOLDER'

from app import GenerationEngine

async def test_full_flow():
    """Test complete generation workflow"""
    engine = GenerationEngine()
    
    # Test different prompts
    test_prompts = [
        "Create a modern landing page with blue gradient and white text",
        "Make a portfolio website with cards layout",
        "Build a dark theme dashboard with sidebar"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {prompt}")
        print(f"{'='*60}")
        
        result = await engine.generate_website(prompt)
        
        print(f"Status: {result['status']}")
        if result['status'] == 'completed':
            print(f"HTML length: {len(result.get('html', ''))} chars")
            print(f"CSS length: {len(result.get('css', ''))} chars")
            print(f"JS length: {len(result.get('js', ''))} chars")
            
            # Show first 200 chars of CSS
            css = result.get('css', '')
            if css:
                print(f"\nCSS Preview:\n{css[:300]}...")
            
            # Show if HTML exists
            html = result.get('html', '')
            if html:
                print(f"\nHTML Preview:\n{html[:300]}...")
            else:
                print("\n⚠️  No HTML in response")
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")

asyncio.run(test_full_flow())
