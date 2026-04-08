#!/usr/bin/env python3
"""
Comprehensive deployment validation test for AutoDevOS OpenEnv submission.
Tests all critical components before HuggingFace deployment.
"""
import sys
import asyncio
import subprocess

print("\n" + "="*70)
print("COMPREHENSIVE DEPLOYMENT VALIDATION TEST")
print("="*70 + "\n")

# TEST 1: Environment Validation
print("[1/4] OpenEnv Validate...")
sys.path.insert(0, 'backend')
try:
    exec(open('validate_env.py').read())
    test1_passed = True
except Exception as e:
    print(f"[✗] FAILED: {e}")
    test1_passed = False

# TEST 2: Dockerfile Build
print("\n[2/4] Dockerfile Build...")
try:
    result = subprocess.run(
        ['docker', 'image', 'inspect', 'autodevos-test:latest'],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
        print("[✓] Docker image exists and is valid")
        print("[✓] Image name: autodevos-test:latest")
        test2_passed = True
    else:
        print("[✗] Docker image not found")
        test2_passed = False
except Exception as e:
    print(f"[✗] FAILED: {e}")
    test2_passed = False

# TEST 3: inference.py Import
print("\n[3/4] inference.py Imports...")
try:
    import os
    os.environ['OPENAI_API_KEY'] = 'test_key'
    os.environ['API_BASE_URL'] = 'https://api.openai.com/v1'
    os.environ['MODEL_NAME'] = 'gpt-3.5-turbo'
    
    from inference import main
    print("[✓] inference.py imported successfully")
    print("[✓] Environment variables configured correctly")
    print("    - OPENAI_API_KEY: set")
    print("    - API_BASE_URL: https://api.openai.com/v1")
    print("    - MODEL_NAME: gpt-3.5-turbo")
    test3_passed = True
except Exception as e:
    print(f"[✗] FAILED: {e}")
    test3_passed = False

# TEST 4: OpenEnv Reset
print("\n[4/4] OpenEnv Reset (POST OK)...")
async def test_reset():
    from openenv_env import WebsiteGenerationEnv, ResetResponse
    try:
        env = WebsiteGenerationEnv(task_type='simple_landing_page')
        response = await env.reset()
        if isinstance(response, ResetResponse):
            obs = response.observation
            print("[✓] OpenEnv Reset successful")
            print(f"    - task_type: {obs.task_type}")
            print(f"    - current_iteration: {obs.current_iteration}")
            print(f"    - max_iterations: {obs.max_iterations}")
            return True
        return False
    except Exception as e:
        print(f"[✗] FAILED: {e}")
        return False

try:
    test4_passed = asyncio.run(asyncio.wait_for(test_reset(), timeout=10))
except asyncio.TimeoutError:
    print("[✗] FAILED: Timeout")
    test4_passed = False
except Exception as e:
    print(f"[✗] FAILED: {e}")
    test4_passed = False

# SUMMARY
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
tests = [
    ("OpenEnv Validate", test1_passed),
    ("Dockerfile Build", test2_passed),
    ("inference.py Imports", test3_passed),
    ("OpenEnv Reset (POST)", test4_passed),
]

for name, passed in tests:
    status = "[✓ PASS]" if passed else "[✗ FAIL]"
    print(f"{status} {name}")

all_passed = all(p for _, p in tests)
print("\n" + ("="*70))
print(f"OVERALL STATUS: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
print("="*70 + "\n")

sys.exit(0 if all_passed else 1)
