#!/usr/bin/env python3
"""
Quick validation script: Verifies OpenEnv environment can be imported and instantiated.
Run this before submitting to catch import errors early.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from openenv_env import (  # type: ignore
            Observation,
            Action,
            Reward,
            WebsiteGenerationEnv,
        )
        print("  [OK] Pydantic models imported")
    except Exception as e:
        print(f"  [FAIL] Failed to import Pydantic models: {e}")
        return False
    
    try:
        import inference
        print("  [OK] inference.py imports")
    except ImportError as e:
        print(f"  [FAIL] Failed to import inference.py: {e}")
        return False
    
    print("[OK] All imports successful\n")
    return True


def test_environment():
    """Test that environment can be created."""
    print("Testing environment instantiation...")
    
    try:
        from openenv_env import WebsiteGenerationEnv  # type: ignore
        
        env = WebsiteGenerationEnv(task_type="simple_landing_page")
        print(f"  [OK] Environment created for task: simple_landing_page")
        
        # Check environment has required methods
        required_methods = ['reset', 'step', 'state']
        for method in required_methods:
            if not hasattr(env, method):
                print(f"  [FAIL] Environment missing method: {method}")
                return False
            else:
                print(f"  [OK] Method {method} exists")
        
    except Exception as e:
        print(f"  [FAIL] Failed to instantiate environment: {e}")
        return False
    
    print("[OK] Environment instantiation successful\n")
    return True


async def test_environment_async():
    """Test async environment methods."""
    print("Testing async methods...")
    
    try:
        from openenv_env import WebsiteGenerationEnv, Action  # type: ignore
        
        env = WebsiteGenerationEnv(task_type="simple_landing_page")
        
        # Test reset
        reset_response = await env.reset()
        print(f"  [OK] reset() returned: Observation with {len(reset_response.observation.task_description)} chars description")
        
        # Test step
        action = Action(
            html="<html><body><h1>Test</h1></body></html>",
            css="body { font-family: sans-serif; }",
            js="console.log('test');",
            reasoning="Initial submission"
        )
        step_response = await env.step(action)
        print(f"  [OK] step() returned: Reward score = {step_response.reward.total_score:.2f}")
        
        # Test state
        state = await env.state()
        print(f"  [OK] state() returned: {list(state.keys())}")
        
    except Exception as e:
        print(f"  [FAIL] Async test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("[OK] Async methods working\n")
    return True


def test_models():
    """Test Pydantic model validation."""
    print("Testing Pydantic models...")
    
    try:
        from openenv_env import Observation, Action, Reward, TaskType  # type: ignore
        
        # Test Action creation
        action = Action(
            html="<h1>Test</h1>",
            css="h1 { color: red; }",
            js="",
            reasoning="Test action"
        )
        print(f"  [OK] Action model valid")
        
        # Test Observation creation
        obs = Observation(
            task_id="simple_landing_page",
            task_type=TaskType.SIMPLE_LANDING_PAGE,
            task_description="Create a landing page",
            current_iteration=0,
            max_iterations=2,
            generated_html="",
            generated_css="",
            generated_js="",
            last_reward=0.0,
            last_feedback={},
            done=False,
        )
        print(f"  [OK] Observation model valid")
        
        # Test Reward creation
        reward = Reward(
            total_score=0.5,
            code_quality=0.5,
            performance=0.5,
            accessibility=0.5,
            design=0.5,
            functionality=0.5,
            has_valid_html=True,
            has_responsive_css=False,
            has_interactivity=False,
            progress_delta=0.0,
        )
        print(f"  [OK] Reward model valid")
        
    except Exception as e:
        print(f"  [FAIL] Model validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("[OK] Pydantic models valid\n")
    return True


async def main():
    """Run all validation tests."""
    print("=" * 60)
    print("OpenEnv Environment Validation")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_environment),
        ("Models", test_models),
        ("Async Methods", test_environment_async),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            if test_name == "Async Methods":
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"[FAIL] {test_name} test failed: {e}")
            results[test_name] = False
    
    print("=" * 60)
    print("Validation Results")
    print("=" * 60)
    for test_name, result in results.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {test_name}")
    
    print()
    all_pass = all(results.values())
    if all_pass:
        print("[OK] All validation tests passed! Ready for submission.")
        return 0
    else:
        print("[FAIL] Some tests failed. Please fix issues before submitting.")
        return 1


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
