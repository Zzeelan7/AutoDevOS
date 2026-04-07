"""
RL Engine for AutoDevOS - Manages strategy storage and retrieval.
Enables learning from past iterations and high-reward agent behaviors.
"""

import json
from typing import Dict, List, Tuple, Optional
from db.chromadb_client import chromadb_client


class RLEngine:
    """Reinforcement Learning engine for strategy memory."""

    def __init__(self):
        """Initialize RL engine."""
        self.chromadb_client = chromadb_client
        self.agent_types = [
            "pm", "architect", "developer", "qa",
            "security", "tech_debt", "seo", "boss"
        ]

    async def store_iteration_results(
        self,
        job_id: str,
        iteration: int,
        agent_results: Dict[str, dict],
        rewards: Dict[str, float],
    ) -> None:
        """
        Store all agent results from an iteration.
        
        Args:
            job_id: Job ID
            iteration: Iteration number
            agent_results: Dict of {agent_type: agent_output}
            rewards: Dict of {agent_type: reward_score}
        """
        for agent_type in self.agent_types:
            if agent_type not in agent_results:
                continue
            
            agent_output = agent_results[agent_type]
            reward_score = rewards.get(agent_type, 0.0)
            
            # Generate task description from context
            task_description = self._generate_task_description(agent_type, agent_output)
            
            # Convert output to string if needed
            if isinstance(agent_output, dict):
                strategy_output = json.dumps(agent_output, indent=2)
            else:
                strategy_output = str(agent_output)
            
            # Store if reward is decent (>= 5.0)
            if reward_score >= 5.0:
                await self.chromadb_client.store_strategy(
                    agent_type=agent_type,
                    task_description=task_description,
                    strategy_output=strategy_output,
                    reward_score=reward_score,
                    metadata={
                        "job_id": job_id,
                        "iteration": iteration,
                    },
                )

    async def get_high_reward_strategies(
        self,
        agent_type: str,
        task: str,
        top_k: int = 3,
    ) -> List[Tuple[str, float]]:
        """
        Get past high-reward strategies for an agent.
        
        Args:
            agent_type: Type of agent (pm, architect, etc.)
            task: Current task description
            top_k: Number of strategies to retrieve
            
        Returns:
            List of (strategy_text, reward_score) tuples
        """
        return await self.chromadb_client.get_high_reward_strategies(
            agent_type=agent_type,
            query_task=task,
            top_k=top_k,
            min_reward=7.0,  # Only high-reward strategies
        )

    async def get_agent_stats(self, agent_type: str) -> dict:
        """
        Get statistics about strategies for an agent.
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Dict with strategy count and average reward
        """
        strategies = await self.chromadb_client.list_strategies(
            agent_type=agent_type,
            limit=1000,
        )
        
        if not strategies:
            return {
                "agent_type": agent_type,
                "total_strategies": 0,
                "avg_reward": 0.0,
                "max_reward": 0.0,
            }
        
        rewards = [s["reward_score"] for s in strategies]
        
        return {
            "agent_type": agent_type,
            "total_strategies": len(strategies),
            "avg_reward": sum(rewards) / len(rewards),
            "max_reward": max(rewards),
            "min_reward": min(rewards),
        }

    async def cleanup_low_reward_strategies(self) -> dict:
        """
        Delete strategies with low rewards to save space.
        
        Returns:
            Dict with cleanup stats per agent
        """
        cleanup_stats = {}
        
        for agent_type in self.agent_types:
            deleted = await self.chromadb_client.delete_low_reward_strategies(
                agent_type=agent_type,
                threshold=5.0,
            )
            cleanup_stats[agent_type] = deleted
        
        return cleanup_stats

    def _generate_task_description(self, agent_type: str, output: dict) -> str:
        """Generate a semantic task description from agent output."""
        if agent_type == "pm":
            return "Generate product specification with target users, value proposition, key pages, and content requirements"
        elif agent_type == "architect":
            return "Design static website file structure with HTML, CSS, JavaScript organization"
        elif agent_type == "developer":
            return "Generate production-ready HTML, CSS, and JavaScript code for website"
        elif agent_type == "qa":
            return "Review generated code for bugs, accessibility, and test results"
        elif agent_type == "security":
            return "Scan code for security vulnerabilities including XSS, CSP, and insecure patterns"
        elif agent_type == "tech_debt":
            return "Identify technical debt, redundant code, and refactoring opportunities"
        elif agent_type == "seo":
            return "Analyze Lighthouse scores and provide SEO optimization recommendations"
        elif agent_type == "boss":
            return "Evaluate all agent contributions and assign performance scores"
        else:
            return f"Execute task for {agent_type} agent"


# Global RL engine instance
rl_engine = RLEngine()
