@echo off
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
if exist "..\AutoDevOS\openenv.yaml" (
    copy "..\AutoDevOS\openenv.yaml" .
    copy "..\AutoDevOS\backend\openenv_env.py" .
    copy "..\AutoDevOS\inference.py" .
    copy "..\AutoDevOS\requirements-inference.txt" .
    copy "..\AutoDevOS\Dockerfile" .
    copy "..\AutoDevOS\.env.example" .
    copy "..\AutoDevOS\README.md" .
    copy "..\AutoDevOS\HUGGINGFACE_DEPLOYMENT.md" .
    copy "..\AutoDevOS\OPENENV_SUBMISSION_CHECKLIST.md" .
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
