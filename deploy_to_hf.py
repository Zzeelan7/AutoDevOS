#!/usr/bin/env python3
"""
Hugging Face Space Deployment Helper

This script helps you:
1. Prepare files for HF Space
2. Verify local Docker builds
3. Generate deployment commands
4. Test the deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_command(cmd: str, description: str = "") -> Tuple[int, str, str]:
    """Run a command and capture output."""
    if description:
        print(f"→ {description}...")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_prerequisites() -> bool:
    """Verify that required tools are installed."""
    print_header("CHECKING PREREQUISITES")
    
    required_tools = {
        "python": "python --version",
        "docker": "docker --version",
        "git": "git --version",
    }
    
    all_ok = True
    for tool, cmd in required_tools.items():
        returncode, stdout, stderr = run_command(cmd)
        if returncode == 0:
            version = stdout.strip() or stderr.strip()
            print(f"  ✓ {tool:15} {version[:50]}")
        else:
            print(f"  ✗ {tool:15} NOT FOUND")
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Some required tools are missing. Please install them:")
        print("  - Python 3.11+ from python.org")
        print("  - Docker Desktop from docker.com")
        print("  - Git from git-scm.com")
        return False
    
    return True


def validate_local_env() -> bool:
    """Validate the local environment setup."""
    print_header("VALIDATING LOCAL ENVIRONMENT")
    
    required_files = [
        "openenv.yaml",
        "backend/openenv_env.py",
        "inference.py",
        "requirements-inference.txt",
        "Dockerfile",
        ".env.example",
        "README.md",
    ]
    
    all_exist = True
    for filepath in required_files:
        if Path(filepath).exists():
            size = Path(filepath).stat().st_size
            print(f"  ✓ {filepath:40} ({size:,} bytes)")
        else:
            print(f"  ✗ {filepath:40} NOT FOUND")
            all_exist = False
    
    return all_exist


def test_python_syntax() -> bool:
    """Test Python file syntax."""
    print_header("VALIDATING PYTHON SYNTAX")
    
    python_files = [
        "backend/openenv_env.py",
        "inference.py",
    ]
    
    all_valid = True
    for filepath in python_files:
        returncode, _, stderr = run_command(
            f"python -m py_compile {filepath}",
            f"Checking {filepath}"
        )
        if returncode == 0:
            print(f"  ✓ {filepath:40} Syntax OK")
        else:
            print(f"  ✗ {filepath:40} Syntax Error")
            if stderr:
                print(f"     {stderr[:100]}")
            all_valid = False
    
    return all_valid


def test_docker_build() -> bool:
    """Test if Docker image builds successfully."""
    print_header("TESTING DOCKER BUILD")
    
    print("  Building Docker image (this may take 1-2 minutes)...")
    returncode, stdout, stderr = run_command(
        "docker build -t autodevos-test:latest . --no-cache",
        "Building Docker image"
    )
    
    if returncode == 0:
        print("  ✓ Docker build successful")
        
        # Get image size
        returncode, stdout, _ = run_command(
            'docker image inspect autodevos-test:latest --format="{{.Size}}"'
        )
        if returncode == 0:
            try:
                size_bytes = int(stdout.strip())
                size_mb = size_bytes / (1024 * 1024)
                print(f"  ✓ Image size: {size_mb:.1f} MB")
            except:
                pass
        
        return True
    else:
        print("  ✗ Docker build failed")
        if stderr:
            print(f"\n{stderr[-500:]}")  # Last 500 chars of error
        return False


def generate_deployment_guide() -> str:
    """Generate step-by-step deployment instructions."""
    return """
DEPLOYMENT STEPS:

1. CREATE HUGGING FACE SPACE:
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Enter:
     * Space name: autodevos-website-generation
     * Space SDK: Docker
     * Visibility: Public
   - Click "Create space"

2. CLONE THE SPACE:
   git clone https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
   cd autodevos-website-generation

3. COPY PROJECT FILES:
   cp ../AutoDevOS/openenv.yaml .
   cp ../AutoDevOS/backend/openenv_env.py .
   cp ../AutoDevOS/inference.py .
   cp ../AutoDevOS/requirements-inference.txt .
   cp ../AutoDevOS/Dockerfile .
   cp ../AutoDevOS/.env.example .
   cp ../AutoDevOS/README.md .
   cp ../AutoDevOS/HUGGINGFACE_DEPLOYMENT.md .

4. SET SECRETS IN HF SPACE SETTINGS:
   Go to Settings → Secrets and add:
   - OPENAI_API_KEY: (your OpenAI key)
   - API_BASE_URL: https://api.openai.com/v1
   - MODEL_NAME: gpt-3.5-turbo
   - HF_TOKEN: (optional)

5. COMMIT AND PUSH:
   git add .
   git commit -m "Initial OpenEnv environment submission"
   git push

6. VERIFY DEPLOYMENT:
   - Wait 2-3 minutes for Space to deploy
   - Check Space URL: https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
   - Verify "App" section shows "Running" status
"""


def show_next_steps() -> None:
    """Display next steps after validation."""
    print_header("✅ VALIDATION COMPLETE - READY FOR DEPLOYMENT")
    
    print("""
Your AutoDevOS OpenEnv environment is ready for Hugging Face deployment!

NEXT STEPS:

1. Create HF Space:
   → https://huggingface.co/spaces → "Create new Space"
   → Select "Docker" and name it "autodevos-website-generation"

2. Prepare files (see HUGGINGFACE_DEPLOYMENT.md for detailed steps):
   → Copy 7 files to the Space repository
   → Commit and push

3. Configure Secrets in HF Space Settings:
   → OPENAI_API_KEY
   → API_BASE_URL
   → MODEL_NAME
   → HF_TOKEN (optional)

4. Monitor deployment (watch the App tab)

5. Test endpoint after deployment completed

6. Submit to competition with Space URL

For detailed instructions, see: HUGGINGFACE_DEPLOYMENT.md

Questions? Check:
- README.md for environment overview
- OPENENV_SUBMISSION_CHECKLIST.md for submission requirements
    """)


def main() -> None:
    """Main validation workflow."""
    print("\n" + "🚀" * 35)
    print("  AUTODEVOS - HUGGING FACE SPACE DEPLOYMENT VALIDATOR")
    print("🚀" * 35)
    
    # Run validation checks
    checks = [
        ("Checking prerequisites", check_prerequisites()),
        ("Validating project files", validate_local_env()),
        ("Validating Python syntax", test_python_syntax()),
        ("Testing Docker build", test_docker_build()),
    ]
    
    print_header("VALIDATION SUMMARY")
    
    all_passed = True
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status:10} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        show_next_steps()
    else:
        print_header("⚠️  VALIDATION FAILED")
        print("""
Please fix the issues above before deploying to Hugging Face.

Common issues:
- Missing files: Run from project root directory
- Docker not installed: Install Docker Desktop
- Python import errors: Run 'pip install -r requirements-inference.txt'
        """)
        sys.exit(1)


if __name__ == "__main__":
    main()
