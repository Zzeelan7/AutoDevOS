#!/usr/bin/env python3
"""Test parsing with proper markdown removal"""
import os

os.environ['GITHUB_TOKEN'] = 'GITHUB_TOKEN_PLACEHOLDER'

# Sample response like we get from GitHub
sample_response = """Here is the complete, functional website code:

HTML:
```html
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello World</h1></body>
</html>
```

CSS:
```css
body { color: blue; }
```

JS:
```javascript
console.log('test');
```

More text here"""

print("Original response:")
print("="*60)
print(sample_response)
print("="*60)

# Test parsing
html_idx = sample_response.find("HTML:")
css_idx = sample_response.find("CSS:")
js_idx = sample_response.find("JS:")

print(f"\nMarkers found: HTML={html_idx}, CSS={css_idx}, JS={js_idx}")

# Extract HTML with improved logic
if html_idx >= 0:
    html_start = html_idx + len("HTML:")
    html_end = css_idx if css_idx >= 0 else js_idx if js_idx >= 0 else len(sample_response)
    html_raw = sample_response[html_start:html_end].strip()
    
    print(f"\nRaw HTML ({len(html_raw)} chars):")
    print(repr(html_raw[:100]))
    
    # Remove markdown  - new improved logic
    html = html_raw
    while html.startswith("```"):
        first_nl = html.find("\n")
        if first_nl >= 0:
            html = html[first_nl+1:]
        else:
            break
    if "```" in html:
        html = html[:html.rfind("```")]
    html = html.strip()
    
    print(f"\nCleaned HTML ({len(html)} chars):")
    print(html)
    print()

# Extract CSS with improved logic
if css_idx >= 0:
    css_start = css_idx + len("CSS:")
    css_end = js_idx if js_idx >= 0 else len(sample_response)
    css_raw = sample_response[css_start:css_end].strip()
    
    print(f"Raw CSS ({len(css_raw)} chars):")
    print(repr(css_raw[:100]))
    
    # Remove markdown - new improved logic
    css = css_raw
    while css.startswith("```"):
        first_nl = css.find("\n")
        if first_nl >= 0:
            css = css[first_nl+1:]
        else:
            break
    if "```" in css:
        css = css[:css.rfind("```")]
    css = css.strip()
    
    print(f"\nCleaned CSS ({len(css)} chars):")
    print(css)
    print()

# Extract JS with improved logic
if js_idx >= 0:
    js_start = js_idx + len("JS:")
    js_raw = sample_response[js_start:].strip()
    
    print(f"Raw JS ({len(js_raw)} chars):")
    print(repr(js_raw[:100]))
    
    # Remove markdown - new improved logic
    js = js_raw
    while js.startswith("```"):
        first_nl = js.find("\n")
        if first_nl >= 0:
            js = js[first_nl+1:]
        else:
            break
    if "```" in js:
        js = js[:js.rfind("```")]
    js = js.strip()
    
    print(f"\nCleaned JS ({len(js)} chars):")
    print(js)
