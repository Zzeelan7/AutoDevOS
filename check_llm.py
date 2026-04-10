#!/usr/bin/env python3
"""
Check LLM availability and display system status
"""
import requests
import os
from datetime import datetime

print("\n" + "="*80)
print("AUTODEVOS LLM INTEGRATION CHECK")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Check Ollama
print("[1] Checking Ollama (Local DeepSeek Coder)...")
try:
    resp = requests.get("http://localhost:11434/api/tags", timeout=2)
    if resp.status_code == 200:
        models = resp.json().get("models", [])
        model_names = [m.get("name", "") for m in models]
        
        if any("deepseek" in name.lower() for name in model_names):
            print("    ✓ Ollama is RUNNING")
            print(f"    ✓ DeepSeek Coder available")
            print(f"    Models: {', '.join(model_names[:3])}")
        else:
            print("    ✗ Ollama running but DeepSeek not found")
            print(f"    Available models: {model_names}")
    else:
        print("    ✗ Ollama not responding properly")
except Exception as e:
    print(f"    ✗ Ollama not available: {e}")

# Check OpenAI
print("\n[2] Checking OpenAI API Key...")
openai_key = os.getenv("OPENAI_API_KEY", "")
if openai_key:
    masked = openai_key[:10] + "..." + openai_key[-5:]
    print(f"    ✓ OpenAI API Key found: {masked}")
else:
    print("    ✗ No OpenAI API Key set")

print("\n" + "="*80)
print("SYSTEM STATUS")
print("="*80)

ollama_ok = False
try:
    resp = requests.get("http://localhost:11434/api/tags", timeout=2)
    if resp.status_code == 200:
        models = resp.json().get("models", [])
        ollama_ok = any("deepseek" in m.get("name", "").lower() for m in models)
except:
    pass

openai_ok = bool(os.getenv("OPENAI_API_KEY", ""))

print(f"\nOllama + DeepSeek: {'✓ READY' if ollama_ok else '✗ NOT AVAILABLE'}")
print(f"OpenAI Fallback:   {'✓ READY' if openai_ok else '✗ NOT AVAILABLE'}")

if ollama_ok or openai_ok:
    print("\n✅ LLM Code Generation: ENABLED")
    print("   → Server will generate production-grade HTML/CSS/JS from prompts")
else:
    print("\n⚠️  LLM Code Generation: FALLBACK MODE")
    print("   → Using template code generator")
    print("   → To enable: Start Ollama (ollama serve) or set OPENAI_API_KEY")

print("\n" + "="*80 + "\n")
