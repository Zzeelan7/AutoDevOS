#!/usr/bin/env python3
"""Test the complete generation pipeline with markdown-aware parser"""
import sys
sys.path.insert(0, r'c:\Users\zzeel\OneDrive\Desktop\AutoDevOS\hf-autodevos-space')

from app import generate_website

# Test with a simple prompt
prompt = "Create a simple minimal landing page"

print(f"Testing with prompt: '{prompt}'")
print("=" * 60)

try:
    # Call the function directly
    status, preview, css, html, js = generate_website(prompt)
    
    print(f"\n[RESULTS]")
    print(f"Status: {status}")
    print(f"HTML length: {len(html)} chars")
    print(f"CSS length: {len(css)} chars")
    print(f"JS length: {len(js)} chars")
    
    if html:
        print(f"\n✓ HTML extracted successfully")
        print(f"  First 100 chars: {html[:100]}...")
    else:
        print(f"✗ HTML not extracted")
    
    if css:
        print(f"\n✓ CSS extracted successfully")
        print(f"  First 100 chars: {css[:100]}...")
    else:
        print(f"✗ CSS not extracted")
    
    if js:
        print(f"\n✓ JS extracted successfully")
        print(f"  First 100 chars: {js[:100]}...")
    else:
        print(f"✗ JS not extracted")
    
    if html and css and js:
        print(f"\n✅ ALL FORMATS EXTRACTED - Parser is working!")
    elif html or css or js:
        print(f"\n⚠️  Partial extraction - Some formats missing")
    else:
        print(f"\n❌ NO EXTRACTION - Parser failed")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
