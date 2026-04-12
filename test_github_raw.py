#!/usr/bin/env python3
"""Debug GitHub API response format"""
import asyncio
import os
import sys

sys.path.insert(0, r'c:\Users\zzeel\OneDrive\Desktop\AutoDevOS\hf-autodevos-space')

os.environ['GITHUB_TOKEN'] = 'GITHUB_TOKEN_PLACEHOLDER'

from app import GenerationEngine

async def test_github_raw():
    """Test GitHub and show raw response"""
    engine = GenerationEngine()
    
    prompt = "Create a simple blue website with white text"
    print(f"Prompt: {prompt}\n")
    print("="*60)
    
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=os.environ['GITHUB_TOKEN']
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Generate a complete, functional website based on this description: {prompt}

Please provide ONLY valid HTML/CSS/JavaScript code in this exact format:

HTML:
[complete HTML code]

CSS:
[complete CSS code]

JS:
[complete JavaScript code]

Make sure:
- HTML is valid and complete (includes <!DOCTYPE>, head, body)
- CSS is production-ready with modern styling
- JavaScript adds interactivity and animations
- All code works together seamlessly"""
            }],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        print(f"Raw Response ({len(content)} chars):")
        print("="*60)
        print(content)
        print("="*60)
        
        # Test parsing
        html_idx = content.find("HTML:")
        css_idx = content.find("CSS:")
        js_idx = content.find("JS:")
        
        print(f"\nParsing markers found:")
        print(f"  HTML: index {html_idx}")
        print(f"  CSS:  index {css_idx}")
        print(f"  JS:   index {js_idx}")
        
        if html_idx >= 0:
            html_start = html_idx + 5
            html_end = css_idx if css_idx >= 0 else js_idx if js_idx >= 0 else len(content)
            html = content[html_start:html_end].strip()
            print(f"\nExtracted HTML ({len(html)} chars):")
            print(html[:200])
            print("...")
        
        if css_idx >= 0:
            css_start = css_idx + 5
            css_end = js_idx if js_idx >= 0 else len(content)
            css = content[css_start:css_end].strip()
            print(f"\nExtracted CSS ({len(css)} chars):")
            print(css[:200])
            print("...")
        
        if js_idx >= 0:
            js_start = js_idx + 3
            js = content[js_start:].strip()
            print(f"\nExtracted JS ({len(js)} chars):")
            print(js[:200] if js else "(empty)")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_github_raw())
