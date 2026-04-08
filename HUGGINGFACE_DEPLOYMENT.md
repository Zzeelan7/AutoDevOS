# AutoDevOS - Hugging Face Space Deployment Guide

## Pre-Deployment Checklist

### ✅ Phase 1: Local Validation (COMPLETED)
- [x] All imports successful
- [x] Environment instantiation working
- [x] Pydantic models valid
- [x] Async methods functional (reset(), step(), state())
- [x] 3+ tasks with graders defined
- [x] `.env.example` created
- [x] `requirements-inference.txt` configured

### 📋 Phase 2: Create Hugging Face Space (REQUIRED BEFORE DEPLOYMENT)

**Steps to create HF Space:**

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Space name**: `autodevos-website-generation` (or similar)
   - **License**: MIT
   - **Space SDK**: Docker
   - **Visibility**: Public (or Private if making private submission)
4. Click "Create space"
5. Clone the space repository locally

**Example command:**
```bash
git clone https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
cd autodevos-website-generation
```

### 📦 Phase 3: Copy Project Files to Space

Copy these files from this repository to the HF Space:

```bash
# Core environment files
cp openenv.yaml .
cp backend/openenv_env.py .
cp inference.py .
cp requirements-inference.txt .
cp Dockerfile .
cp .env.example .

# Documentation
cp README.md .
```

### 🔑 Phase 4: Set Space Secrets

In Hugging Face Space Settings → Secrets, add:

| Key | Value | Description |
|-----|-------|-------------|
| `OPENAI_API_KEY` | `sk-...` (your OpenAI key) | OpenAI API key for LLM calls |
| `API_BASE_URL` | `https://api.openai.com/v1` | OpenAI endpoint |
| `MODEL_NAME` | `gpt-3.5-turbo` or `gpt-4` | Model to use for inference |
| `HF_TOKEN` | (optional) | Your HuggingFace token |

**Security Note**: Do NOT commit `.env` file with real keys. Use Space Secrets instead.

### 🚀 Phase 5: Deploy

Option A: **Auto-Deploy from Docker** (Recommended)
1. Space automatically detects `Dockerfile`
2. Builds and deploys when you push code
3. Monitor deployment in "App" tab

Option B: **Manual Deploy**
```bash
git add .
git commit -m "Initial OpenEnv environment submission"
git push
```

Wait for the deployment to complete (monitor the "App" tab).

### ✔️ Phase 6: Verify Deployment

Once deployed, the Space should:

1. **Respond to health checks**
   ```bash
   curl https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
   ```
   Expected: HTTP 200 OK

2. **Accept reset() calls**
   ```bash
   curl -X POST https://api-inference.huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation/reset
   ```
   Expected: Returns Observation JSON

3. **Run inference**
   - The `inference.py` script should execute without errors
   - Logs should appear in [START] → [STEP] → [END] format

### 📊 Phase 7: Pre-Submission Validation

Before final submission, run this local validation:

```bash
# 1. Validate OpenEnv spec
python validate_env.py

# 2. Check Dockerfile builds
docker build -t autodevos-test .

# 3. Run Docker container (with env vars)
docker run \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e API_BASE_URL=https://api.openai.com/v1 \
  -e MODEL_NAME=gpt-3.5-turbo \
  autodevos-test

# 4. Verify inference runs and completes
python inference.py
```

Expected output: Structured logs with [START], [STEP], [END] format.

---

## Troubleshooting

### Issue: Space won't build
**Solution**: 
- Check Dockerfile syntax: `docker build -t test . --no-cache`
- Verify all COPY paths exist relative to repository root
- Check Python version compatibility (requires Python 3.11)

### Issue: Inference times out (>20 minutes)
**Solution**:
- Reduce `MAX_STEPS_PER_TASK` in `inference.py`
- Use faster model: `gpt-3.5-turbo` instead of `gpt-4`
- Check OpenAI API rate limits

### Issue: Space runs out of memory
**Solution**:
- Target machine has 2vCPU, 8GB RAM (system requirement)
- Verify `requirements-inference.txt` doesn't have bloated dependencies
- Stream outputs instead of buffering

### Issue: Logs not matching [START]/[STEP]/[END] format
**Solution**:
- Ensure all `print()` statements output valid JSON only
- No debug `print()` outside the structured log functions
- Check character encoding (UTF-8)

---

## Deployment Success Criteria

✅ Space deploys without errors  
✅ Automated ping to URL returns 200  
✅ `openenv validate` passes  
✅ `docker build` succeeds (without cache)  
✅ `inference.py` runs and completes within 20 minutes  
✅ All 3 tasks have working graders (return scores 0.0-1.0)  
✅ Logs follow [START]/[STEP]/[END] structure  
✅ Can run on 2vCPU, 8GB RAM machine  

---

## Next Steps After Deployment

1. **Test the endpoint** (see Phase 6 above)
2. **Monitor Space logs** for any runtime errors
3. **Collect baseline scores** from your deployed vs. local inference
4. **Submit to competition** with Space URL and this validation proof

**Your Space URL will look like:**
```
https://huggingface.co/spaces/YOUR-USERNAME/autodevos-website-generation
```

Include this URL in your competition submission.
