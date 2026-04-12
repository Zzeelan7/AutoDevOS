#!/usr/bin/env python3
"""
Final deployment verification - all 4 tests in one command.
"""
import subprocess
import asyncio
import sys
import os

# Windows consoles often use cp1252; avoid Unicode checkmarks in prints.
def _ok(label: str) -> None:
    print(f"[PASS] {label}")


def _fail(label: str, detail: str = "") -> None:
    print(f"[FAIL] {label}" + (f" - {detail}" if detail else ""))


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
        _ok('OpenEnv Validate')
        results['openenv_validate'] = True
    else:
        _fail('OpenEnv Validate')
        print(result.stdout[-200:] if result.stdout else '')
        results['openenv_validate'] = False
except Exception as e:
    _fail('OpenEnv Validate', str(e))
    results['openenv_validate'] = False

# TEST 2: Dockerfile at repo root
print('[2/4] Dockerfile at repo root...')
try:
    result = subprocess.run(
        ['docker', 'run', '--rm', 'autodevos-test:latest', 'python', '-c', 'print("OK")'],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0 and 'OK' in result.stdout:
        _ok('Dockerfile at repo root')
        results['dockerfile'] = True
    else:
        _fail('Dockerfile at repo root')
        print(result.stderr[-200:] if result.stderr else '')
        results['dockerfile'] = False
except Exception as e:
    _fail('Dockerfile at repo root', str(e))
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
        _ok('inference.py at repo root')
        results['inference'] = True
    else:
        _fail('inference.py at repo root', f'checks: {checks}')
        results['inference'] = False
except Exception as e:
    _fail('inference.py at repo root', str(e))
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
        _ok('OpenEnv Reset (POST OK)')
        results['reset'] = True
    else:
        _fail('OpenEnv Reset (POST OK)')
        results['reset'] = False
except Exception as e:
    _fail('OpenEnv Reset (POST OK)', str(e))
    import traceback
    traceback.print_exc()
    results['reset'] = False

# SUMMARY
print()
print('='*70)
print('SUMMARY')
print('='*70)
for test, passed in results.items():
    status = 'PASS' if passed else 'FAIL'
    print(f'[{status}] {test}')

all_pass = all(results.values())
print()
if all_pass:
    print('[PASS] ALL 4 TESTS PASSED - READY FOR DEPLOYMENT')
    sys.exit(0)
else:
    print('[FAIL] SOME TESTS FAILED')
    sys.exit(1)
