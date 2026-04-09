#!/usr/bin/env python3
"""
OpenEnv Server for AutoDevOS Website Generation Environment
FastAPI-based server for hosting the RL environment
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from fastapi import FastAPI
from openenv.server import Environment

# Import your environment
from openenv_env import WebsiteGenerationEnv, Observation, Action, Reward

# Create FastAPI app
app = FastAPI(title="AutoDevOS Environment Server")

# Register environment with OpenEnv server
env = Environment(
    env_class=WebsiteGenerationEnv,
    observation_type=Observation,
    action_type=Action,
    reward_type=Reward,
)

# Mount OpenEnv server endpoints
app.include_router(env.router)

def main():
    """Main entry point for OpenEnv server"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
