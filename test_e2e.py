#!/usr/bin/env python3
"""
End-to-End Test for Phase 2: Multi-Agent Orchestration Pipeline

This script:
1. POSTs a business prompt to /api/jobs
2. Monitors WebSocket for all agent events
3. Displays real-time agent activity
4. Verifies all 11 nodes executed
5. Checks final rewards and job status
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime
from typing import Optional
import websockets

# Configuration
BACKEND_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

async def test_e2e():
    """Execute full end-to-end test"""
    
    print(f"{Colors.HEADER}{Colors.BOLD}=== AutoDevOS Phase 2 End-to-End Test ==={Colors.END}\n")
    
    # ========================================================================
    # STEP 1: Create Job via POST /api/jobs
    # ========================================================================
    
    prompt = "Build a landing page for an AI-powered email productivity assistant. Show features like smart scheduling, auto-reply suggestions, and inbox prioritization."
    
    print(f"{Colors.BLUE}Step 1: Creating Job...{Colors.END}")
    print(f"Prompt: {prompt}\n")
    
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/api/jobs",
                json={"prompt": prompt},
                headers={"Content-Type": "application/json"},
            )
            
            if response.status_code != 201:
                print(f"{Colors.RED}Error: {response.status_code} {response.text}{Colors.END}")
                return
            
            result = response.json()
            job_id = result.get("jobId")
            status = result.get("status")
            
            print(f"{Colors.GREEN}✓ Job Created{Colors.END}")
            print(f"  Job ID: {Colors.CYAN}{job_id}{Colors.END}")
            print(f"  Status: {status}\n")
            
        except Exception as e:
            print(f"{Colors.RED}Failed to create job: {e}{Colors.END}")
            return
    
    # ========================================================================
    # STEP 2: Monitor WebSocket for Events
    # ========================================================================
    
    print(f"{Colors.BLUE}Step 2: Monitoring WebSocket Events...{Colors.END}")
    print(f"Connecting to {Colors.CYAN}{WS_URL}/{job_id}{Colors.END}\n")
    
    agent_states = {}
    node_order = [
        "pm", "architect", "developer", "execution",
        "qa", "tech_debt", "security", "seo",
        "meeting", "boss", "rl"
    ]
    completed_nodes = set()
    rewards = {}
    meeting_log = []
    boss_verdict = None
    
    try:
        async with websockets.connect(f"{WS_URL}/{job_id}") as websocket:
            print(f"{Colors.GREEN}✓ WebSocket Connected{Colors.END}\n")
            
            # Set timeout for event stream (5 minutes max)
            start_time = datetime.utcnow()
            timeout_seconds = 300
            
            while True:
                try:
                    # Set per-message timeout
                    message = await asyncio.wait_for(
                        websocket.recv(),
                        timeout=5.0
                    )
                    
                    event = json.loads(message)
                    event_type = event.get("type")
                    agent = event.get("agent", "N/A")
                    content = event.get("content", "")
                    timestamp = event.get("timestamp", "")
                    
                    # Track agent progress
                    if agent in node_order:
                        agent_states[agent] = event_type
                    
                    # Display event based on type
                    if event_type == "agent_log":
                        ts = timestamp.split("T")[-1][:8] if timestamp else ""
                        print(f"{Colors.CYAN}[{ts}] {agent:12}{Colors.END} {content}")
                        if agent in node_order:
                            completed_nodes.add(agent)
                    
                    elif event_type == "meeting_start":
                        print(f"\n{Colors.BOLD}{Colors.YELLOW}🤝 === TEAM MEETING ==={Colors.END}\n")
                    
                    elif event_type == "meeting_message":
                        print(f"  {Colors.YELLOW}{agent:12}{Colors.END} {content}")
                        meeting_log.append(content)
                    
                    elif event_type == "boss_verdict":
                        print(f"\n{Colors.BOLD}{Colors.YELLOW}👔 === BOSS EVALUATION ==={Colors.END}")
                        print(f"{Colors.YELLOW}{content}{Colors.END}\n")
                        boss_verdict = content
                    
                    elif event_type == "reward":
                        reward_value = event.get("reward", 0)
                        rewards[agent] = reward_value
                        print(f"{Colors.GREEN}🏆 {agent:12} Reward: {reward_value}/10{Colors.END}")
                    
                    elif event_type == "iteration_complete":
                        iteration = event.get("iteration", 0)
                        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Iteration {iteration} Complete{Colors.END}\n")
                    
                    elif event_type == "job_done":
                        print(f"\n{Colors.GREEN}{Colors.BOLD}✓✓✓ JOB COMPLETE ✓✓✓{Colors.END}\n")
                        break
                    
                    # Check overall timeout
                    elapsed = (datetime.utcnow() - start_time).total_seconds()
                    if elapsed > timeout_seconds:
                        print(f"\n{Colors.YELLOW}Timeout: Test ran for {timeout_seconds}s{Colors.END}")
                        break
                
                except asyncio.TimeoutError:
                    # No message received in 5s - could mean job is still processing
                    pass
                except Exception as e:
                    print(f"{Colors.YELLOW}WebSocket event parse error: {e}{Colors.END}")
                    pass
    
    except Exception as e:
        print(f"{Colors.RED}WebSocket connection error: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Note: This may happen if backend is still initializing.{Colors.END}")
    
    # ========================================================================
    # STEP 3: Verify Results via GET /api/jobs/{job_id}
    # ========================================================================
    
    print(f"\n{Colors.BLUE}Step 3: Verifying Job Completion...{Colors.END}\n")
    
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(f"{BACKEND_URL}/api/jobs/{job_id}")
            
            if response.status_code == 200:
                job_data = response.json()
                
                print(f"{Colors.GREEN}✓ Job Retrieved from Database{Colors.END}")
                print(f"  Job ID: {job_data['jobId']}")
                print(f"  Status: {Colors.BOLD}{job_data['status']}{Colors.END}")
                print(f"  Iterations Completed: {job_data['current_iteration']}")
                print(f"  Overall Reward: {Colors.BOLD}{job_data['overall_reward']:.1f}/100{Colors.END}")
                
                # Display rewards by agent
                rewards_by_iter = job_data.get("rewards", {})
                if rewards_by_iter:
                    print(f"\n  {Colors.BOLD}Agent Rewards:{Colors.END}")
                    for iteration, iter_rewards in sorted(rewards_by_iter.items()):
                        print(f"    Iteration {iteration}:")
                        for agent, score in sorted(iter_rewards.items()):
                            print(f"      {agent:15} {score:5.1f}/10")
            
            else:
                print(f"{Colors.RED}Error retrieving job: {response.status_code}{Colors.END}")
        
        except Exception as e:
            print(f"{Colors.RED}Failed to retrieve job: {e}{Colors.END}")
    
    # ========================================================================
    # STEP 4: Test Summary
    # ========================================================================
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== TEST SUMMARY ==={Colors.END}\n")
    
    print(f"Nodes Completed: {len(completed_nodes)}/{len(node_order)}")
    for node in node_order:
        status = "✓" if node in completed_nodes else "✗"
        color = Colors.GREEN if node in completed_nodes else Colors.RED
        print(f"  {color}{status}{Colors.END} {node}")
    
    print(f"\n{Colors.BOLD}Rewards Recorded:{Colors.END} {len(rewards)} agents")
    for agent, score in sorted(rewards.items()):
        print(f"  {agent:15} {Colors.BOLD}{score}/10{Colors.END}")
    
    print(f"\n{Colors.BOLD}Meeting Entries:{Colors.END} {len(meeting_log)}")
    if boss_verdict:
        print(f"\n{Colors.BOLD}Boss Verdict:{Colors.END}")
        print(f"  {boss_verdict[:200]}...")
    
    # ========================================================================
    # FINAL RESULT
    # ========================================================================
    
    success = len(completed_nodes) == len(node_order) and len(rewards) >= 7
    
    print(f"\n{Colors.BOLD}")
    if success:
        print(f"{Colors.GREEN}✓✓✓ PHASE 2 END-TO-END TEST PASSED ✓✓✓{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ PHASE 2 TEST INCOMPLETE{Colors.END}")
        print(f"Expected all 11 nodes + 7+ rewards, got {len(completed_nodes)} nodes + {len(rewards)} rewards")
    print(f"{Colors.END}")


if __name__ == "__main__":
    print(f"{Colors.YELLOW}Note: Ensure docker-compose services are running!{Colors.END}")
    print(f"Run: docker-compose up -d\n")
    
    try:
        asyncio.run(test_e2e())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}Test failed: {e}{Colors.END}")
        sys.exit(1)
