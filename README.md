# AutoDevOS: Website Generation Environment 🚀

**Real-World OpenEnv for Training AI Agents to Build Websites**

AutoDevOS is an **OpenEnv-compliant benchmark environment** where AI agents iteratively generate and improve website code through structured feedback. The environment simulates real-world website development challenges with multi-dimensional quality evaluation.

**Real-world utility:** Directly applicable to automated web development, code generation evaluation, and reinforcement learning on structured coding tasks.

---

## Overview

### What is this?

AutoDevOS is an OpenEnv environment where:
- **Task**: Generate complete, functional websites in HTML/CSS/JavaScript
- **Agent Input**: Observation of task description, previous code, and feedback
- **Agent Output**: Improved HTML/CSS/JavaScript code
- **Reward**: Multi-dimensional score (0.0–1.0) on: code quality, performance, accessibility, design, functionality
- **Episode**: Agent iterates up to N steps to maximize reward

### Why This Problem?

Website generation is a **real-world task** that:
1. **Requires** multi-modal reasoning (design + code + functionality)
2. **Has clear quality metrics** (HTML validity, responsiveness, accessibility)
3. **Supports iteration** (agents can improve incrementally from feedback)
4. **Scales** from simple (landing pages) to complex (e-commerce)
5. **Benefits from RL/training** (agents can learn better code patterns)

This is fundamentally different from toy environments — companies actually need automated web development.

---

## Benchmark Tasks

### Task 1: Simple Landing Page (Easy)
- **Objective**: Create a simple landing page with hero section and call-to-action
- **Max Iterations**: 2
- **Target Reward**: 0.8
- **Example**: Single-page marketing site for a product

**Success Criteria**:
- Valid HTML structure with DOCTYPE, meta tags
- Responsive CSS with @media queries
- Clickable CTA button
- Accessible (semantic HTML, alt text)
- Optimized file sizes

### Task 2: Professional Portfolio Website (Medium)
- **Objective**: Create a portfolio website with projects, about, and contact sections
- **Max Iterations**: 3
- **Target Reward**: 0.85
- **Example**: Professional designer/developer portfolio

**Success Criteria**:
- Multiple semantic sections (header, nav, sections, footer)
- Project showcase with descriptions
- About section with bio
- Contact form
- Responsive mobile layout
- Accessibility features (ARIA, semantic HTML)

### Task 3: Responsive E-commerce (Hard)
- **Objective**: Build e-commerce product listing with filters and search
- **Max Iterations**: 4
- **Target Reward**: 0.9
- **Example**: Online store product page

**Success Criteria**:
- Product card grid with image, title, price
- Filter functionality (required JavaScript)
- Search capability
- Shopping interactions (add to cart)
- Fully responsive design
- High accessibility score
- Optimized performance

---

## OpenEnv Specification

### Observation Space

```python
{
  "task_id": str,                    # Task identifier
  "task_type": str,                  # Type of generation task
  "task_description": str,           # What to build
  "current_iteration": int,          # Current step (0-indexed)
  "max_iterations": int,             # Max allowed steps
  
  # Generated code so far
  "generated_html": str,             # HTML (truncated to 5000 chars)
  "generated_css": str,              # CSS (truncated to 5000 chars)  
  "generated_js": str,               # JavaScript (truncated to 5000 chars)
  
  # Feedback
  "last_reward": float,              # Previous reward (0.0-1.0)
  "last_feedback": {
    "code_quality": float,           # 0.0-1.0
    "performance": float,            # 0.0-1.0
    "accessibility": float,          # 0.0-1.0
    "design": float,                 # 0.0-1.0
    "functionality": float,          # 0.0-1.0
  },
  
  # Episode state
  "done": bool,                      # Is episode complete?
  "error_message": null|str          # Error details if step failed
}
```

### Action Space

```python
{
  "html": str,                 # Updated HTML code (max 10000 chars) - REQUIRED
  "css": str,                  # Updated CSS code (max 10000 chars)
  "js": str,                   # Updated JavaScript code (max 10000 chars)
  "reasoning": str             # Why these changes (debugging)
}
```

### Reward Structure

```python
{
  "total_score": float,              # Overall score (0.0-1.0)
  
  # Dimensional scores
  "code_quality": float,             # HTML/CSS/JS validity
  "performance": float,              # File sizes, optimization
  "accessibility": float,            # WCAG compliance, semantic HTML
  "design": float,                   # Responsiveness, UI/UX quality
  "functionality": float,            # Interactive features, completeness
  
  # Partial progress signals
  "has_valid_html": bool,            # Basic HTML structure valid
  "has_responsive_css": bool,        # Responsive design patterns present
  "has_interactivity": bool,         # JavaScript functionality
  
  # Learning signal
  "progress_delta": float            # Change from previous iteration
}
```

**Weighting**:
- Code Quality: 20%
- Performance: 20%
- Accessibility: 15%
- Design: 30% (highest weight — visual quality matters)
- Functionality: 15%

