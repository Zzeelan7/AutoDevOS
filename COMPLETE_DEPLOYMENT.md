# COMPLETE DEPLOYMENT GUIDE: GitHub + Hugging Face

**Status**: All code ready for deployment  
**Local Git**: Initialized ✓  
**Your GitHub Username**: (Will be set by you)  
**Your HF Username**: (Will be set by you)

---

## 🚀 DEPLOYMENT SUMMARY

You have:
- ✅ OpenEnv environment (fully validated)
- ✅ 3 benchmark tasks
- ✅ Local git repository initialized
- ✅ GitHub credentials configured ($user: Zzeelan7)
- ✅ Deployment scripts created

**Next**: Push to GitHub, create HF Space, deploy there

---

## STEP 1: COMMIT ALL CHANGES LOCALLY

```bash
cd c:\Users\zzeel\OneDrive\Desktop\AutoDevOS

# Stage all files
git add .

# Commit with message
git commit -m "AutoDevOS OpenEnv environment: Full submission package with docs"

# Verify
git log -1
```

Expected output: Your commit with all files.

---

## STEP 2: CREATE GITHUB REPOSITORY

**Manual setup (one-time only):**

1. Go to: https://github.com/new
2. Create repository:
   - Name: `autodevos-openenv`
   - Description: "OpenEnv environment for AI website generation"
   - Visibility: **Public**
   - License: MIT
3. Click **Create repository**
4. **Copy the HTTPS URL** (will look like `https://github.com/YOUR-USERNAME/autodevos-openenv.git`)

---

## STEP 3: PUSH TO GITHUB

Run these commands in your AutoDevOS directory:

```bash
# Add GitHub as origin (replace with your HTTPS URL from Step 2)
git remote set-url origin https://github.com/YOUR-USERNAME/autodevos-openenv.git

# Verify remote is set
git remote -v

# Set main branch
git branch -M main

# Push all code to GitHub
git push -u origin main

# Verify on GitHub
# Go to: https://github.com/YOUR-USERNAME/autodevos-openenv
```

**Expected result**: All your files visible on GitHub

---

## STEP 4: CREATE HUGGING FACE SPACE

**Manual setup (one-time only):**

1. Go to: https://huggingface.co/spaces
2. Click **Create new Space**
3. Fill in:
   - **Space name**: `autodevos-website-generation`
   - **License**: MIT
   - **Space SDK**: Docker  ← **IMPORTANT**
   - **Visibility**: Public
4. Click **Create space**

---

## STEP 5: SETUP HUGGING FACE SPACE

**Clone your HF Space:**

```bash
# Clone (replace YOUR-HF-USERNAME with your HF account name)
git clone https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation
cd autodevos-website-generation
```

**Copy the required files:**

Do ONE of these:

### Option A: Copy from local repo (fastest)
```bash
# From the HF Space directory, copy these 9 files from your AutoDevOS folder:

xcopy ..\AutoDevOS\openenv.yaml .
xcopy ..\AutoDevOS\backend\openenv_env.py .
xcopy ..\AutoDevOS\inference.py .
xcopy ..\AutoDevOS\requirements-inference.txt .
xcopy ..\AutoDevOS\Dockerfile .
xcopy ..\AutoDevOS\.env.example .
xcopy ..\AutoDevOS\README.md .
xcopy ..\AutoDevOS\HUGGINGFACE_DEPLOYMENT.md .
xcopy ..\AutoDevOS\OPENENV_SUBMISSION_CHECKLIST.md .

# On macOS/Linux:
cp ../AutoDevOS/openenv.yaml .
cp ../AutoDevOS/backend/openenv_env.py .
cp ../AutoDevOS/inference.py .
cp ../AutoDevOS/requirements-inference.txt .
cp ../AutoDevOS/Dockerfile .
cp ../AutoDevOS/.env.example .
cp ../AutoDevOS/README.md .
cp ../AutoDevOS/HUGGINGFACE_DEPLOYMENT.md .
cp ../AutoDevOS/OPENENV_SUBMISSION_CHECKLIST.md .
```

### Option B: Clone from GitHub
```bash
# Clone your GitHub repo
git clone https://github.com/YOUR-USERNAME/autodevos-openenv.git temp

# Copy files
cp temp/openenv.yaml .
cp temp/backend/openenv_env.py .
cp temp/inference.py .
cp temp/requirements-inference.txt .
cp temp/Dockerfile .
cp temp/.env.example .
cp temp/README.md .
cp temp/HUGGINGFACE_DEPLOYMENT.md .
cp temp/OPENENV_SUBMISSION_CHECKLIST.md .

# Cleanup
rm -rf temp
```

