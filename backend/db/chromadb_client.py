"""
ChromaDB client for semantic strategy retrieval.
Stores high-reward agent strategies as vector embeddings.
"""

import json
from typing import List, Tuple, Optional
import chromadb


class ChromaDBClient:
    """Client for ChromaDB vector store."""

    def __init__(self, persist_dir: str = "/app/chroma_data"):
        """
        Initialize ChromaDB client using new API.
        
        Args:
            persist_dir: Directory for persistent storage
        """
        # Use new ChromaDB persistent client
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Create or get collection for storing strategies
        # Collection name format: "{agent_type}_strategies"
        self.strategy_collections = {}

    def _get_or_create_collection(self, agent_type: str) -> chromadb.Collection:
        """Get or create a collection for a specific agent type."""
        collection_name = f"{agent_type}_strategies"
        
        if collection_name not in self.strategy_collections:
            try:
                collection = self.client.get_collection(name=collection_name)
            except:
                # Collection doesn't exist, create it
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
            
            self.strategy_collections[collection_name] = collection
        
        return self.strategy_collections[collection_name]

    async def store_strategy(
        self,
        agent_type: str,
        task_description: str,
        strategy_output: str,
        reward_score: float,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Store a high-reward strategy in ChromaDB.
        
        Args:
            agent_type: Type of agent (pm, architect, developer, etc.)
            task_description: What the agent was asked to do
            strategy_output: The agent's response/strategy
            reward_score: Score given (0-10)
            metadata: Additional metadata dict
            
        Returns:
            strategy_id: ID of stored strategy
        """
        collection = self._get_or_create_collection(agent_type)
        
        # Generate ID from hash of task + timestamp
        import hashlib
        import time
        strategy_id = hashlib.md5(
            f"{agent_type}_{task_description}_{time.time()}".encode()
        ).hexdigest()[:12]
        
        # Prepare metadata
        meta = {
            "agent_type": agent_type,
            "reward_score": float(reward_score),
            "task_length": len(task_description),
            "output_length": len(strategy_output),
        }
        if metadata:
            meta.update(metadata)
        
        # Store in ChromaDB (uses embedding model automatically)
        # Document combines task + output for semantic search
        document = f"Task: {task_description}\n\nStrategy: {strategy_output}"
        
        collection.add(
            ids=[strategy_id],
            documents=[document],
            metadatas=[meta],
        )
        
        return strategy_id

    async def get_high_reward_strategies(
        self,
        agent_type: str,
        query_task: str,
        top_k: int = 3,
        min_reward: float = 7.0,
    ) -> List[Tuple[str, float]]:
        """
        Retrieve high-reward strategies similar to the given task.
        
        Args:
            agent_type: Type of agent to query
            query_task: Description of the current task to match against
            top_k: Number of strategies to retrieve
            min_reward: Only return strategies with reward >= this
            
        Returns:
            List of (strategy_output, reward_score) tuples
        """
        try:
            collection = self._get_or_create_collection(agent_type)
        except:
            # Collection doesn't exist yet
            return []
        
        try:
            # Query by similarity to task description
            results = collection.query(
                query_texts=[query_task],
                n_results=top_k,
                where={"reward_score": {"$gte": min_reward}},  # Filter by min reward
            )
            
            if not results or not results["documents"] or len(results["documents"]) == 0:
                return []
            
            # Extract strategies and scores
            strategies = []
            documents = results["documents"][0]  # query_texts returns results per query
            metadatas = results["metadatas"][0]
            
            for doc, meta in zip(documents, metadatas):
                # Extract just the strategy part (after "Strategy: ")
                if "Strategy:" in doc:
                    strategy = doc.split("Strategy:")[-1].strip()
                else:
                    strategy = doc
                
                reward = meta.get("reward_score", 5.0)
                strategies.append((strategy, reward))
            
            return strategies
        
        except Exception as e:
            print(f"Error querying strategies for {agent_type}: {e}")
            return []

    async def list_strategies(
        self,
        agent_type: str,
        limit: int = 10,
    ) -> List[dict]:
        """
        List all strategies for a given agent type.
        
        Args:
            agent_type: Type of agent
            limit: Maximum number to return
            
        Returns:
            List of strategy dicts with metadata
        """
        try:
            collection = self._get_or_create_collection(agent_type)
        except:
            return []
        
        try:
            # Get all items (no query needed)
            results = collection.get(
                limit=limit,
                where={"reward_score": {"$gte": 0}},  # All scores
            )
            
            strategies_list = []
            for doc_id, document, metadata in zip(
                results["ids"],
                results.get("documents", []),
                results.get("metadatas", []),
            ):
                strategies_list.append({
                    "id": doc_id,
                    "document": document,
                    "reward_score": metadata.get("reward_score", 0),
                    "agent_type": agent_type,
                })
            
            return strategies_list
        
        except Exception as e:
            print(f"Error listing strategies: {e}")
            return []

    async def delete_low_reward_strategies(
        self,
        agent_type: str,
        threshold: float = 3.0,
    ) -> int:
        """
        Delete strategies with reward below threshold.
        
        Args:
            agent_type: Type of agent
            threshold: Delete if reward < threshold
            
        Returns:
            Number of strategies deleted
        """
        try:
            collection = self._get_or_create_collection(agent_type)
        except:
            return 0
        
        try:
            # Get low-reward strategies
            results = collection.get(
                where={"reward_score": {"$lt": threshold}},
            )
            
            if results["ids"]:
                collection.delete(ids=results["ids"])
                return len(results["ids"])
            
            return 0
        
        except Exception as e:
            print(f"Error deleting low-reward strategies: {e}")
            return 0

    async def clear_collection(self, agent_type: str) -> None:
        """Delete all strategies for an agent type."""
        try:
            collection_name = f"{agent_type}_strategies"
            if collection_name in self.strategy_collections:
                self.client.delete_collection(name=collection_name)
                del self.strategy_collections[collection_name]
        except Exception as e:
            print(f"Error clearing collection: {e}")


# Global ChromaDB client instance
chromadb_client = ChromaDBClient()
