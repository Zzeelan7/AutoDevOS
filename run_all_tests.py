#!/usr/bin/env python3
"""
Final deployment verification - all 4 tests in one command.
"""
import subprocess
import asyncio
import sys
import os

print('='*70)
print('FINAL DEPLOYMENT VERIFICATION - ALL 4 TESTS')
print('='*70)
print()

results = {}

# TEST 1: openenv validate
print('[1/4] OpenEnv Validate...')
try:
    result = subprocess.run(['python', 'validate_env.py'], capture_output=True, text=True, timeout=15)
    if 'All validation tests passed' in result.stdout:
        print('[✓ PASS] OpenEnv Validate')
        results['openenv_validate'] = True
    else:
        print('[✗ FAIL] OpenEnv Validate')
        print(result.stdout[-200:] if result.stdout else '')
        results['openenv_validate'] = False
except Exception as e:
    print(f'[✗ FAIL] OpenEnv Validate - {e}')
    results['openenv_validate'] = False

# TEST 2: Dockerfile at repo root
print('[2/4] Dockerfile at repo root...')
try:
    result = subprocess.run(
        ['docker', 'run', '--rm', 'autodevos-test:latest', 'python', '-c', 'print("OK")'],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0 and 'OK' in result.stdout:
        print('[✓ PASS] Dockerfile at repo root')
        results['dockerfile'] = True
    else:
        print('[✗ FAIL] Dockerfile at repo root')
        print(result.stderr[-200:] if result.stderr else '')
        results['dockerfile'] = False
except Exception as e:
    print(f'[✗ FAIL] Dockerfile at repo root - {e}')
    results['dockerfile'] = False

# TEST 3: inference.py at repo root
print('[3/4] inference.py at repo root...')
try:
    os.environ['OPENAI_API_KEY'] = 'test'
    os.environ['API_BASE_URL'] = 'https://api.openai.com/v1'
    os.environ['MODEL_NAME'] = 'gpt-3.5-turbo'
    from inference import validate_environment_variables, validate_openai_client, validate_logging_format
    
    checks = [
        validate_environment_variables(),
        validate_openai_client(),
        validate_logging_format()
    ]
    
    if all(checks):
        print('[✓ PASS] inference.py at repo root')
        results['inference'] = True
    else:
        print(f'[✗ FAIL] inference.py at repo root - checks: {checks}')
        results['inference'] = False
except Exception as e:
    print(f'[✗ FAIL] inference.py at repo root - {e}')
    import traceback
    traceback.print_exc()
    results['inference'] = False

# TEST 4: OpenEnv Reset (POST OK)
print('[4/4] OpenEnv Reset (POST OK)...')
try:
    sys.path.insert(0, 'backend')
    from openenv_env import WebsiteGenerationEnv, ResetResponse
    
    async def test_reset():
        for task in ['simple_landing_page', 'portfolio_website', 'responsive_ecommerce']:
            env = WebsiteGenerationEnv(task_type=task)
            resp = await env.reset()
            if not isinstance(resp, ResetResponse):
                return False
        return True
    
    if asyncio.run(test_reset()):
        print('[✓ PASS] OpenEnv Reset (POST OK)')
        results['reset'] = True
    else:
        print('[✗ FAIL] OpenEnv Reset (POST OK)')
        results['reset'] = False
except Exception as e:
    print(f'[✗ FAIL] OpenEnv Reset (POST OK) - {e}')
    import traceback
    traceback.print_exc()
    results['reset'] = False

# SUMMARY
print()
print('='*70)
print('SUMMARY')
print('='*70)
for test, passed in results.items():
    status = '✓ PASS' if passed else '✗ FAIL'
    print(f'{status} - {test}')

all_pass = all(results.values())
print()
if all_pass:
    print('✓ ALL 4 TESTS PASSED - READY FOR DEPLOYMENT')
    sys.exit(0)
else:
    print('✗ SOME TESTS FAILED')
    sys.exit(1)