### Episode Structure

- **Reset**: Initialize environment, return task description and empty code
- **Step**: Agent submits improved code → receive observation + reward + done flag
- **Done**: Reached target reward OR max iterations
- **Max Total Reward**: 1.0 (perfect score across all dimensions)

---

## Running the Environment

### Quick Start (Docker)

```bash
# Build the Docker image
docker build -t autodevos-env .

# Run inference with OpenAI API
docker run \
  -e OPENAI_API_KEY="your-key-here" \
  -e API_BASE_URL="https://api.openai.com/v1" \
  -e MODEL_NAME="gpt-3.5-turbo" \
  autodevos-env
```

### Local Setup

#### Prerequisites
- Python 3.11+
- OpenAI API key

#### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-inference.txt

# Add backend to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

#### Running Inference

```bash
# Set environment variables
export OPENAI_API_KEY="your-key-here"
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-3.5-turbo"

# Run the baseline agent
python inference.py
```

#### Output Format

**stdout** is one JSON object per line (no extra print statements). **stderr** carries validation and debug messages.

```json
{"event": "START", "timestamp": "2026-04-12T12:00:00+00:00", "task": "all_tasks", "environment": "WebsiteGenerationEnvironment", "model": "gpt-3.5-turbo", "api_endpoint": "https://api.openai.com/v1"}
{"event": "STEP", "timestamp": "...", "step": 1, "task": "simple_landing_page", "step_in_task": 1, "action_summary": "...", "reward": 0.65, "done": false}
{"event": "END", "timestamp": "...", "success": true, "total_steps": 9, "final_score": 0.72, "reward_history": [0.45, 0.65], "average_reward": 0.55}
```

---

## Baseline Agent Performance

The provided `inference.py` uses OpenAI's GPT-3.5-turbo to generate code.

**Expected Baseline Scores** (gpt-3.5-turbo):
- Simple Landing Page: **~0.75** (easy task, usually passes)
- Portfolio Website: **~0.70** (medium complexity)
- Responsive E-commerce: **~0.60** (hard task, advanced CSS/JS needed)
- **Overall Average: ~0.68**

These scores are reproducible and should be treated as the reference baseline.

---

## Grading Methodology

### Code Quality (20%)
- HTML: DOCTYPE, meta tags, semantic elements, proper closure
- CSS: Valid selectors, responsive patterns, layout properties
- JS: Function definitions, event listeners, DOM manipulation

### Performance (20%)
- Total payload size < 20KB = 0.4 points
- CSS file < 5KB = 0.3 points
- JS file < 5KB = 0.3 points
- Code compactness (whitespace optimization) = 0.2 points

### Accessibility (15%)
- Alt text on images
- Proper heading hierarchy (h1, h2, etc.)
- Semantic HTML elements
- Form labels
- ARIA attributes

### Design (30%)
- Responsive design (@media queries) = 0.25 points
- Color scheme consistency = 0.25 points
- Structural layout quality = 0.25 points
- Typography hierarchy = 0.25 points

### Functionality (15%)
- Interactive elements (buttons, forms)
- Feature completeness
- Task-specific requirements met
- User experience

---

## Validation Checklist

Before submitting, verify:

- [ ] `openenv validate` passes
- [ ] `docker build` succeeds
- [ ] `inference.py` runs and completes
- [ ] Output includes JSON lines with `"event": "START"`, `"STEP"`, and `"END"`
- [ ] All 3+ tasks have graders returning 0.0–1.0 scores
- [ ] Baseline reproduces consistent scores
- [ ] Dockerfile runs on 2vCPU, 8GB RAM machines
- [ ] Runtime < 20 minutes for inference
- [ ] No hardcoded API keys in code
- [ ] README documents everything above

---

## Project Structure

```
AutoDevOS/
├── Dockerfile                 # Entry point for HF Space submission
├── inference.py              # Baseline agent script (REQUIRED)
├── openenv.yaml              # OpenEnv metadata (REQUIRED)
├── requirements-inference.txt # Python dependencies
├── README.md                 # This file
│
├── backend/
│   ├── openenv_env.py        # Core environment implementation
│   ├── main.py               # FastAPI routes
│   ├── requirements.txt       # Backend dependencies
│   ├── agents/               # Multi-agent orchestration
│   ├── models/               # Database schemas
│   └── orchestration/        # Job processing pipeline
│
└── frontend/
    ├── app/
    │   ├── page.tsx          # Home page
    │   ├── dashboard/        # Job dashboard
    │   └── openenv/          # Task browser
    └── components/           # React components
```

---

## Development Setup (Optional)

To work on the full AutoDevOS system locally:

```bash
# Copy environment file
cp .env.example .env

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Return to root and start with Docker Compose
docker-compose up --build
```

This starts the full stack including PostgreSQL, Redis, ChromaDB, and both frontend/backend services.

---

