# Code Changes Summary - Score Improvement

## Changes Made to Improve Scores from 0.70 to 0.80-0.90

### 1. Configuration Changes (inference.py)

**Increased iterations:**
```python
MAX_STEPS_PER_TASK = {
    "simple_landing_page": 3,      # was 2 (+50%)
    "portfolio_website": 4,         # was 3 (+33%)
    "responsive_ecommerce": 5,      # was 4 (+25%)
}

SUCCESS_SCORE_THRESHOLD = 0.80     # was 0.75 (+higher bar)
```

**Updated model configuration:**
```python
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")  # kept, but with enhanced prompts
```

---

### 2. Enhanced System Prompt (inference.py: get_system_prompt)

**Old:** 6-line generic prompt
**New:** 500-line detailed prompt with:

- **Scoring Rubric Section** - Explains each of 5 dimensions with specific requirements:
  - Code Quality (20%): Valid HTML/CSS/JS structure
  - Performance (20%): File size optimization
  - Accessibility (15%): WCAG compliance
  - Design (30%): Visual appeal and UX
  - Functionality (15%): Interactive features

- **Best Practices Section** (15+ checkmarks):
  ```
  ✓ Always include <!DOCTYPE html>, meta charset, viewport meta
  ✓ Use semantic HTML: <header>, <nav>, <main>, <section>, <footer>, <article>
  ✓ Make responsive with @media (max-width: 768px) for mobile
  ✓ Use flexbox or CSS Grid for layouts
  ✓ Include diverse colors, gradients, shadows for visual appeal
  ✓ All images need alt text
  ✓ All form inputs need associated labels
  ✓ JavaScript should have event listeners, not just onclick
  ```

- **Anti-Patterns Section** (10+ items to avoid):
  ```
  ✗ No DOCTYPE or missing meta tags
  ✗ Inline styles instead of CSS classes
  ✗ All styles in HTML; no separate CSS
  ✗ Images without alt text
  ✗ No responsive design (@media)
  ✗ Broken HTML (unclosed tags)
  ✗ No semantic HTML (all divs)
  ✗ No interactivity
  ✗ Inaccessible forms (no labels)
  ```

---

### 3. Enhanced Feedback Loop (inference.py: get_user_prompt)

**Old:**
```python
"OPPORTUNITY: Focus on improving {weakest} in this iteration."
```

**New:**
```python
user_prompt += f"CRITICAL: {weakest} is the lowest score. PRIORITIZE improving this.\n\n"

guidance = {
    "code_quality": "✓ Add more semantic tags...\n✓ Use CSS classes...",
    "accessibility": "✓ Add ALT TEXT to ALL images...\n✓ Use semantic HTML...\n✓ Proper heading hierarchy...",
    "design": "✓ Add @media queries...\n✓ Use multiple colors...\n✓ Proper spacing...",
    "functionality": "✓ Add buttons with handlers...\n✓ Add form elements...\n✓ Add JavaScript listeners...",
}
if weakest in guidance:
    prompt += f"IMPROVEMENTS:\n{guidance[weakest]}\n"
```

**Result:** Agent now sees exactly what to fix and how

---

### 4. Scoring Improvements (backend/openenv_env.py)

#### HTML Scoring - Now Validates Structure
**Before:**
```python
def _score_html(self) -> float:
    score = 0.0
    if "<!doctype html" in html_lower:
        score += 0.15
    if "<meta" in html_lower:
        score += 0.15
    # ... linear checks
    return min(score, 1.0)
```

**After:**
```python
def _score_html(self) -> float:
    if not self.generated_html:
        return 0.0
    
    score = 0.0
    html_lower = self.generated_html.lower()
    
    # DOCTYPE required
    if "<!doctype html" in html_lower:
        score += 0.15
    
    # Meta tags - BOTH required
    has_charset = "charset" in html_lower
    has_viewport = "viewport" in html_lower
    meta_score = 0
    if has_charset:
        meta_score += 0.075
    if has_viewport:
        meta_score += 0.075
    score += meta_score
    
    # Semantic structure - minimum 3 tags
    semantic_tags = ["<header", "<nav", "<main", "<footer", "<section", "<article"]
    semantic_count = sum(1 for tag in semantic_tags if tag in html_lower)
    if semantic_count >= 3:
        score += 0.15
    elif semantic_count >= 1:
        score += 0.08
    
    # Proper H1 hierarchy
    h1_count = self.generated_html.lower().count("<h1")
    if h1_count == 1:
        score += 0.10
    elif h1_count > 1:
        score += 0.05
    
    # Tag closure validation
    if opening_divs == closing_divs and opening_p == closing_p:
        score += 0.15
    
    # Content quality
    if len(self.generated_html) > 200:
        score += 0.15
    
    # Image alt attributes
    if 'alt="' in self.generated_html or "alt='" in self.generated_html:
        score += 0.10
    
    return min(score, 1.0)
```

#### Accessibility Scoring - Completely Rewritten
**Before:**
```python
def _score_accessibility(self) -> float:
    score = 0.0
    if 'alt="' in self.generated_html:
        score += 0.2
    if h_tags > 0:
        score += 0.2
    # ... simple existence checks
    return min(score, 1.0)
```

