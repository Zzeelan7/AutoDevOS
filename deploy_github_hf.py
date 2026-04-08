#!/usr/bin/env python3
"""
Complete GitHub + Hugging Face Deployment Automation
Handles all steps from local repo to deployed spaces on both platforms
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional, Tuple
import sys

def run_cmd(cmd: str, check: bool = True, verbose: bool = True) -> Tuple[int, str]:
    """Run command and return exit code + output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        if verbose and result.stdout:
            print(result.stdout.strip())
        if result.returncode != 0 and result.stderr:
            print(f"[ERROR] {result.stderr[:200]}")
        if check and result.returncode != 0:
            sys.exit(1)
        return result.returncode, result.stdout
    except subprocess.TimeoutExpired:
        print("[ERROR] Command timed out")
        return 1, ""
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return 1, ""

def section(title: str) -> None:
    """Print section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")

def check_git_config() -> bool:
    """Check if git is configured."""
    section("CHECKING GIT CONFIGURATION")
    
    # Check git installation
    code, _ = run_cmd("git --version", check=False, verbose=False)
    if code != 0:
        print("[ERROR] Git not installed")
        return False
    print("[OK] Git is installed")
    
    # Check git config
    code, user = run_cmd("git config --global user.name", check=False, verbose=False)
    if code != 0 or not user.strip():
        print("[WARN] Git user.name not configured")
        print("       Run: git config --global user.name 'Your Name'")
    else:
        print(f"[OK] Git user: {user.strip()}")
    
    code, email = run_cmd("git config --global user.email", check=False, verbose=False)
    if code != 0 or not email.strip():
        print("[WARN] Git user.email not configured")
        print("       Run: git config --global user.email 'your@email.com'")
    else:
        print(f"[OK] Git email: {email.strip()}")
    
    return True

def create_gitignore() -> None:
    """Create .gitignore file."""
    section("CREATING .gitignore")
    
    gitignore_content = """# Environment
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/

# Docker
.dockerignore

# Node (if any frontend files)
node_modules/
npm-debug.log

# Generated files
_deployment_package/
*.log
"""
    
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        print("[OK] .gitignore already exists")
    else:
        gitignore_path.write_text(gitignore_content)
        print("[OK] Created .gitignore")

def init_local_git() -> bool:
    """Initialize local git repository."""
    section("INITIALIZING LOCAL GIT REPOSITORY")
    
    git_dir = Path(".git")
    if git_dir.exists():
        print("[OK] Git repository already initialized")
        return True
    
    print("Running: git init")
    code, _ = run_cmd("git init", check=False)
    if code != 0:
        print("[ERROR] Failed to initialize git repo")
        return False
    
    print("[OK] Git repository initialized")
    
    # Create .gitignore
    create_gitignore()
    
    # Add files
    print("\nRunning: git add .")
    run_cmd("git add .")
    
    # Create initial commit
    print("\nRunning: git commit")
    code, _ = run_cmd(
        'git commit -m "Initial commit: AutoDevOS OpenEnv environment submission"',
        check=False
    )
    if code != 0:
        print("[WARN] No changes to commit or other issue")
    
    return True

def create_github_instructions() -> str:
    """Generate GitHub upload instructions."""
    return """
================================================================================
  GITHUB SETUP INSTRUCTIONS
================================================================================

Follow these steps to upload your code to GitHub:

STEP 1: CREATE REPOSITORY ON GITHUB
   1. Go to: https://github.com/new
   2. Repository name: autodevos-openenv
   3. Description: OpenEnv environment for AI website generation
   4. Visibility: Public
   5. Click "Create repository"

STEP 2: GET YOUR REPOSITORY URL
   After creation, you'll see:
   
   HTTPS:  https://github.com/YOUR-USERNAME/autodevos-openenv.git
   SSH:    git@github.com:YOUR-USERNAME/autodevos-openenv.git
   
   Copy the HTTPS URL

STEP 3: PUSH TO GITHUB
   Run these commands in your AutoDevOS directory:
   
   git remote add origin https://github.com/YOUR-USERNAME/autodevos-openenv.git
   git branch -M main
   git push -u origin main
   
   (Replace YOUR-USERNAME with your actual GitHub username)

STEP 4: VERIFY
   Go to: https://github.com/YOUR-USERNAME/autodevos-openenv
   You should see all your files!

STEP 5: ADD PAT (PERSONAL ACCESS TOKEN) IF NEEDED
   If auth fails, create a Personal Access Token:
   1. GitHub Settings -> Developer settings -> Personal access tokens
   2. Generate new token
   3. Grant "repo" and "read:user" permissions
   4. Copy token
   5. When git asks for password, paste token

================================================================================
  GITHUB + HUGGING FACE AUTO-SYNC (OPTIONAL)
================================================================================

You can set up automatic deployment from GitHub to HF Spaces:

