#!/usr/bin/env python3
"""
AutoDevOS HF Space Deployment Automation
Complete end-to-end deployment helper
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import shutil
from typing import Optional

def print_section(title: str, char: str = "=") -> None:
    """Print formatted section header."""
    width = 70
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}\n")

def run_cmd(cmd: str, quiet: bool = False) -> tuple[int, str]:
    """Run command and return exit code + output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if not quiet and result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"⚠️  {result.stderr[:200]}")
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except Exception as e:
        return 1, str(e)

def verify_files() -> bool:
    """Verify all required files exist."""
    print_section("VERIFYING FILES")
    
    required = [
        "openenv.yaml",
        "backend/openenv_env.py",
        "inference.py",
        "requirements-inference.txt",
        "Dockerfile",
        ".env.example",
        "README.md",
    ]
    
    all_exist = True
    for f in required:
        exists = Path(f).exists()
        status = "[OK]" if exists else "[MISSING]"
        print(f"  {status} {f}")
        if not exists:
            all_exist = False
    
    return all_exist

def create_deployment_package() -> bool:
    """Create a deployment package with all files."""
    print_section("PREPARING DEPLOYMENT PACKAGE")
    
    # Create deployment directory
    deploy_dir = Path("_deployment_package")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    files_to_copy = [
        "openenv.yaml",
        "backend/openenv_env.py",
        "inference.py",
        "requirements-inference.txt",
        "Dockerfile",
        ".env.example",
        "README.md",
        "DEPLOY_QUICK_START.md",
        "HUGGINGFACE_DEPLOYMENT.md",
    ]
    
    for f in files_to_copy:
        src = Path(f)
        if src.exists():
            if src.is_file():
                shutil.copy2(src, deploy_dir / src.name)
                print(f"  [OK] Copied {f}")
            elif src.is_dir():
                # For backend directory, copy the file to root level
                for file in src.glob("*.py"):
                    shutil.copy2(file, deploy_dir / file.name)
                    print(f"  [OK] Copied {file.name}")
        else:
            print(f"  [SKIP] Missing {f}")
    
    print(f"\nPackage created in: {deploy_dir}")
    print(f"Run: cd {deploy_dir} && cat DEPLOY_QUICK_START.md")
    return True

def create_git_deployment_script() -> None:
    """Create a git deployment script."""
    print_section("CREATING GIT DEPLOYMENT SCRIPT")
    
    script_content = """#!/bin/bash
# HF Space Deployment Script
# Run this AFTER you've created a space and cloned it

set -e

echo "AutoDevOS HF Space Deployment"
echo "================================"
echo ""

# Check if in HF Space directory
if [ ! -d ".git" ]; then
    echo "[ERROR] Not in a git repository!"
    echo "Clone your HF Space first:"
    echo "  git clone https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation"
    exit 1
fi

echo "[OK] Git repository detected"
echo ""

# Copy deployment files
echo "Copying files..."
if [ -f "../AutoDevOS/openenv.yaml" ]; then
    cp ../AutoDevOS/openenv.yaml .
    cp ../AutoDevOS/backend/openenv_env.py .
    cp ../AutoDevOS/inference.py .
    cp ../AutoDevOS/requirements-inference.txt .
    cp ../AutoDevOS/Dockerfile .
    cp ../AutoDevOS/.env.example .
    cp ../AutoDevOS/README.md .
    cp ../AutoDevOS/HUGGINGFACE_DEPLOYMENT.md .
    cp ../AutoDevOS/OPENENV_SUBMISSION_CHECKLIST.md .
    echo "[OK] Files copied"
else
    echo "[ERROR] Can't find AutoDevOS directory"
    echo "Make sure you're in the right location"
    exit 1
fi

echo ""
echo "Creating .gitignore..."
cat > .gitignore <<EOF
.env
__pycache__/
*.pyc
.venv
.pytest_cache
*.egg-info
.DS_Store
EOF
echo "[OK] .gitignore created"

echo ""
echo "Staging files..."
git add .
echo "[OK] Files staged"

echo ""
echo "Committing..."
git commit -m "Initial AutoDevOS OpenEnv environment submission"
echo "[OK] Committed"

echo ""
echo "Pushing to Hugging Face..."
git push
echo "[OK] Pushed!"

echo ""
echo "================================"
echo "[SUCCESS] Deployment Complete!"
echo "================================"
echo ""
echo "Your Space will build in 2-3 minutes."
echo "Monitor at: https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation"
echo ""
echo "Next: Add these secrets in Space Settings:"
echo "  - OPENAI_API_KEY: sk-..."
echo "  - API_BASE_URL: https://api.openai.com/v1"
echo "  - MODEL_NAME: gpt-3.5-turbo"
echo ""
"""
    
    script_path = Path("deploy_to_hf.sh")
    script_path.write_text(script_content, encoding='utf-8')
    script_path.chmod(0o755)
    print(f"[OK] Created deploy_to_hf.sh\n  Usage: bash deploy_to_hf.sh")