---

## STEP 6: CREATE .gitignore (HF Space)

In the HF Space directory, create `.gitignore`:

```
.env
__pycache__/
*.pyc
.venv
.pytest_cache
*.egg-info
.DS_Store
```

---

## STEP 7: ADD HUGGING FACE SECRETS

**Go to HF Space Settings → Secrets**

Add these 4 secrets:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `sk-...` (your OpenAI key) |
| `API_BASE_URL` | `https://api.openai.com/v1` |
| `MODEL_NAME` | `gpt-3.5-turbo` |
| `HF_TOKEN` | (optional - your HF token) |

**IMPORTANT**: Don't commit `.env` file. HF reads from Settings → Secrets.

---

## STEP 8: PUSH TO HUGGING FACE

In your HF Space directory:

```bash
# Stage files
git add .

# Commit
git commit -m "Initial AutoDevOS OpenEnv environment deployment"

# Push to HF
git push
```

---

## STEP 9: MONITOR DEPLOYMENT

1. Go to your HF Space: `https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation`
2. Click **App** tab
3. Watch for "Running" status (takes 2-3 minutes)
4. Check **Logs** to see output

**Expected logs:**
```json
{"event": "START", "task": "simple_landing_page", ...}
{"event": "STEP", "step": 1, "reward": 0.45, ...}
{"event": "END", "success": true, "final_score": 0.85, ...}
```

---

## STEP 10: VERIFY ENDPOINTS

After Space is "Running":

```bash
# Test endpoint
curl https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation

# Should return HTTP 200
```

---

## STEP 11: SUBMIT TO COMPETITION

Your submission URLs:

**GitHub Repository:**
```
https://github.com/YOUR-USERNAME/autodevos-openenv
```

**Hugging Face Space (use THIS one for submission):**
```
https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation
```

---

## 📋 CHECKLIST BEFORE SUBMISSION

- [ ] Local code committed to git
- [ ] GitHub repository created and code pushed
- [ ] HF Space created and configured
- [ ] All 9 files copied to HF Space
- [ ] .gitignore created in HF Space
- [ ] 4 secrets added in HF Space Settings
- [ ] Code pushed to HF Space
- [ ] Space shows "Running" status
- [ ] Space logs show [START], [STEP], [END] events
- [ ] Endpoint responds with HTTP 200
- [ ] All scores in [0.0-1.0] range
- [ ] Ready to submit!

---

## 🆘 TROUBLESHOOTING

### Git issues

**"fatal: not a git repository"**
```bash
cd c:\Users\zzeel\OneDrive\Desktop\AutoDevOS
git status
```

**"Permission denied" when pushing**
→ Create GitHub Personal Access Token:
1. GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (repo + read:user scopes)
3. When git asks for password, paste the token

### HF Space issues

**Space won't build**
→ Check Dockerfile locally: `docker build -t test .`
→ Check Space "Build" tab for error logs

**Inference times out (> 20 min)**
→ Reduce iterations in `inference.py`
→ Use faster model: `gpt-3.5-turbo` instead of `gpt-4`

**Wrong output format**
→ All print() statements must output valid JSON only
→ Three events: START, STEP, END (exact names)
→ No debug output

---

## FINAL URLS

After all steps complete:

**GitHub:**
```
https://github.com/YOUR-USERNAME/autodevos-openenv
```

**Hugging Face Space (SUBMIT THIS):**
```
https://huggingface.co/spaces/YOUR-HF-USERNAME/autodevos-website-generation
```

---

## NEXT STEPS

1. Follow steps 1-11 above
2. Replace `YOUR-USERNAME` with your actual GitHub username
3. Replace `YOUR-HF-USERNAME` with your actual Hugging Face username
4. Submit the HF Space URL to competition organizers

**Questions?** Check:
- [HUGGINGFACE_DEPLOYMENT.md](HUGGINGFACE_DEPLOYMENT.md)
- [OPENENV_SUBMISSION_CHECKLIST.md](OPENENV_SUBMISSION_CHECKLIST.md)
- [README.md](README.md)

**You're ready!** 🚀