1. In your HF Space, go to Settings
2. Linked Repository: Select GitHub
3. Link with: Your GitHub repo
4. Auto sync enabled: Yes

Now when you push to GitHub, HF Space auto-deploys!

"""

def show_github_next_steps() -> None:
    """Show next steps for GitHub."""
    section("GITHUB SETUP")
    instructions = create_github_instructions()
    print(instructions)

def create_hf_space_instructions() -> str:
    """Generate HF Space instructions."""
    return """
================================================================================
  HUGGING FACE SPACE DEPLOY INSTRUCTIONS
================================================================================

STEP 1: CREATE SPACE ON HUGGING FACE
   1. Go to: https://huggingface.co/spaces
   2. Click "Create new Space"
   3. Fill in:
      - Space name: autodevos-website-generation
      - License: MIT
      - Space SDK: Docker
      - Visibility: Public
   4. Create space

STEP 2: CLONE HF SPACE
   git clone https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation
   cd autodevos-website-generation

STEP 3: COPY FILES FROM GITHUB
   Option A - From local repo with deployed GitHub:
   
   Copy these files from your local AutoDevOS folder:
   - openenv.yaml
   - backend/openenv_env.py
   - inference.py
   - requirements-inference.txt
   - Dockerfile
   - .env.example
   - README.md
   - HUGGINGFACE_DEPLOYMENT.md
   - OPENENV_SUBMISSION_CHECKLIST.md
   
   Or clone from GitHub:
   git clone https://github.com/YOUR-USERNAME/autodevos-openenv.git temp
   cp temp/{list of files above} .
   rm -rf temp

STEP 4: CONFIGURE SECRETS
   In HF Space Settings -> Secrets, add:
   
   Key: OPENAI_API_KEY
   Value: sk-... (your OpenAI API key)
   
   Key: API_BASE_URL
   Value: https://api.openai.com/v1
   
   Key: MODEL_NAME
   Value: gpt-3.5-turbo
   
   Key: HF_TOKEN
   Value: (your HF token - optional)

STEP 5: PUSH TO HF SPACE
   git add .
   git commit -m "Deploy AutoDevOS OpenEnv environment"
   git push

STEP 6: MONITOR DEPLOYMENT
   - Watch Space "App" tab
   - Should show "Running" in 2-3 minutes
   - Check logs for [START], [STEP], [END] events

STEP 7: VERIFY
   Space URL: https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation
   
   Test endpoint responds:
   curl https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation

================================================================================
  OPTIONAL: LINK GITHUB TO HF SPACE (Auto-Deploy)
================================================================================

For automatic deployment when you push to GitHub:

1. Create HF Space (step 1 above)
2. Go to Space Settings -> Linked Repository
3. Select GitHub
4. Link to: https://github.com/YOUR-USERNAME/autodevos-openenv
5. Enable "Auto sync"

Now every GitHub push triggers HF Space deployment!

"""

def show_hf_next_steps() -> None:
    """Show next steps for HF."""
    section("HUGGING FACE DEPLOYMENT")
    instructions = create_hf_space_instructions()
    print(instructions)

def create_combined_script() -> None:
    """Create a combined deployment script."""
    section("CREATING COMBINED DEPLOYMENT SCRIPT")
    
    script_content = """#!/bin/bash
# Combined GitHub + Hugging Face Deployment
# Run this script to deploy to both platforms

set -e

echo ""
echo "=================================================="
echo "  AutoDevOS -> GitHub + Hugging Face Deployment"
echo "=================================================="
echo ""

# Step 1: Verify git
echo "[1/3] Checking git configuration..."
if ! command -v git &> /dev/null; then
    echo "[ERROR] Git not installed"
    exit 1
fi
echo "[OK] Git available"

# Step 2: Upload to GitHub
echo ""
echo "[2/3] GitHub Setup"
echo "==========================================="
echo ""
echo "1. Create repo at: https://github.com/new"
echo "   - Name: autodevos-openenv"
echo "   - Click 'Create repository'"
echo ""
echo "2. Copy HTTPS URL from GitHub"
echo ""
echo "3. Run these commands:"
echo ""
echo "   git remote add origin YOUR-GITHUB-HTTPS-URL"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
read -p "Press ENTER when you've pushed to GitHub..."

# Step 3: Deploy to HF Space
echo ""
echo "[3/3] Hugging Face Space Deployment"
echo "==========================================="
echo ""
echo "1. Go to: https://huggingface.co/spaces"
echo "2. Click 'Create new Space'"
echo "3. SDK: Docker, Name: autodevos-website-generation"
echo "4. Click 'Create space'"
echo ""
echo "5. Clone your space:"
echo "   git clone https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation"
echo ""
echo "6. Copy files and push (see README for details)"
echo ""
echo "7. Add secrets in Space Settings (OPENAI_API_KEY, API_BASE_URL, MODEL_NAME)"
echo ""
read -p "Press ENTER when you've set up HF Space..."

