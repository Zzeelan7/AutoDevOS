#!/usr/bin/env python3
"""
OpenEnv Server for AutoDevOS Website Generation Environment
FastAPI-based server for hosting the RL environment
"""
import os
import sys
from pathlib import Path
import asyncio

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import your environment
from openenv_env import WebsiteGenerationEnv, Observation, Action, Reward
from llm_generator import generate_production_code

# Create FastAPI app
app = FastAPI(
    title="AutoDevOS Environment Server",
    description="FastAPI server for AutoDevOS OpenEnv environment"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize environment
env_instance = None

@app.on_event("startup")
async def startup_event():
    """Initialize environment on startup"""
    global env_instance
    env_instance = WebsiteGenerationEnv(task_type='simple_landing_page')
    print("[Server] Environment initialized")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "AutoDevOS Environment Server"}

@app.post("/reset")
async def reset_env():
    """Reset the environment"""
    if env_instance is None:
        raise HTTPException(status_code=503, detail="Environment not initialized")
    try:
        import asyncio
        result = await env_instance.reset()
        return {
            "status": "success",
            "observation": result.observation.dict(),
            "info": result.info if hasattr(result, 'info') else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step_env(action_data: dict):
    """Take a step in the environment"""
    if env_instance is None:
        raise HTTPException(status_code=503, detail="Environment not initialized")
    try:
        import asyncio
        action = Action(**action_data)
        result = await env_instance.step(action)
        return {
            "status": "success",
            "observation": result.observation.dict(),
            "reward": result.reward.dict(),
            "done": result.done,
            "info": result.info if hasattr(result, 'info') else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def get_state():
    """Get current environment state"""
    if env_instance is None:
        raise HTTPException(status_code=503, detail="Environment not initialized")
    try:
        import asyncio
        state = await env_instance.state()
        return {"status": "success", "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API endpoints for job history and creation
jobs_storage = {}

@app.get("/api/jobs")
async def get_jobs(limit: int = 10):
    """Get list of jobs"""
    jobs_list = list(jobs_storage.values())
    return jobs_list[-limit:]

@app.post("/api/jobs")
async def create_job(data: dict):
    """Create a new job"""
    import uuid
    from datetime import datetime
    
    job_id = str(uuid.uuid4())
    job = {
        "jobId": job_id,
        "prompt": data.get("prompt", ""),
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "overall_reward": 0.0,
        "steps": 0,
        "error": None
    }
    jobs_storage[job_id] = job
    
    return job

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get a specific job"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs_storage[job_id]

@app.get("/api/jobs/{job_id}/preview")
async def get_job_preview(job_id: str):
    """Get preview/output for a job"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_storage[job_id]
    
    # Retrieve generated files
    html_content = job.get("generated_html", "")
    css_content = job.get("generated_css", "")
    js_content = job.get("generated_js", "")
    
    if not html_content:
        # Fallback if not stored yet
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Site</title>
    <style>{css_content or "body { background: #f0f0f0; font-family: system-ui; margin: 0; padding: 20px; }"}</style>
</head>
<body>
    <h1>Website Generation in Progress</h1>
    <p>Status: {job.get('status', 'processing')}</p>
    <p>Reward: {job.get('overall_reward', 0):.2f}/10</p>
    <script>{js_content or ""}</script>
</body>
</html>"""
    
    return {
        "html": html_content,
        "css": css_content,
        "js": js_content,
        "status": job.get("status"),
        "reward": job.get("overall_reward", 0),
        "steps": job.get("steps", 0)
    }

@app.get("/preview/{job_id}")
async def preview_page(job_id: str):
    """Get preview page HTML iframe"""
    from fastapi.responses import HTMLResponse
    
    if job_id not in jobs_storage:
        return HTMLResponse("<html><body><p>Job not found</p></body></html>", status_code=404)
    
    job = jobs_storage[job_id]
    
    # Get generated code
    html_content = job.get("generated_html", "")
    css_content = job.get("generated_css", "")
    js_content = job.get("generated_js", "")
    
    # If no generated code, show status message
    if not html_content:
        return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generation in Progress</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background: #f0f0f0;
        }}
        .message {{
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; margin-top: 0; }}
        p {{ color: #666; }}
    </style>
</head>
<body>
    <div class="message">
        <h1>Website Generation in Progress</h1>
        <p>Status: {job.get('status', 'processing')}</p>
        <p>Reward: {job.get('overall_reward', 0):.2f}/10</p>
    </div>
</body>
</html>""")
    
    # Combine HTML with CSS and JS
    if "<style>" not in html_content and css_content:
        # Insert CSS into head if not already present
        html_content = html_content.replace("</head>", f"<style>{css_content}</style></head>", 1)
    elif "<style>" not in html_content and not css_content:
        # Add default style if no CSS
        html_content = html_content.replace("</head>", "<style>body { margin: 0; padding: 0; }</style></head>", 1)
    
    if js_content and "<script>" not in html_content:
        # Append JS at end of body
        html_content = html_content.replace("</body>", f"<script>{js_content}</script></body>", 1)
    
    return HTMLResponse(html_content)

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for job progress updates"""
    if job_id not in jobs_storage:
        await websocket.close(code=1008, reason="Job not found")
        return
    
    job = jobs_storage[job_id]
    
    # Prevent multiple processing attempts for same job
    if job.get("processing"):
        await websocket.accept()
        await websocket.send_json({
            "type": "event",
            "message": "Job already processing, reconnected to stream"
        })
        # Just stream updates without reprocessing
        while True:
            await asyncio.sleep(0.5)
            if job.get("status") in ["completed", "error"]:
                await websocket.send_json({
                    "type": "complete" if job["status"] == "completed" else "error",
                    "job": job,
                    "message": job.get("error", "") if job["status"] == "error" else None
                })
                break
        return
    
    # Mark job as processing
    job["processing"] = True
    
    await websocket.accept()
    
    try:
        # Send initial job state
        await websocket.send_json({
            "type": "init",
            "job": job
        })
        
        # Process the job
        if env_instance is None:
            await websocket.send_json({
                "type": "error",
                "message": "Environment not initialized"
            })
            job["status"] = "error"
            job["error"] = "Environment not initialized"
            await websocket.close()
            return
        
        try:
            # STEP 1: Generate code from prompt using LLM
            await websocket.send_json({
                "type": "event",
                "message": "Generating code from prompt..."
            })
            
            try:
                generated_code = await generate_production_code(job["prompt"])
            except RuntimeError as llm_error:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Code generation failed: {str(llm_error)}"
                })
                job["status"] = "error"
                job["error"] = f"LLM generation failed: {str(llm_error)}"
                await websocket.close()
                return
            
            await websocket.send_json({
                "type": "event",
                "message": "Code generation complete",
                "code_stats": {
                    "html_chars": len(generated_code.get("html", "")),
                    "css_chars": len(generated_code.get("css", "")),
                    "js_chars": len(generated_code.get("js", ""))
                }
            })
            
            # STEP 2: Reset environment
            reset_resp = await env_instance.reset()
            await websocket.send_json({
                "type": "event",
                "message": "Environment reset"
            })
            
            # STEP 3: Create action with generated code
            action = Action(
                html=generated_code.get("html", ""),
                css=generated_code.get("css", ""),
                js=generated_code.get("js", ""),
                reasoning="Generated from LLM based on prompt"
            )
            
            # STEP 4: Evaluate generated code
            step_resp = await env_instance.step(action)
            
            await websocket.send_json({
                "type": "event",
                "message": "Code evaluated by environment",
                "evaluation": {
                    "code_quality": float(step_resp.reward.code_quality),
                    "performance": float(step_resp.reward.performance),
                    "accessibility": float(step_resp.reward.accessibility),
                    "design": float(step_resp.reward.design),
                    "functionality": float(step_resp.reward.functionality),
                }
            })
            
            # STEP 5: Update job with generated content
            job["status"] = "completed"
            job["steps"] = 1
            job["overall_reward"] = float(step_resp.reward.total_score) if hasattr(step_resp.reward, 'total_score') else 0.0
            
            # Store generated files
            job["generated_html"] = generated_code.get("html", "")
            job["generated_css"] = generated_code.get("css", "")
            job["generated_js"] = generated_code.get("js", "")
            job["evaluation"] = {
                "code_quality": float(step_resp.reward.code_quality),
                "performance": float(step_resp.reward.performance),
                "accessibility": float(step_resp.reward.accessibility),
                "design": float(step_resp.reward.design),
                "functionality": float(step_resp.reward.functionality),
            }
            
            await websocket.send_json({
                "type": "complete",
                "job": job
            })
            
        except Exception as e:
            job["status"] = "error"
            job["error"] = str(e)
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        finally:
            # Mark job as no longer processing if it was processing
            if job.get("processing"):
                job["processing"] = False
        
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Final cleanup
        if job_id in jobs_storage:
            jobs_storage[job_id]["processing"] = False
        try:
            await websocket.close()
        except:
            pass

@app.get("/api/openenv/tasks")
async def get_tasks():
    """Get available tasks"""
    return {
        "tasks": [
            {"name": "simple_landing_page", "description": "Create a simple landing page"},
            {"name": "portfolio_website", "description": "Create a portfolio website"},
            {"name": "responsive_ecommerce", "description": "Create a responsive ecommerce site"}
        ]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AutoDevOS Environment Server",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "reset": "/reset",
            "step": "/step",
            "state": "/state"
        }
    }

def main():
    """Main entry point for the server"""
    import uvicorn
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()

def main():
    """Main entry point for OpenEnv server"""
    import uvicorn
    print("[Server] Starting AutoDevOS Environment Server...")
    print("[Server] Backend: http://0.0.0.0:8000")
    print("[Server] Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
