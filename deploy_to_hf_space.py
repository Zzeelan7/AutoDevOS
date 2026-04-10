#!/usr/bin/env python3
"""
Deploy AutoDevOS to HuggingFace Spaces - Complete Setup
Handles: cloning Space, copying files, configuring everything needed
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

USERNAME = "Zzeelan7"  # CHANGE THIS TO YOUR HF USERNAME
SPACE_NAME = "autodevos-website-generation"
SPACE_URL = f"https://huggingface.co/spaces/{USERNAME}/{SPACE_NAME}"
HF_SPACE_PATH = Path("./hf-autodevos-space")

def run_cmd(cmd, desc=""):
    """Run command and report status."""
    print(f"\n[*] {desc}")
    print(f"    Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[X] ERROR: {result.stderr}")
        return False
    print(f"[OK] Success")
    return True

def main():
    print("="*70)
    print("HuggingFace Spaces Deployment - AutoDevOS")
    print("="*70)
    
    # Step 1: Remove old space dir if exists
    if HF_SPACE_PATH.exists():
        print(f"\n[*] Removing existing Space directory...")
        shutil.rmtree(HF_SPACE_PATH)
        print("[✓] Removed")
    
    # Step 2: Clone HF Space
    clone_url = f"https://huggingface.co/spaces/{USERNAME}/{SPACE_NAME}"
    if not run_cmd(f"git clone {clone_url} {HF_SPACE_PATH}", "Cloning HuggingFace Space"):
        print("[✗] Failed to clone Space. Check username and Space name.")
        return False
    
    # Step 3: Copy key files
    print("\n[*] Copying AutoDevOS files to Space...")
    files_to_copy = [
        "Dockerfile",
        "requirements-inference.txt",
        "inference.py",
        "openenv.yaml",
        ".env.example",
        "backend",
        "validate_env.py",
    ]
    
    for file in files_to_copy:
        src = Path(file)
        dst = HF_SPACE_PATH / file
        
        if not src.exists():
            print(f"[!] Warning: {file} not found")
            continue
        
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        
        print(f"[✓] Copied {file}")
    
    # Step 4: Create app.py for HF (wrapper around inference)
    app_py = HF_SPACE_PATH / "app.py"
    if not app_py.exists():
        print("\n[*] Creating app.py wrapper for HuggingFace...")
        app_content = """#!/usr/bin/env python3
import asyncio
import os
import sys
sys.path.insert(0, '/app/backend')
sys.path.insert(0, '/app')

from inference import validate_environment_variables, validate_openai_client, validate_logging_format

# Validate on startup
print("[STARTUP] Validating requirements...")
if not validate_environment_variables():
    print("[ERROR] REQUIREMENT 1 FAILED: Missing environment variables")
    sys.exit(1)
print("[STARTUP] [OK] REQUIREMENT 1: Environment variables set")

if not validate_openai_client():
    print("[ERROR] REQUIREMENT 2 FAILED: OpenAI client not configured")
    sys.exit(1)
print("[STARTUP] [OK] REQUIREMENT 2: OpenAI client ready")

if not validate_logging_format():
    print("[ERROR] REQUIREMENT 3 FAILED: Logging format invalid")
    sys.exit(1)
print("[STARTUP] [OK] REQUIREMENT 3: Logging format valid")

print("[STARTUP] [OK] All validations passed - Space ready")
print("[STARTUP] Inference available at: /app/inference.py")
"""
        app_py.write_text(app_content)
        print("[OK] Created app.py")
    
    # Step 5: Commit and push
    os.chdir(HF_SPACE_PATH)
    
    if not run_cmd("git add .", "Staging all files"):
        return False
    
    if not run_cmd('git commit -m "Deploy AutoDevOS to HuggingFace Spaces"', "Committing files"):
        return False
    
    if not run_cmd("git push origin main", "Pushing to HuggingFace (starts Docker build)"):
        return False
    
    # Summary
    print("\n" + "="*70)
    print("DEPLOYMENT COMPLETE")
    print("="*70)
    print(f"\n[✓] Space deployed! Watch build progress at:")
    print(f"    {SPACE_URL}?logs")
    print(f"\n[*] Build time: ~5 minutes")
    print(f"[*] Once complete, your Space will be live at:")
    print(f"    {SPACE_URL}")
    print("\n[*] Required secrets to set in HF Space Settings:")
    print("    - OPENAI_API_KEY: Your actual OpenAI API key")
    print("    - API_BASE_URL: https://api.openai.com/v1")
    print("    - MODEL_NAME: gpt-3.5-turbo")
    print("    - HF_TOKEN: Your HF API token")
    print("\n[✓] Read the Space logs to debug any issues")
    print("="*70)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[✗] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
