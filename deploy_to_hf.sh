#!/bin/bash
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
