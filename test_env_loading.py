#!/usr/bin/env python3
"""Test that .env loading works"""
import subprocess
import sys

# Run in completely fresh process
result = subprocess.run([
    sys.executable, '-c',
    '''
import sys
sys.path.insert(0, r"c:\\Users\\zzeel\\OneDrive\\Desktop\\AutoDevOS\\hf-autodevos-space")
from app import GenerationEngine
engine = GenerationEngine()
print(f"OpenAI: {'Available' if engine.openai_client else 'Not Available'}")
print(f"GitHub Token: {engine.github_token[:20] if engine.github_token else 'None'}...")
'''
], capture_output=True, text=True, cwd=r'c:\Users\zzeel\OneDrive\Desktop\AutoDevOS\hf-autodevos-space')

print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)
print(f"\nReturn code: {result.returncode}")
