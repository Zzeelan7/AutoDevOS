# ⚡ QUICK START: Deploy to Hugging Face in 5 Minutes

**Copy-paste each command in order:**

## 1. Create Space (Manual - 1 minute)
```
Go to: https://huggingface.co/spaces
Click: "Create new Space"

Fields:
- Name: autodevos-website-generation
- License: MIT
- SDK: Docker
- Visibility: Public

Click: "Create space"
```

## 2. Clone Space Repository
```bash
git clone https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
cd autodevos-website-generation
```

## 3. Copy Required Files
```bash
# From your AutoDevOS directory, copy these files:
cp openenv.yaml .
cp backend/openenv_env.py .
cp inference.py .
cp requirements-inference.txt .
cp Dockerfile .
cp .env.example .
cp README.md .
cp HUGGINGFACE_DEPLOYMENT.md .
```

## 4. Add GitHub Secrets (In HF Space Settings)
Go to: **Settings → Secrets**

Add these 4 secrets:

```
KEY: OPENAI_API_KEY
VALUE: sk-... (your OpenAI API key)

KEY: API_BASE_URL
VALUE: https://api.openai.com/v1

KEY: MODEL_NAME
VALUE: gpt-3.5-turbo

KEY: HF_TOKEN
VALUE: (leave empty for now, optional)
```

## 5. Commit & Push
```bash
git add .
git commit -m "Initial OpenEnv environment submission"
git push
```

## 6. Wait for Deployment
- Go to your Space URL
- Watch the "App" tab
- Should show "Running" in 2-3 minutes
- Green checkmark means success ✅

## 7. Verify It Works
```bash
# Test endpoint responds
curl https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation

# Should return HTTP 200 ✓
```

---

## 🎯 Your Space URL
```
https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
```

**Use this URL when submitting to competition.**

---

## ✅ What Happens During Deployment

HF will automatically:
1. Read your Dockerfile ✓
2. Build Docker image ✓
3. Install requirements ✓
4. Start the container ✓
5. Run `python inference.py` ✓
6. Stream output to Space logs ✓

You'll see logs like:
```json
{"event": "START", "task": "simple_landing_page", ...}
{"event": "STEP", "step": 1, "reward": 0.45, ...}
{"event": "END", "success": true, "final_score": 0.85, ...}
```

---

## 🆘 If Something Goes Wrong

**Space won't build?**
1. Check Dockerfile locally: `docker build -t test .`
2. Verify file paths are correct
3. Check Space build logs in "Build" tab

**Inference times out?**
1. Check if OPENAI_API_KEY is set correctly in Secrets
2. Try with different model: `gpt-3.5-turbo`
3. Reduce iterations in `inference.py`

**Scripts won't start?**
1. Check Requirements: `pip install -r requirements-inference.txt`
2. Verify Python syntax: `python -m py_compile inference.py`
3. Check Space build logs for errors

**Questions?** See HUGGINGFACE_DEPLOYMENT.md for detailed troubleshooting

---

## 📋 Submission Requirements Met

✅ Environment deploys  
✅ 3+ tasks with graders  
✅ Dockerfile builds  
✅ Baseline script runs  
✅ OpenEnv spec compliant  
✅ Output format correct  
✅ Runs in < 20 minutes  
✅ Works on 2vCPU, 8GB RAM  

**Ready to submit!** 🚀
