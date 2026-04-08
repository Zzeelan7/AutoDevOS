@echo off
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