## API Endpoints (For Reference)

**Get Available Tasks**
```
GET /api/openenv/tasks
```

**Get Task Details**
```
GET /api/openenv/tasks/{task_id}
```

**Create Job from Task**
```
POST /api/jobs/from-task
Body: { "task_id": "simple_landing_page" }
```

**Evaluate Website**
```
POST /api/openenv/evaluate
Body: { "html": "...", "css": "...", "js": "..." }
```

---

## Key Design Decisions

1. **Multi-dimensional Rewards**: Single scalar rewards aren't enough for website generation. We provide 5 dimensional scores to help agents understand where to improve.

2. **Partial Progress Signals**: Boolean flags (has_valid_html, has_responsive_css, has_interactivity) provide early learning signals before final grading.

3. **Iterative Refinement**: Max 2–4 iterations per task encourages agents to improve incrementally rather than starting from scratch each time.

4. **Difficulty Scaling**: Tasks progress from simple (landing page) → medium (portfolio) → hard (e-commerce) to test agent capabilities across complexity levels.

5. **Reproducibility**: Grading is deterministic based on code analysis, not external services (no flaky API calls).

---

## Troubleshooting

**Q: inference.py returns 0.0 scores**
A: Check that openenv_env.py is in PYTHONPATH. Also verify OpenAI API key format.

**Q: Docker build fails**
A: Ensure requirements-inference.txt is in root directory, and backend/openenv_env.py exists.

**Q: Scores don't match baseline**
A: Model randomness may cause variation. Run multiple times and average. Environmental differences (different LLM versions) will cause score differences.

**Q: Submission rejected for "invalid openenv.yaml"**
A: Run `openenv validate` locally to debug. Check field names and structure match the spec.

---

## Citation

If you use this environment in research, please cite:

```bibtex
@software{autodevos2024,
  title={AutoDevOS: OpenEnv for Website Generation},
  author={AutoDevOS Team},
  year={2024},
  url={https://github.com/...}
}
```

---

## License

MIT License - see LICENSE file for details.

---

## Questions?

- Check [OpenEnv Documentation](https://openenv.io)
- Review example inference.py for baseline implementation
- Examine openenv.yaml for full specification details

```
Frontend (Next.js)       →→ Backend (FastAPI)  ←→ Ollama (LLM)
      ↓                        ↓ ↓ ↓               PostgreSQL
   WebSocket ←→ Redis Pub/Sub  Agents              ChromaDB
      ↓
 Real-time Dashboard    ← Sandbox (Tests) ← Generated Files
```

### Tech Stack
| Layer | Tech |
|-------|------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, LangGraph, Ollama |
| **Database** | PostgreSQL, Redis, ChromaDB |
| **Execution** | Docker (Node 20 + Chrome + Lighthouse) |
| **Deployment** | Docker Compose |

## Project Structure

```
autodevos/
├── docker-compose.yml         # 6-service orchestra
├── .env.example               # Configuration template
├── frontend/                  # Next.js app
│   ├── app/page.tsx           # Landing page (prompt input)
│   ├── app/dashboard/         # Live job dashboard
│   ├── components/            # React components
│   └── lib/                   # Hooks & utilities
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── agents/                # Agent classes (PM, Architect, etc.)
│   ├── orchestration/         # LangGraph pipeline
│   ├── models/                # SQLAlchemy models (Job, Reward)
│   ├── db/                    # Database & Redis clients
│   └── sandbox/               # Code execution environment
└── generated_sites/           # Output directory (mounted volume)
```

## Phase Status

- [x] Phase 1: Foundation (repo, Docker, DB models, FastAPI endpoints, WebSocket bridge)
- [ ] Phase 2: Core Agents & LangGraph
- [ ] Phase 3: RL Strategy Memory
- [ ] Phase 4: Frontend Dashboard
- [ ] Phase 5: Polish & Production

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `mistral` | LLM model name |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `REDIS_URL` | `redis://redis:6379` | Redis connection |
| `CHROMA_URL` | `http://chroma:8001` | ChromaDB endpoint |

## Troubleshooting

### Ollama connection failed
- Ensure `ollama serve` is running in another terminal
- Check `OLLAMA_URL` points to correct address
- Run `ollama list` to see available models

### Database connection refused
- Verify PostgreSQL is running / Docker container started
- Check `DATABASE_URL` in `.env`
- Run `docker-compose logs postgres` to see errors

### WebSocket connection fails
- Check backend is running on port 8000
- Verify `NEXT_PUBLIC_WS_URL` in `.env`
- Check browser console for connection errors

## Next Steps

1. **Phase 2**: Implement 8 agent classes + LangGraph orchestration
2. **Phase 3**: Add ChromaDB RL memory for improving agent strategies over iterations
3. **Phase 4**: Build React dashboard with real-time event streaming
4. **Phase 5**: Integrate real Lighthouse CI, error handling, and production hardening

## License

MIT
