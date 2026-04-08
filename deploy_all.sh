#!/bin/bash
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
