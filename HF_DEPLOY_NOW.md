# HuggingFace Deployment - READY NOW

## Step 1: Create HuggingFace Space (2 minutes)

Go to: https://huggingface.co/spaces

Click: **Create new Space**

Fill in:
- **Space name**: `autodevos-website-generation`
- **Owner**: Your username
- **License**: Apache 2.0
- **Select the Space SDK**: **Docker**
- **Visibility**: Public
- **README**: Leave blank (we'll add files)

Click: **Create Space**

---

## Step 2: Set Up Repository (5 minutes)

In terminal, run these commands:

```powershell
cd "C:\Users\zzeel\OneDrive\Desktop\AutoDevOS"

# Clone your new HF Space
git clone https://huggingface.co/spaces/YOUR_HF_USERNAME/autodevos-website-generation hf-space
cd hf-space

# Copy all files from AutoDevOS to HF Space
cp -r ..\* . -Exclude .git, .venv, __pycache__, .env

# Add 4 required environment secrets
# These will be set in HF Space settings
```

---

## Step 3: Add Secrets to HF Space (2 minutes)

Go to your Space: https://huggingface.co/spaces/YOUR_HF_USERNAME/autodevos-website-generation

Click: **Settings** → **Repository secrets**

Add these 4 secrets:

| Secret Name | Value |
|---|---|
| `OPENAI_API_KEY` | Your actual OpenAI API key |
| `API_BASE_URL` | `https://api.openai.com/v1` |
| `MODEL_NAME` | `gpt-3.5-turbo` |
| `HF_TOKEN` | Your HuggingFace API token (from https://huggingface.co/settings/tokens) |

Click: **Save** for each

---

## Step 4: Deploy (3-5 minutes)

In terminal, from the `hf-space` folder:

```powershell
# Stage all files
git add .

# Commit
git commit -m "Deploy AutoDevOS to HuggingFace Spaces"

# Push to HF (will trigger automatic Docker build)
git push origin main
```

Watch the build progress at: https://huggingface.co/spaces/YOUR_HF_USERNAME/autodevos-website-generation?logs

**Build time: 3-5 minutes**

---

## Step 5: Submit (1 minute)

Once the Space shows "Running" (green), open it and verify it works.

Copy the Space URL:
```
https://huggingface.co/spaces/YOUR_HF_USERNAME/autodevos-website-generation
```

Submit to competition!

---

## Replace These Values:
- `YOUR_HF_USERNAME` → Your HuggingFace username
- `YOUR_OPENAI_API_KEY` → Your actual OpenAI API key

---

## Total Time: ~15 minutes

✅ Everything is ready. Just follow these 5 steps.