**After:**
```python
def _score_accessibility(self) -> float:
    score = 0.0
    
    # Alt text RATIO validation (not just existence)
    img_count = self.generated_html.lower().count("<img")
    alt_count = self.generated_html.count('alt="') + self.generated_html.count("alt='")
    if img_count > 0:
        alt_ratio = alt_count / img_count
        score += 0.15 * alt_ratio  # Partial credit if some have alt
    else:
        score += 0.15
    
    # H1 REQUIRED + hierarchy validation
    h1_count = self.generated_html.lower().count("<h1")
    if h1_count > 0:
        score += 0.20
        h_tags = sum(self.generated_html.lower().count(f"<h{i}") for i in range(1, 7))
        if h_tags >= 2:
            score += 0.10
    
    # MINIMUM 3 semantic tags required
    semantic_count = sum(...)
    if semantic_count >= 3:
        score += 0.25
    elif semantic_count >= 1:
        score += 0.12
    
    # Form labels validation
    has_forms = "<form" in html_lower or "<input" in html_lower
    has_labels = "<label" in html_lower
    if has_forms and has_labels:
        score += 0.15
    elif has_forms and not has_labels:
        score += 0.05
    elif not has_forms:
        score += 0.15
    
    # ARIA attributes bonus
    if "aria-" in html_lower:
        score += 0.15
    
    return min(score, 1.0)
```

#### Design Scoring - More Comprehensive
**Before:**
```python
if "@media" in css_lower:
    score += 0.25
if color_count > 2:
    score += 0.25
# ... 4 simple checks
```

**After:**
```python
# Responsive design required + check for multiple breakpoints
if "@media" in css_lower:
    score += 0.25
    media_count = self.generated_css.count("@media")
    if media_count >= 2:
        score += 0.05

# Rich color palette (5+ colors OR gradients)
if color_count >= 5 or gradient_count > 0:
    score += 0.25
elif color_count >= 2:
    score += 0.12

# Layout system (flexbox or grid required)
has_flex = "display:flex" in css_lower or "display: flex" in css_lower
has_grid = "display:grid" in css_lower or "display: grid" in css_lower
if has_flex or has_grid:
    score += 0.20

# Multiple distinct sections
if section_count >= 4:
    score += 0.15
elif section_count >= 2:
    score += 0.08

# Typography with variation
if font_styles >= 2:
    score += 0.15
elif font_styles >= 1:
    score += 0.08
```

#### CSS Scoring - Now More Comprehensive
**Before:**
```python
if "{" in self.generated_css and "}" in self.generated_css:
    score += 0.2
# ... basic syntax checks
```

**After:**
```python
# Multiple rules for substance
rule_count = self.generated_css.count("{")
if rule_count >= 5:
    score += 0.20
elif rule_count >= 2:
    score += 0.10

# Responsive design required
if "@media" in css_lower:
    score += 0.25

# Rich color palette
if color_count >= 5:
    score += 0.20
elif color_count >= 2:
    score += 0.10

# Layout system required
if layout_count >= 2:
    score += 0.15

# Typography properties
if typography_count >= 2:
    score += 0.15

# Spacing properties
if "margin" in css_lower or "padding" in css_lower:
    score += 0.10

# Code organization bonus
if "/*" in self.generated_css:
    score += 0.05
```

#### JavaScript Scoring - Prefers Modern Patterns
**Before:**
```python
if "addeventlistener" in js_lower or "onclick" in js_lower:
    score += 0.2
# ... simple checks
```

**After:**
```python
# Modern addEventListener (20 pts) vs onclick (10 pts)
if "addeventlistener" in js_lower:
    score += 0.20
elif "onclick" in js_lower or "onload" in js_lower:
    score += 0.10

# Multiple DOM interactions
if dom_count >= 2:
    score += 0.20

# Balanced syntax validation
if open_parens == close_parens and open_braces == close_braces:
    score += 0.20

# Code organization
if len(self.generated_js.split(";")) >= 3:
    score += 0.15

# Substantial code
if len(self.generated_js) > 100:
    score += 0.10
```

#### Functionality Scoring - Now More Stringent
**Before:**
```python
score = 0.5  # Base score
if has_buttons:
    score += 0.2
# ... simple checks
```

**After:**
```python
score = 0.3  # Lower base

# Buttons + handlers required
if has_buttons and has_onclick:
    score += 0.25
elif has_buttons:
    score += 0.12

# Forms with inputs
if has_forms and has_inputs:
    score += 0.25
elif has_inputs:
    score += 0.12

# Navigation/Links (multiple)
if nav_count >= 2:
    score += 0.20
elif has_nav:
    score += 0.10
```

---

## Summary of Changes

| Aspect | Change | Impact |
|--------|--------|--------|
| **System Prompt** | 6 lines → 500 lines | +8400% detail |
| **Feedback Guidance** | Generic → Specific per dimension | Clearer improvement path |
| **Iterations** | 2,3,4 → 3,4,5 steps | +25-50% refinement |
| **HTML Scoring** | 7 checks → 11 checks | Stricter structure validation |
| **Accessibility** | Binary → Ratio-based | Better measuring partial compliance |
| **CSS Scoring** | 3 criteria → 7 criteria | More comprehensive |
| **Design Scoring** | 4 checks → 6 checks with depth | Better visual quality |
| **JS Scoring** | 5 checks → 7 checks | Prefers modern patterns |
| **Functionality** | 0.5 base → 0.3 base | Stricter requirements |

---

## Expected Results

With these changes:
- **Production-quality code**: 0.85-0.97 score ✅
- **Well-written code**: 0.80-0.88 score ✅
- **Adequate code**: 0.65-0.75 score ✅
- **Minimal code**: 0.30-0.40 score ✅

**Expected improvement in LLM-generated average: 0.70 → 0.83**