def create_windows_deployment_script() -> None:
    """Create a Windows batch deployment script."""
    print_section("CREATING WINDOWS DEPLOYMENT SCRIPT")
    
    batch_content = """@echo off
REM AutoDevOS HF Space Deployment Script (Windows)
setlocal enabledelayedexpansion

echo.
echo AutoDevOS HF Space Deployment
echo ================================
echo.

REM Check if in git repository
if not exist ".git" (
    echo [ERROR] Not in a git repository!
    echo Clone your HF Space first:
    echo   git clone https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
    exit /b 1
)

echo [OK] Git repository detected
echo.

REM Copy deployment files
echo Copying files...
if exist "..\\AutoDevOS\\openenv.yaml" (
    copy "..\\AutoDevOS\\openenv.yaml" .
    copy "..\\AutoDevOS\\backend\\openenv_env.py" .
    copy "..\\AutoDevOS\\inference.py" .
    copy "..\\AutoDevOS\\requirements-inference.txt" .
    copy "..\\AutoDevOS\\Dockerfile" .
    copy "..\\AutoDevOS\\.env.example" .
    copy "..\\AutoDevOS\\README.md" .
    copy "..\\AutoDevOS\\HUGGINGFACE_DEPLOYMENT.md" .
    copy "..\\AutoDevOS\\OPENENV_SUBMISSION_CHECKLIST.md" .
    echo [OK] Files copied
) else (
    echo [ERROR] Can't find AutoDevOS directory
    exit /b 1
)

echo.
echo Creating .gitignore...
(
    echo .env
    echo __pycache__/
    echo *.pyc
    echo .venv
    echo .pytest_cache
    echo *.egg-info
    echo .DS_Store
) > .gitignore
echo [OK] .gitignore created

echo.
echo Staging files...
git add .
echo [OK] Files staged

echo.
echo Committing...
git commit -m "Initial AutoDevOS OpenEnv environment submission"
echo [OK] Committed

echo.
echo Pushing to Hugging Face...
git push
echo [OK] Pushed!

echo.
echo ================================
echo [SUCCESS] Deployment Complete!
echo ================================
echo.
echo Your Space will build in 2-3 minutes.
echo Monitor at: https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
echo.
echo Next: Add these secrets in Space Settings:
echo   - OPENAI_API_KEY: sk-...
echo   - API_BASE_URL: https://api.openai.com/v1
echo   - MODEL_NAME: gpt-3.5-turbo
echo.
pause
"""
    
    batch_path = Path("deploy_to_hf.bat")
    batch_path.write_text(batch_content, encoding='utf-8')
    print(f"[OK] Created deploy_to_hf.bat\n  Usage: deploy_to_hf.bat (from cloned HF Space directory)")

def show_setup_instructions() -> None:
    """Show final setup instructions."""
    print_section("SETUP INSTRUCTIONS")
    
    instructions = """
STEP 1: CREATE HUGGING FACE SPACE (Manual)
   -> Go to: https://huggingface.co/spaces
   -> Click "Create new Space"
   -> Fill in:
      * Name: autodevos-website-generation
      * SDK: Docker
      * Visibility: Public
   -> Create space

STEP 2: CLONE YOUR SPACE
   $ git clone https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
   $ cd autodevos-website-generation

STEP 3: RUN DEPLOYMENT SCRIPT
   
   On macOS/Linux:
   $ bash ../AutoDevOS/deploy_to_hf.sh
   
   On Windows:
   $ cd ..\\\\autodevos-website-generation
   $ ..\\\\AutoDevOS\\\\deploy_to_hf.bat

STEP 4: ADD SECRETS IN HF SPACE SETTINGS
   Go to Settings -> Secrets and add:
   
   Key: OPENAI_API_KEY
   Value: sk-... (your OpenAI API key)
   
   Key: API_BASE_URL
   Value: https://api.openai.com/v1
   
   Key: MODEL_NAME
   Value: gpt-3.5-turbo

STEP 5: MONITOR DEPLOYMENT
   Wait 2-3 minutes for Space to build
   -> Check: https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
   -> Look for "Running" status

STEP 6: VERIFY & SUBMIT
   Your Space URL: https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
   Submit this URL to competition

"""
    print(instructions)

def main() -> None:
    """Main deployment setup."""
    print("\n" + "🚀" * 40)
    print("\n  AUTODEVOS → HUGGING FACE SPACE DEPLOYMENT SETUP")
    print("\n" + "🚀" * 40)
    
    # Verify files
    if not verify_files():
        print("\n❌ Missing required files!")
        sys.exit(1)
    
    # Create deployment package
    create_deployment_package()
    
    # Create scripts
    create_git_deployment_script()
    create_windows_deployment_script()
    
    # Show instructions
    show_setup_instructions()
    
    print("\n" + "=" * 70)
    print("✅ DEPLOYMENT SETUP COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Create space at: https://huggingface.co/spaces")
    print("  2. Clone your new space locally")
    print("  3. Run the deployment script (deploy_to_hf.sh or deploy_to_hf.bat)")
    print("  4. Add secrets in HF Space Settings")
    print("  5. Monitor deployment (2-3 minutes)")
    print("\nHave questions? Check HUGGINGFACE_DEPLOYMENT.md")
    print()

if __name__ == "__main__":
    main()
