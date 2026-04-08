# QUICK REFERENCE: Essential Commands Only

Replace `YOUR-USERNAME` and `YOUR-HF-USERNAME` with your actual usernames.

---

## GITHUB PUSH (5 minutes)

```bash
cd c:\Users\zzeel\OneDrive\Desktop\AutoDevOS

# 1. Commit everything
git add .
git commit -m "AutoDevOS OpenEnv submission"

# 2. Create repo on GitHub: https://github.com/new
#    Name: autodevos-openenv
#    Copy HTTPS URL

# 3. Push to GitHub (replace URL)
git remote set-url origin https://github.com/YOUR-USERNAME/autodevos-openenv.git
git branch -M main
git push -u origin main

# Result: Code on GitHub at https://github.com/YOUR-USERNAME/autodevos-openenv
```

---

## HUGGING FACE DEPLOY (10 minutes)

```bash
# 1. Create Space on HF: https://huggingface.co/spaces
#    SDK: Docker
#    Name: autodevos-website-generation

# 2. Clone your space
git clone https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation
cd autodevos-website-generation

# 3. Copy files from local repo
cd ..
cp AutoDevOS/openenv.yaml autodevos-website-generation/
cp AutoDevOS/backend/openenv_env.py autodevos-website-generation/
cp AutoDevOS/inference.py autodevos-website-generation/
cp AutoDevOS/requirements-inference.txt autodevos-website-generation/
cp AutoDevOS/Dockerfile autodevos-website-generation/
cp AutoDevOS/.env.example autodevos-website-generation/
cp AutoDevOS/README.md autodevos-website-generation/

# 4. Enter HF space directory
cd autodevos-website-generation

# 5. Create .gitignore
echo ".env" > .gitignore
echo "__pycache__/" >> .gitignore

# 6. Push to HF
git add .
git commit -m "Initial OpenEnv submission"
git push

# 7. Add secrets in HF Settings:
#    OPENAI_API_KEY = sk-...
#    API_BASE_URL = https://api.openai.com/v1
#    MODEL_NAME = gpt-3.5-turbo

# 8. Wait 2-3 minutes for deployment
# Result: Your Space at https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation
```

---

## WINDOWS USERS (PowerShell)

```powershell
# GitHub
cd 'c:\Users\zzeel\OneDrive\Desktop\AutoDevOS'
git add .
git commit -m "AutoDevOS OpenEnv submission"
git remote set-url origin https://github.com/YOUR-USERNAME/autodevos-openenv.git
git branch -M main
git push -u origin main

# Hugging Face (after creating space on HF)
git clone https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation
cd autodevos-website-generation
Copy-Item '..\AutoDevOS\openenv.yaml' .
Copy-Item '..\AutoDevOS\backend\openenv_env.py' .
Copy-Item '..\AutoDevOS\inference.py' .
Copy-Item '..\AutoDevOS\requirements-inference.txt' .
Copy-Item '..\AutoDevOS\Dockerfile' .
Copy-Item '..\AutoDevOS\.env.example' .
Copy-Item '..\AutoDevOS\README.md' .
git add .
git commit -m "Initial OpenEnv submission"
git push
```

---

## FINAL URLS FOR SUBMISSION

GitHub: `https://github.com/YOUR-USERNAME/autodevos-openenv`

**Hugging Face (SUBMIT THIS)**: `https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation`

---

## WHAT HAPPENS AUTOMATICALLY

When you push to HF Space:
1. Docker builds automatically
2. Environment installs
3. `inference.py` runs
4. Logs display in "App" tab
5. Space goes "Running" (2-3 min)
6. Endpoint responds to HTTP requests

Done! 🚀
