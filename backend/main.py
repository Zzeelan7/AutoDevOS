import os
import uuid
import sys
from datetime import datetime
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import json
import asyncio
from pathlib import Path
from pydantic import BaseModel

from models.job import init_db, get_db, Job, Reward, SessionLocal
from db.redis_client import redis_client, RedisClient
from agents.base import BaseAgent
from api.strategies import router as strategies_router
from orchestration.worker import job_worker_loop
from openenv_integration import OpenEnvBenchmark, create_task_from_prompt


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class JobCreateRequest(BaseModel):
    prompt: str

class JobResponse(BaseModel):
    jobId: str
    status: str
    prompt: str | None = None
    iterations: int | None = None
    current_iteration: int | None = None
    overall_reward: float | None = None
    created_at: str | None = None
    updated_at: str | None = None
    error_message: str | None = None
    degraded: bool | None = None

class JobListResponse(BaseModel):
    jobId: str
    prompt: str
    status: str
    created_at: str
    overall_reward: float | None = None


# Global task reference
worker_task = None

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global worker_task
    print("🚀 AutoDevOS Backend Starting...", flush=True)
    sys.stdout.flush()
    
    await redis_client.connect()
    init_db()
    print("✓ Database initialized", flush=True)
    print("✓ Redis connected", flush=True)
    sys.stdout.flush()
    
    # Start background worker
    worker_task = asyncio.create_task(job_worker_loop())
    print("✓ Job worker started", flush=True)
    sys.stdout.flush()
    
    yield
    
    # Shutdown
    print("🛑 AutoDevOS Backend Shutting Down...", flush=True)
    if worker_task:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass
    await redis_client.disconnect()


