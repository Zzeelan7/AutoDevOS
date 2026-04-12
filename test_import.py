#!/usr/bin/env python3
"""Test if app can be imported without Gradio errors"""
import sys
import os

# Load token from environment variable
if 'GITHUB_TOKEN' not in os.environ:
    print('Warning: GITHUB_TOKEN not set')

sys.path.insert(0, r'c:\Users\zzeel\OneDrive\Desktop\AutoDevOS\hf-autodevos-space')

try:
    from app import GenerationEngine
    print('✅ Import successful')
    
    engine = GenerationEngine()
    print(f"🔧 [Engine] Configuration:")
    print(f"   OpenAI: {'Available' if engine.openai_client else 'Not Available'}")
    print(f"   GitHub: {'Available' if engine.github_token else 'Not Available'}")
    
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
