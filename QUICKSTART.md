# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Prerequisites
```bash
# Python 3.11+
python --version

# OpenAI API key (get it at https://platform.openai.com/api-keys)
echo $OPENAI_API_KEY
```

### Step 2: Setup Python Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-inference.txt
```

### Step 3: Set Environment Variables
```bash
# Linux/Mac:
export OPENAI_API_KEY="sk-..."
export MODEL_NAME="gpt-3.5-turbo"
export API_BASE_URL="https://api.openai.com/v1"

# Windows PowerShell:
$env:OPENAI_API_KEY="sk-..."
$env:MODEL_NAME="gpt-3.5-turbo"
$env:API_BASE_URL="https://api.openai.com/v1"
```

### Step 4: Validate Environment
```bash
# Run validation test
python validate_env.py
```

### Step 5: Run Baseline Agent
```bash
# Run inference on all 3 tasks
python inference.py

# Expected output:
# [START] ...
# [STEP] step=1, reward=0.65, done=false
# [STEP] step=2, reward=0.78, done=true
# [END] success=true, score=0.78
```

---

## 🐳 Using Docker

### Option A: Build Locally
```bash
# Build image
docker build -t autodevos-env .

# Run inference
docker run \
  -e OPENAI_API_KEY="sk-..." \
  -e MODEL_NAME="gpt-3.5-turbo" \
  autodevos-env
```

### Option B: Deploy to Hugging Face Space
1. Create new Space at https://huggingface.co/spaces
2. Link your GitHub repository
3. Space auto-deploys the Dockerfile
4. Set `OPENAI_API_KEY` in Space secrets
5. Run inference via Space interface

---

## 📊 Understanding the Output

### Structured Logs
```json
{"event": "START", "timestamp": "2024-04-07T...", "task": "simple_landing_page"}
{"event": "STEP", "step": 1, "reward": 0.65, "done": false}
{"event": "STEP", "step": 2, "reward": 0.78, "done": true}
{"event": "END", "success": true, "score": 0.78}
```

### Reward Breakdown
- **total_score**: 0.0–1.0 overall quality
- **code_quality**: HTML/CSS/JS validity
- **performance**: File sizes and optimization
- **accessibility**: WCAG compliance
- **design**: Responsiveness and UI quality
- **functionality**: Interactive features

### Tasks
| Task | Difficulty | Max Steps | Target Reward |
|------|-----------|-----------|---------------|
| simple_landing_page | Easy | 2 | 0.80 |
| portfolio_website | Medium | 3 | 0.85 |
| responsive_ecommerce | Hard | 4 | 0.90 |

---

## 🔧 Troubleshooting

### ModuleNotFoundError: No module named 'openenv_env'
```bash
# Make sure backend is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
python inference.py
```

### No module named 'openai'
```bash
# Install dependencies
pip install -r requirements-inference.txt
```

### OPENAI_API_KEY not set
```bash
# Check environment variable
echo $OPENAI_API_KEY

# If empty, set it
export OPENAI_API_KEY="sk-xxxx..."
```

### Scores all 0.0
- Check that OpenAI API key is valid
- Verify model name (use gpt-3.5-turbo for testing)
- Check response format in parse_agent_response()

### Docker build fails
```bash
# Check Dockerfile is in root
ls Dockerfile

# Check requirements files exist
ls requirements-inference.txt
ls backend/openenv_env.py

# Try building with verbose output
docker build --progress=plain -t autodevos-env .
```

---

## 📚 Development

### Local Testing
```bash
# Test environment without inference
python validate_env.py

# Test inference with verbose output
PYTHONPATH=backend python inference.py 2>&1 | tee inference.log
```

### Code Structure
```
AutoDevOS/
├── inference.py              # Main inference script
├── openenv.yaml              # OpenEnv specification
├── requirements-inference.txt # Python dependencies
├── Dockerfile                # Container definition
│
└── backend/
    ├── openenv_env.py        # Core environment (Pydantic + grader)
    ├── openenv_integration.py # Original integration (full stack)
    └── ... (other backend files)
```

### Customization

**Add a new task:**
```python
# In backend/openenv_env.py
class WebsiteGenerationEnv:
    def _get_task_specs(self):
        specs = {
            ...
            "my_new_task": {
                "description": "Task description",
                "max_iterations": 3,
                "target_reward": 0.85,
                "difficulty": "medium",
            }
        }
```

**Change model:**
```bash
export MODEL_NAME="gpt-4"  # Use GPT-4 instead
python inference.py
```

**Adjust max steps:**
```python
# In inference.py
MAX_STEPS_PER_TASK = {
    "simple_landing_page": 3,  # Increased from 2
    "portfolio_website": 4,      # Increased from 3
    "responsive_ecommerce": 5,   # Increased from 4
}
```

---

## 🎯 Expected Performance

**Baseline scores** (gpt-3.5-turbo):
- simple_landing_page: ~0.75 (easy - usually passes)
- portfolio_website: ~0.70 (medium complexity)
- responsive_ecommerce: ~0.60 (hard - needs advanced CSS/JS)
- **Average: ~0.68**

Scores vary based on:
- Model temperature/randomness
- Model version (3.5-turbo vs gpt-4)
- Environmental factors
- Token generation variations

**Re-run 3+ times and average for stability.**

---

## 📖 Next Steps

1. **Read full documentation**: See [README.md](README.md)
2. **Understand environment**: See [openenv.yaml](openenv.yaml)
3. **Review inference script**: See [inference.py](inference.py)
4. **Check submission requirements**: See [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)
5. **Deploy to HF Space**: Create space at huggingface.co/spaces

---

## 🆘 Support

- **OpenEnv docs**: https://openenv.io
- **OpenAI API docs**: https://platform.openai.com/docs
- **Docker docs**: https://docs.docker.com
- **HF Spaces**: https://huggingface.co/spaces

---

**Ready to build? Let's go! 🚀**
