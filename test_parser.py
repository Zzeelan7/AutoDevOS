#!/usr/bin/env python3
"""Test markdown-aware parser"""
import re

def _parse_generated_content(content):
    html = ''
    css = ''
    js = ''
    
    print(f'[Test] Content length: {len(content)} chars')
    print(f'[Test] Attempting markdown extraction...')
    
    # Strategy 1: Extract from markdown code blocks
    html_pattern = r'```html\s*\n(.*?)\n```'
    html_match = re.search(html_pattern, content, re.DOTALL | re.IGNORECASE)
    if html_match:
        html = html_match.group(1).strip()
        print(f'[Test] ✓ Found HTML: {len(html)} chars')
    
    css_pattern = r'```css\s*\n(.*?)\n```'
    css_match = re.search(css_pattern, content, re.DOTALL | re.IGNORECASE)
    if css_match:
        css = css_match.group(1).strip()
        print(f'[Test] ✓ Found CSS: {len(css)} chars')
    
    js_pattern = r'```(?:javascript|js)\s*\n(.*?)\n```'
    js_match = re.search(js_pattern, content, re.DOTALL | re.IGNORECASE)
    if js_match:
        js = js_match.group(1).strip()
        print(f'[Test] ✓ Found JS: {len(js)} chars')
    
    return html, css, js

# Test with realistic markdown output
test_content = '''Below is production code for a contact form website.

### HTML:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Contact Form</title>
</head>
<body>
    <form>
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
```

### CSS:

```css
body {
    font-family: Arial, sans-serif;
    margin: 20px;
    background: #f5f5f5;
}

form {
    max-width: 400px;
    padding: 20px;
    background: white;
    border-radius: 8px;
}

input {
    width: 100%;
    padding: 10px;
}

button {
    background: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
```

### JavaScript:

```javascript
document.querySelector('form').addEventListener('submit', function(e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    alert('Thanks, ' + name + '!');
});
```
'''

html, css, js = _parse_generated_content(test_content)
print(f'\n[RESULT] ✓ HTML: {len(html)} chars')
print(f'[RESULT] ✓ CSS: {len(css)} chars')
print(f'[RESULT] ✓ JS: {len(js)} chars')
print(f'\n[RESULT] HTML starts with: {html[:50]}...')
print(f'[RESULT] CSS starts with: {css[:50]}...')
print(f'[RESULT] JS starts with: {js[:50]}...')

# Validation
if html and css and js:
    print(f'\n✅ SUCCESS: All three formats extracted!')
else:
    print(f'\n❌ FAILURE: Some formats missing')
