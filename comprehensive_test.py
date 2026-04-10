#!/usr/bin/env python3
"""
Comprehensive Testing Suite for AutoDevOS OpenEnv Submission
Tests: Environment, Inference, Logging Format, Docker, Official Validation
"""
import os
import asyncio
import sys
import subprocess
import io
from contextlib import redirect_stdout

# Set environment
os.environ['OPENAI_API_KEY'] = 'sk-test'
os.environ['API_BASE_URL'] = 'https://api.openai.com/v1'
os.environ['MODEL_NAME'] = 'gpt-3.5-turbo'
os.environ['HF_TOKEN'] = 'test_hf_token'

sys.path.insert(0, 'backend')

print('='*70)
print('COMPREHENSIVE SERVER & INFERENCE TESTING')
print('='*70)
print()

tests_passed = 0
tests_total = 5

# TEST 1: OpenEnv Environment
print('[1/5] Testing OpenEnv Environment...')
try:
    from openenv_env import WebsiteGenerationEnv, ResetResponse, Action
    
    async def test_env():
        env = WebsiteGenerationEnv(task_type='simple_landing_page')
        
        # Reset
        resp = await env.reset()
        assert isinstance(resp, ResetResponse), 'Reset should return ResetResponse'
        print(f'  [OK] reset() works - task: {resp.observation.task_type}')
        
        # Step
        action = Action(
            html='<h1>Test</h1>',
            css='h1 { color: red; }',
            js='console.log("test");',
            reasoning='Test action'
        )
        step_resp = await env.step(action)
        print(f'  [OK] step() works - reward: {step_resp.reward.total_score:.2f}')
        
        # State
        state = await env.state()
        print(f'  [OK] state() works - {len(state)} fields in state')
        
        return True
    
    result = asyncio.run(test_env())
    if result:
        print('[OK] TEST 1 PASSED: OpenEnv Environment')
        tests_passed += 1
except Exception as e:
    print(f'[FAIL] TEST 1 FAILED: {e}')
    import traceback
    traceback.print_exc()

print()

# TEST 2: Inference Script Validation
print('[2/5] Testing Inference Script Validation...')
try:
    from inference import (
        validate_environment_variables,
        validate_openai_client,
        validate_logging_format
    )
    
    checks = [
        ('Environment Variables', validate_environment_variables()),
        ('OpenAI Client', validate_openai_client()),
        ('Logging Format', validate_logging_format()),
    ]
    
    all_pass = True
    for name, result in checks:
        status = 'OK' if result else 'FAIL'
        print(f'  [{status}] {name}')
        all_pass = all_pass and result
    
    if all_pass:
        print('[OK] TEST 2 PASSED: All validations pass')
        tests_passed += 1
except Exception as e:
    print(f'[FAIL] TEST 2 FAILED: {e}')

print()

# TEST 3: Logging Format (Critical for evaluation)
print('[3/5] Testing Logging Format (Critical for evaluation)...')
try:
    from inference import log_start, log_step, log_end
    
    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        log_start('test_task', 'test_env', 'test_model')
        log_step(1, 'test_action', 0.75, False, None)
        log_end(True, 1, 0.75, [0.75])
    
    output = f.getvalue()
    print('  Output:')
    for line in output.strip().split('\n'):
        print(f'    {line}')
    
    # Verify format
    has_start = '[START]' in output and 'task=test_task' in output
    has_step = '[STEP]' in output and 'step=1' in output
    has_end = '[END]' in output and 'success=true' in output
    
    print()
    print(f'  [{'OK' if has_start else 'FAIL'}] [START] format correct')
    print(f'  [{'OK' if has_step else 'FAIL'}] [STEP] format correct')
    print(f'  [{'OK' if has_end else 'FAIL'}] [END] format correct')
    
    if has_start and has_step and has_end:
        print('[OK] TEST 3 PASSED: Logging format matches spec')
        tests_passed += 1
except Exception as e:
    print(f'[FAIL] TEST 3 FAILED: {e}')

print()

# TEST 4: Docker Image
print('[4/5] Testing Docker Image...')
try:
    result = subprocess.run(
        ['docker', 'image', 'inspect', 'autodevos-test:latest'],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        print('  [OK] Docker image exists (autodevos-test:latest)')
        print('[OK] TEST 4 PASSED: Docker image ready')
        tests_passed += 1
    else:
        print('[X] Docker image not found')
except Exception as e:
    print(f'[FAIL] TEST 4 FAILED: {e}')

print()

# TEST 5: Official OpenEnv Validation
print('[5/5] Testing Official OpenEnv Validation...')
try:
    result = subprocess.run(
        ['openenv', 'validate'],
        capture_output=True,
        text=True,
        timeout=10,
        cwd='C:\\Users\\zzeel\\OneDrive\\Desktop\\AutoDevOS'
    )
    if result.returncode == 0:
        if 'Ready' in result.stdout or 'ready' in result.stdout.lower():
            print('  [OK] Official OpenEnv validation passes')
            print('[OK] TEST 5 PASSED: Official validation')
            tests_passed += 1
        else:
            print(f'  [?] Validation output: {result.stdout[:100]}')
            print('[OK] TEST 5 PASSED: Official validation (with warnings)')
            tests_passed += 1
    else:
        print(f'[FAIL] Validation failed: {result.stderr[:200]}')
except Exception as e:
    print(f'[FAIL] TEST 5 FAILED: {e}')

print()
print('='*70)
print(f'TEST RESULTS: {tests_passed}/{tests_total} PASSED')
print('='*70)

if tests_passed == tests_total:
    print('SUCCESS: All tests passed! Ready for deployment.')
    sys.exit(0)
else:
    print('Some tests failed. Review output above.')
    sys.exit(1)
