#!/usr/bin/env python3
"""Direct test of GitHub Models API"""

import os
import sys

# Try with OpenAI SDK directly
try:
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI SDK not installed. Run: pip install openai")
    sys.exit(1)

def test_direct():
    """Direct test using OpenAI SDK"""
    token = os.getenv("GITHUB_TOKEN", "").strip('"').strip("'")
    
    if not token or token == "your-github-token-here":
        print("❌ GITHUB_TOKEN not set or placeholder")
        print("")
        print("To generate a token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Click 'Fine-grained tokens'")
        print("3. Click 'Generate new token'")
        print("4. Name: 'GitHub Models'")
        print("5. Permissions: Account - Models (Read-only)")
        print("6. Repository access: All repositories")
        print("7. Click 'Generate' and copy token")
        print("")
        print("Then set it:")
        print('  $env:GITHUB_TOKEN = "github_pat_xxxxxxx..."')
        print("  python test_github_direct.py")
        return
    
    print("✅ Token found")
    print(f"   Token: {token[:20]}...")
    print("")
    
    try:
        client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=token
        )
        
        print("📡 Calling GitHub Models API...")
        print(f"   Model: gpt-4o")
        print(f"   Endpoint: https://models.github.ai/inference")
        print("")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": "Say hello and explain what you are in 1 sentence."
            }],
            max_tokens=100
        )
        
        print("✅ SUCCESS!")
        print("")
        print("Response:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("")
        
        # Parse error for debugging
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            print("  → Token is invalid or expired")
            print("  → Generate a new token at: https://github.com/settings/tokens")
        elif "404" in error_str:
            print("  → Endpoint not found. Current endpoint:")
            print("     https://models.github.ai/inference")
            print("  → Check if this is correct")
        elif "429" in error_str or "rate" in error_str:
            print("  → Rate limit exceeded")
            print("  → Wait a few minutes and try again")
        elif "connection" in error_str:
            print("  → Connection failed")
            print("  → Check if endpoint is accessible")
        else:
            print(f"  → {str(e)[:200]}")

if __name__ == "__main__":
    test_direct()
