"""Background job worker - Processes queued jobs through LangGraph pipeline"""
import asyncio
import json
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session
from pathlib import Path

from models.job import Job, Reward, SessionLocal
from db.redis_client import redis_client
from orchestration.graph import graph, AgentState


async def save_codebase_to_disk(job_id: str, codebase: dict) -> str:
    """
    Persist generated code files to disk
    
    Args:
        job_id: Unique job identifier
        codebase: Dict mapping filename -> content
        
    Returns:
        Path to saved files
    """
    # Create job-specific directory
    base_path = Path("/app/generated_sites") if os.path.exists("/app") else Path("./generated_sites")
    job_path = base_path / job_id
    job_path.mkdir(parents=True, exist_ok=True)
    
    # Write each file
    for filename, content in codebase.items():
        file_path = job_path / filename
        file_path.write_text(content, encoding='utf-8')
        print(f"  📝 Saved {filename}", flush=True)
    
    print(f"✓ Wrote {len(codebase)} files to {job_path}", flush=True)
    return str(job_path)


async def process_job(job_id: str, db: Session):
    """
    Process a single job through the complete LangGraph pipeline
    
    Args:
        job_id: Unique job identifier
        db: Database session
    """
    # Fetch job from database
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        print(f"❌ Job {job_id} not found", flush=True)
        return
    
    try:
        # Update job status to running
        job.status = "running"
        job.current_iteration = 1
        db.commit()
        
        print(f"🚀 Processing job {job_id}: {job.prompt[:50]}...", flush=True)
        sys.stdout.flush()
        
        # Emit job started event
        await redis_client.publish_event(
            job_id,
            {
                "type": "job_started",
                "agent": "worker",
                "content": "Starting AutoDevOS pipeline...",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        # Initialize state for LangGraph
        initial_state: AgentState = {
            "job_id": job_id,
            "prompt": job.prompt,
            "iteration": 1,
            "codebase": {},
            "spec": "",
            "design": {},
            "test_results": {},
            "security_report": {},
            "tech_debt_report": {},
            "seo_report": {},
            "meeting_log": [],
            "rewards": {},
            "error": None,
            "lighthouse_results": {},
            "redis_client": redis_client,
        }
        
        # Run the LangGraph pipeline
        final_state = await graph.ainvoke(initial_state)
        
        # Store results in database
        job.status = "completed"
        job.iterations = final_state.get("iteration", 1)
        job.overall_reward = sum(final_state.get("rewards", {}).values()) / 7  # Average of 7 agents
        job.codebase = final_state.get("codebase", {})
        job.meeting_log = final_state.get("meeting_log", [])
        
        # Store individual rewards
        for agent_name, score in final_state.get("rewards", {}).items():
            reward = Reward(
                job_id=job_id,
                iteration=final_state.get("iteration", 1),
                agent=agent_name,
                score=score,
            )
            db.add(reward)
        
        db.commit()
        
        # Save generated files to disk
        if job.codebase:
            saved_path = await save_codebase_to_disk(job_id, job.codebase)
            print(f"💾 Generated files saved to: {saved_path}", flush=True)
            sys.stdout.flush()
        
        # Evaluate with OpenEnv graders
        if job.codebase:
            try:
                from openenv_integration import evaluate_website
                openenv_score, openenv_metrics = await evaluate_website(job.codebase)
                
                print(f"🎯 OpenEnv Evaluation Score: {openenv_score:.2f}/1.0", flush=True)
                for metric_name, metric_value in openenv_metrics.items():
                    print(f"   - {metric_name}: {metric_value:.2f}", flush=True)
                sys.stdout.flush()
                
                # Emit OpenEnv evaluation event
                await redis_client.publish_event(
                    job_id,
                    {
                        "type": "openenv_evaluation",
                        "agent": "openenv",
                        "content": f"✓ OpenEnv Evaluation Complete: {openenv_score:.2f}/1.0",
                        "metrics": openenv_metrics,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
            except Exception as e:
                print(f"⚠️ OpenEnv evaluation failed: {e}", flush=True)
                sys.stdout.flush()
        
        # Emit job completed event
        await redis_client.publish_event(
            job_id,
            {
                "type": "job_done",
                "agent": "worker",
                "content": f"✓ Job completed. Overall reward: {job.overall_reward:.1f}/10",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        print(f"✓ Job {job_id} completed successfully", flush=True)
        sys.stdout.flush()
        
    except Exception as e:
        # Handle errors
        job.status = "failed"
        job.error_message = str(e)
        db.commit()
        
        print(f"❌ Job {job_id} failed: {e}", flush=True)
        sys.stdout.flush()
        
        await redis_client.publish_event(
            job_id,
            {
                "type": "job_error",
                "agent": "worker",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


async def job_worker_loop():
    """
    Main worker loop - continuously processes jobs from queue
    """
    print("🔄 Job worker started", flush=True)
    sys.stdout.flush()
    
    while True:
        try:
            # Try to pop next job from queue (blocking with 1s timeout)
            job_id = await redis_client.pop_job()
            
            if job_id:
                # Get fresh DB session for this job
                db = SessionLocal()
                try:
                    await process_job(job_id, db)
                finally:
                    db.close()
            else:
                # No jobs, sleep briefly before retry
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Worker error: {e}", flush=True)
            sys.stdout.flush()
            await asyncio.sleep(5)  # Back-off on error


def start_worker():
    """Start the background job worker"""
    asyncio.run(job_worker_loop())


if __name__ == "__main__":
    start_worker()