echo ""
echo "=================================================="
echo "[SUCCESS] Deployment Instructions Complete!"
echo "=================================================="
echo ""
echo "GitHub Repo:  https://github.com/YOUR-USERNAME/autodevos-openenv"
echo "HF Space:     https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation"
echo ""
echo "Next: Submit your HF Space URL to the competition"
echo ""
"""
    
    script_path = Path("deploy_all.sh")
    script_path.write_text(script_content, encoding='utf-8')
    try:
        script_path.chmod(0o755)
    except:
        pass
    print("[OK] Created deploy_all.sh")

def create_powershell_script() -> None:
    """Create PowerShell deployment script for Windows."""
    section("CREATING WINDOWS DEPLOYMENT SCRIPT")
    
    script_content = """@echo off
REM Combined GitHub + Hugging Face Deployment (Windows)

setlocal enabledelayedexpansion

cls
echo.
echo ==================================================
echo   AutoDevOS - GitHub + Hugging Face Deployment
echo ==================================================
echo.

REM Check git
echo [1/3] Checking git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not installed
    pause
    exit /b 1
)
echo [OK] Git available
echo.

REM Step 1: GitHub
echo [2/3] GITHUB SETUP
echo ==================================================
echo.
echo 1. Create repo at: https://github.com/new
echo    - Name: autodevos-openenv
echo    - Visibility: Public
echo    - Click "Create repository"
echo.
echo 2. Copy the HTTPS URL from GitHub
echo.
echo 3. Run in PowerShell:
echo.
echo    git remote add origin YOUR-GITHUB-URL
echo    git branch -M main
echo    git push -u origin main
echo.
pause

REM Step 2: Hugging Face
echo.
echo [3/3] HUGGING FACE SPACE DEPLOYMENT
echo ==================================================
echo.
echo 1. Go to: https://huggingface.co/spaces
echo 2. Click "Create new Space"
echo     - SDK: Docker
echo     - Name: autodevos-website-generation
echo     - Visibility: Public
echo 3. Click "Create space"
echo.
echo 4. Clone your space:
echo    git clone https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation
echo.
echo 5. Copy project files into the cloned folder
echo.
echo 6. Add these secrets in Space Settings:
echo    - OPENAI_API_KEY: sk-...
echo    - API_BASE_URL: https://api.openai.com/v1
echo    - MODEL_NAME: gpt-3.5-turbo
echo.
echo 7. Push to HF:
echo    git add .
echo    git commit -m "Deploy AutoDevOS"
echo    git push
echo.
pause

cls
echo.
echo ==================================================
echo [SUCCESS] Deployment Setup Complete!
echo ==================================================
echo.
echo GitHub:  https://github.com/YOUR-USERNAME/autodevos-openenv
echo HF Space: https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
echo.
echo Next: Submit your HF Space URL to the competition
echo.
pause
"""
    
    script_path = Path("deploy_all.bat")
    script_path.write_text(script_content)
    print("[OK] Created deploy_all.bat")

def main() -> None:
    """Main deployment setup."""
    print("\n" + "=" * 70)
    print("  AUTODEVOS: GITHUB + HUGGING FACE DEPLOYMENT")
    print("=" * 70)
    
    # Check git
    if not check_git_config():
        print("\n[WARN] Git configuration incomplete")
        print("Run: git config --global user.name 'Your Name'")
        print("Run: git config --global user.email 'your@email.com'")
    
    # Initialize local git
    if not init_local_git():
        print("\n[ERROR] Failed to initialize git repository")
        sys.exit(1)
    
    # Create deployment scripts
    create_combined_script()
    create_powershell_script()
    
    # Show instructions
    section("DEPLOYMENT SUMMARY")
    print("Deployment files created successfully!")
    print("\nFiles created:")
    print("  [OK] .gitignore")
    print("  [OK] deploy_all.sh (macOS/Linux)")
    print("  [OK] deploy_all.bat (Windows)")
    print("  [OK] Local git repository initialized")
    print("\nYour project is ready for deployment to both GitHub and Hugging Face!")
    
    # Show next steps
    show_github_next_steps()
    show_hf_next_steps()
    
    print("\n" + "=" * 70)
    print("  QUICK SUMMARY")
    print("=" * 70)
    print("""
1. GitHub (Manual):
   - Create: https://github.com/new
   - Clone URL format: https://github.com/YOUR-USERNAME/autodevos-openenv.git
   - Push: git push -u origin main

2. Hugging Face (Manual):
   - Create: https://huggingface.co/spaces
   - SDK: Docker
   - Link to GitHub (optional auto-deploy)

3. Submit:
   - Your Space URL to competition organizers
   - URL format: https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation

Your code is committed locally and ready to push!
    """)

if __name__ == "__main__":
    main()