# Create FastAPI app
app = FastAPI(title="AutoDevOS Backend", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include strategy routes
app.include_router(strategies_router)


# ============================================================================
# API ENDPOINTS
# ============================================================================


@app.post("/api/jobs", response_model=JobResponse)
async def create_job(request: JobCreateRequest, db: Session = Depends(get_db)):
    """
    POST /api/jobs
    Create a new job and queue it for processing
    
    Request: { prompt: str }
    Response: { jobId: str, status: str }
    """
    prompt = request.prompt.strip()
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())[:8]
    
    # Create job record
    job = Job(
        job_id=job_id,
        prompt=prompt,
        status="queued",
        iterations=3,
        current_iteration=1,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Queue job for processing
    await redis_client.push_job(job_id)
    
    # Emit initial event
    await redis_client.publish_event(
        job_id,
        {
            "type": "job_created",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    
    return JSONResponse(
        status_code=201,
        content={"jobId": job_id, "status": "queued"}
    )


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """
    GET /api/jobs/{jobId}
    Retrieve full job record
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Fetch rewards for this job
    rewards = db.query(Reward).filter(Reward.job_id == job_id).all()
    rewards_by_agent = {}
    for reward in rewards:
        if reward.iteration not in rewards_by_agent:
            rewards_by_agent[reward.iteration] = {}
        rewards_by_agent[reward.iteration][reward.agent] = reward.score
    
    return JSONResponse(
        content={
            "jobId": job.job_id,
            "prompt": job.prompt,
            "status": job.status,
            "degraded": job.status == "degraded",
            "iterations": job.iterations,
            "current_iteration": job.current_iteration,
            "overall_reward": job.overall_reward,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "rewards": rewards_by_agent,
            "error_message": job.error_message,
        }
    )


@app.get("/api/jobs")
async def list_jobs(limit: int = 10, db: Session = Depends(get_db)):
    """
    GET /api/jobs
    Retrieve last N jobs (for history display)
    """
    jobs = (
        db.query(Job)
        .order_by(Job.created_at.desc())
        .limit(limit)
        .all()
    )
    
    return JSONResponse(
        content=[
            {
                "jobId": job.job_id,
                "prompt": job.prompt[:100],  # Truncate for list view
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "overall_reward": job.overall_reward,
            }
            for job in jobs
        ]
    )


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================


@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket /ws/{jobId}
    
    Establishes real-time connection and streams events from Redis pub/sub
    Event format:
    {
      "type": "agent_log" | "meeting_start" | "meeting_message" | 
              "boss_verdict" | "reward" | "iteration_complete" | "job_done",
      "agent": agent name,
      "content": string,
      "reward": number | null,
      "timestamp": ISO string
    }
    """
    await websocket.accept()
    
    try:
        # Subscribe to job channel
        pubsub = await redis_client.subscribe(f"job:{job_id}")
        
        # Listen for messages
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            
            if message and message['type'] == 'message':
                try:
                    event = json.loads(message['data'])
                    await websocket.send_json(event)
                except json.JSONDecodeError:
                    pass
            
            # Small delay to prevent busy-waiting
            await asyncio.sleep(0.1)
    
    except Exception as e:
        print(f"WebSocket error for {job_id}: {e}")
    finally:
        await pubsub.unsubscribe(f"job:{job_id}")
        await websocket.close()



# ============================================================================
# WEBSITE SERVING ENDPOINT
# ============================================================================


@app.get("/api/jobs/{job_id}/preview")
async def get_website_preview(job_id: str, db: Session = Depends(get_db)):
    """
    GET /api/jobs/{job_id}/preview
    Retrieve the generated website HTML for preview
    """
    # Verify job exists
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Build path to generated HTML
    generated_dir = Path("/app/generated_sites") / job_id
    index_html = generated_dir / "index.html"
    
    # Check if file exists
    if not index_html.exists():
        raise HTTPException(status_code=404, detail="Website not yet generated")
    
    # Read and return HTML
    with open(index_html, 'r') as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


@app.get("/api/jobs/{job_id}/files/{file_path:path}")
async def get_website_file(job_id: str, file_path: str, db: Session = Depends(get_db)):
    """
    GET /api/jobs/{job_id}/files/{file_path}
    Retrieve specific files (CSS, JS, images) from generated website
    """
    # Verify job exists
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Prevent directory traversal attacks
    if ".." in file_path or file_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Build safe path
    generated_dir = Path("/app/generated_sites") / job_id
    file_full_path = (generated_dir / file_path).resolve()
    
    # Verify file is within the job directory
    if not str(file_full_path).startswith(str(generated_dir.resolve())):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    if not file_full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file with appropriate content type
    return FileResponse(file_full_path)


# ============================================================================
# OPENENV INTEGRATION ENDPOINTS
# ============================================================================


@app.get("/api/openenv/tasks")
async def list_openenv_tasks():
    """
    GET /api/openenv/tasks
    List all available OpenEnv benchmark tasks
    """
    tasks = OpenEnvBenchmark.list_tasks()
    return JSONResponse(content={"tasks": tasks})


@app.get("/api/openenv/tasks/{task_id}")
async def get_openenv_task(task_id: str):
    """
    GET /api/openenv/tasks/{task_id}
    Get details of a specific OpenEnv task
    """
    try:
        task = OpenEnvBenchmark.get_task(task_id)
        return JSONResponse(content={
            "task_id": task.spec.task_id,
            "description": task.spec.description,
            "prompt": task.spec.prompt,
            "difficulty": task.spec.difficulty.value,
            "constraints": task.spec.constraints,
            "criteria": task.grader.get_criteria(),
        })
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/openenv/evaluate")
async def evaluate_website_with_openenv(request: dict):
    """
    POST /api/openenv/evaluate
    Evaluate a website using OpenEnv graders
    
    Request body:
    {
        "job_id": str,
        "codebase": {
            "index.html": str,
            "style.css": str,
            "script.js": str
        }
    }
    """
    from openenv_integration import evaluate_website
    
    job_id = request.get("job_id", "")
    codebase = request.get("codebase", {})
    
    if not codebase:
        raise HTTPException(status_code=400, detail="Codebase required for evaluation")
    
    # Evaluate the website
    score, metrics = await evaluate_website(codebase)
    
    return JSONResponse(content={
        "job_id": job_id,
        "overall_score": float(score),
        "metrics": {k: float(v) for k, v in metrics.items()},
        "evaluation_timestamp": datetime.utcnow().isoformat()
    })


@app.post("/api/jobs/from-task")
async def create_job_from_openenv_task(request: dict, db: Session = Depends(get_db)):
    """
    POST /api/jobs/from-task
    Create a job from an OpenEnv benchmark task
    
    Request body:
    {
        "task_id": str  # e.g., "simple_landing_page", "portfolio_website"
    }
    """
    task_id = request.get("task_id", "").strip()
    
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id required")
    
    try:
        # Get the task template
        openenv_task = OpenEnvBenchmark.get_task(task_id)
        prompt = openenv_task.spec.prompt
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())[:8]
    
    # Create job record
    job = Job(
        job_id=job_id,
        prompt=prompt,
        status="queued",
        iterations=openenv_task.spec.constraints.get('max_iterations', 3),
        current_iteration=1,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Queue job for processing
    await redis_client.push_job(job_id)
    
    # Emit initial event with task info
    await redis_client.publish_event(
        job_id,
        {
            "type": "job_created_from_task",
            "job_id": job_id,
            "task_id": task_id,
            "task_difficulty": openenv_task.spec.difficulty.value,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    
    return JSONResponse(
        status_code=201,
        content={
            "jobId": job_id,
            "status": "queued",
            "task_id": task_id,
            "task_description": openenv_task.spec.description
        }
    )


# ============================================================================
# HEALTH CHECKS
# ============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis
        await redis_client.client.ping()
        
        # Test Database
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {"status": "healthy"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
