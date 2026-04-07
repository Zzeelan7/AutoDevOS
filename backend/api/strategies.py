from fastapi import APIRouter, Query
from typing import List, Dict, Any
from orchestration.rl_engine import rl_engine

router = APIRouter(prefix="/api", tags=["strategies"])


@router.get("/strategies")
async def list_all_strategies(
    job_id: str = Query(None),
    agent_type: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """
    List high-reward strategies with optional filtering.
    
    Args:
        job_id: Filter by job ID (optional)
        agent_type: Filter by agent type (pm, architect, developer, etc.)
        limit: Maximum strategies to return
    """
    try:
        strategies = []
        
        if agent_type:
            # Get strategies for specific agent type
            results = await rl_engine.get_high_reward_strategies(
                agent_type, "", top_k=limit
            )
            for output, reward in results:
                strategies.append({
                    "agent": agent_type,
                    "output": output[:200],  # Truncate for API
                    "reward": reward,
                })
        else:
            # Get all agent types
            for agent in ["pm", "architect", "developer", "qa", "security", "tech_debt", "seo", "boss"]:
                results = await rl_engine.get_high_reward_strategies(
                    agent, "", top_k=limit // 8
                )
                for output, reward in results:
                    strategies.append({
                        "agent": agent,
                        "output": output[:200],
                        "reward": reward,
                    })
        
        # Sort by reward descending
        strategies.sort(key=lambda x: x["reward"], reverse=True)
        strategies = strategies[:limit]
        
        return {
            "success": True,
            "strategies": strategies,
            "count": len(strategies),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "strategies": [],
            "count": 0,
        }


@router.get("/strategies/{agent_type}")
async def get_agent_strategies(
    agent_type: str,
    job_id: str = Query(None),
    limit: int = Query(10, ge=1, le=50),
) -> Dict[str, Any]:
    """
    Get strategies for a specific agent type.
    
    Args:
        agent_type: Agent type (pm, architect, developer, etc.)
        job_id: Filter by job ID (optional)
        limit: Maximum strategies to return
    """
    try:
        results = await rl_engine.get_high_reward_strategies(
            agent_type, "", top_k=limit
        )
        
        strategies = []
        for output, reward in results:
            strategies.append({
                "agent": agent_type,
                "output": output[:300],  # More detail for specific agent
                "reward": reward,
                "timestamp": None,  # TODO: Add timestamp to ChromaDB metadata
            })
        
        return {
            "success": True,
            "agent": agent_type,
            "strategies": strategies,
            "count": len(strategies),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "strategies": [],
            "count": 0,
        }


@router.get("/agent-stats/{agent_type}")
async def get_agent_stats(agent_type: str) -> Dict[str, Any]:
    """
    Get performance statistics for an agent.
    
    Args:
        agent_type: Agent type (pm, architect, developer, etc.)
    """
    try:
        stats = await rl_engine.get_agent_stats(agent_type)
        return {
            "success": True,
            "agent": agent_type,
            **stats,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "count": 0,
            "avg_reward": 0,
            "max_reward": 0,
        }


@router.post("/cleanup-strategies")
async def cleanup_low_reward_strategies(
    agent_type: str = Query(None),
    min_reward: float = Query(5.0),
) -> Dict[str, Any]:
    """
    Delete low-reward strategies from memory.
    
    Args:
        agent_type: Optional specific agent type. If None, cleanup all agents.
        min_reward: Minimum reward threshold (delete if below this)
    """
    try:
        if agent_type:
            await rl_engine.cleanup_low_reward_strategies(agent_type, min_reward)
            count = 1
        else:
            for agent in ["pm", "architect", "developer", "qa", "security", "tech_debt", "seo", "boss"]:
                await rl_engine.cleanup_low_reward_strategies(agent, min_reward)
            count = 8
        
        return {
            "success": True,
            "message": f"Cleaned up low-reward strategies for {count} agent(s)",
            "threshold": min_reward,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
