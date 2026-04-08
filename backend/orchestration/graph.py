"""
Complete LangGraph orchestration pipeline for AutoDevOS.
Implements all 11 nodes and state management.
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional
import json
from datetime import datetime

# Import all agents
from agents.pm import PMAgent
from agents.architect import ArchitectAgent
from agents.developer import DeveloperAgent
from agents.qa import QAAgent
from agents.security import SecurityAgent
from agents.tech_debt import TechDebtAgent
from agents.seo import SEOAgent
from agents.boss import BossAgent
from sandbox.runner import sandbox
from orchestration.rl_engine import rl_engine


class AgentState(TypedDict):
    """Shared state flowing through all pipeline nodes"""
    job_id: str
    prompt: str
    iteration: int
    codebase: Dict[str, str]  # filename -> content
    spec: str
    design: Dict[str, str]  # filename -> description
    test_results: Dict[str, Any]
    security_report: Dict[str, Any]
    tech_debt_report: Dict[str, Any]
    seo_report: Dict[str, Any]
    meeting_log: List[str]
    rewards: Dict[str, float]  # agent_name -> score
    error: Optional[str]
    lighthouse_results: Dict[str, Any]
    redis_client: Any  # RedisClient instance


# ============================================================================
# NODE IMPLEMENTATIONS
# ============================================================================


async def pm_node(state: AgentState) -> AgentState:
    """Product Manager generates specification from prompt"""
    agent = PMAgent(state["redis_client"], state["job_id"], rl_engine=rl_engine)
    await agent.emit("agent_log", f"📋 Generating detailed spec...")
    
    # Use raw prompt (or enhanced plan if available)
    source = state.get("enhanced_plan") or state["prompt"]
    spec = await agent.generate_spec(source)
    state["spec"] = spec
    
    await agent.emit("agent_log", f"✓ Spec generated ({len(spec)} chars)")
    return state


async def architect_node(state: AgentState) -> AgentState:
    """Architect designs file structure"""
    agent = ArchitectAgent(state["redis_client"], state["job_id"], rl_engine=rl_engine)
    await agent.emit("agent_log", "🏗️  Designing file structure...")
    
    design = await agent.design_architecture(state["spec"])
    state["design"] = design
    
    await agent.emit("agent_log", f"✓ Design complete ({len(design)} files)")
    return state


async def developer_node(state: AgentState) -> AgentState:
    """Developer generates HTML/CSS/JS code"""
    agent = DeveloperAgent(state["redis_client"], state["job_id"], rl_engine=rl_engine)
    await agent.emit("agent_log", "💻 Writing production code...")
    
    qa_results = state.get("test_results", {})
    security_report = state.get("security_report", {})
    seo_rec = state.get("seo_report", {})
    
    codebase = await agent.generate_code(
        state["spec"],
        state["design"],
        json.dumps(qa_results),
        json.dumps(security_report),
        json.dumps(seo_rec),
    )
    state["codebase"] = codebase
    
    await agent.emit("agent_log", f"✓ Code generated ({len(codebase)} files)")
    return state


async def execution_node(state: AgentState) -> AgentState:
    """Execute site in sandbox and collect metrics"""
    from agents.base import OllamaClient
    
    # Attempt to ensure Ollama model is available (gracefully skip if unavailable)
    try:
        client = OllamaClient()
        await client.pull_model()  # Ensure model available  
    except Exception as e:
        print(f"⚠️  Ollama unavailable for verification, skipping model pull: {e}", flush=True)
    
    # Emit to client
    event = {
        "type": "agent_log",
        "agent": "execution",
        "content": "🧪 Running site in sandbox...",
        "timestamp": datetime.utcnow().isoformat(),
    }
    await state["redis_client"].publish_event(state["job_id"], event)
    
    # Run in sandbox
    lighthouse_results = await sandbox.run_site(
        state["job_id"],
        state["iteration"],
        state["codebase"]
    )
    state["lighthouse_results"] = lighthouse_results
    
    # Emit result
    event = {
        "type": "agent_log",
        "agent": "execution",
        "content": f"✓ Lighthouse score: {lighthouse_results.get('lighthouse_score', 0)}/100",
        "timestamp": datetime.utcnow().isoformat(),
    }
    await state["redis_client"].publish_event(state["job_id"], event)
    
    return state


async def qa_node(state: AgentState) -> AgentState:
    """QA reviews code and results"""
    agent = QAAgent(state["redis_client"], state["job_id"], rl_engine=rl_engine)
    await agent.emit("agent_log", "🧪 Running QA review...")
    
    test_results = await agent.review_code(state["codebase"], state["lighthouse_results"])
    state["test_results"] = test_results
    
    bugs = len(test_results.get("bugs", []))
    await agent.emit("agent_log", f"✓ Found {bugs} issues to address")
    return state


async def tech_debt_node(state: AgentState) -> AgentState:
    """Tech Debt engineer reviews for refactoring"""
    agent = TechDebtAgent(state["redis_client"], state["job_id"], rl_engine=rl_engine)
    await agent.emit("agent_log", "🔧 Reviewing technical debt...")
    
    tech_debt_report = await agent.review_tech_debt(state["codebase"])
    state["tech_debt_report"] = tech_debt_report
    
    issues = len(tech_debt_report.get("issues", []))
    await agent.emit("agent_log", f"✓ Identified {issues} tech debt items")
    return state


async def security_node(state: AgentState) -> AgentState:
    """Security engineer scans for vulnerabilities"""
    agent = SecurityAgent(state["redis_client"], state["job_id"], rl_engine=rl_engine)
    await agent.emit("agent_log", "🔒 Running security scan...")
    
    security_report = await agent.scan_security(state["codebase"])
    state["security_report"] = security_report
    
    vulns = len(security_report.get("vulnerabilities", []))
    await agent.emit("agent_log", f"✓ Found {vulns} security items")
    return state


async def seo_node(state: AgentState) -> AgentState:
    """SEO specialist analyzes and recommends"""
    agent = SEOAgent(state["redis_client"], state["job_id"], rl_engine=rl_engine)
    await agent.emit("agent_log", "📊 Analyzing SEO...")
    
    seo_report = await agent.analyze_seo(state["codebase"], state["lighthouse_results"])
    state["seo_report"] = seo_report
    
    recs = len(seo_report.get("recommendations", []))
    await agent.emit("agent_log", f"✓ Generated {recs} SEO recommendations")
    return state


async def meeting_node(state: AgentState) -> AgentState:
    """Orchestrate structured team meeting"""
    await state["redis_client"].publish_event(
        state["job_id"],
        {
            "type": "meeting_start",
            "agent": "meeting",
            "content": "🤝 Team meeting started",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    
    # Each agent presents (abbreviated for Phase 2)
    presentations = [
        ("pm", f"Spec: Targets users who need website generation. Key pages: home, features, contact."),
        ("architect", f"Design: {len(state['design'])} files. HTML/CSS/JS structure for static deployment."),
        ("developer", f"Code: {len(state['codebase'])} files generated. Modern, responsive design."),
        ("qa", f"Testing: {len(state.get('test_results', {}).get('bugs', []))} issues found."),
        ("security", f"Security: {len(state.get('security_report', {}).get('vulnerabilities', []))} items."),
        ("tech_debt", f"Refactoring: {len(state.get('tech_debt_report', {}).get('issues', []))} items."),
        ("seo", f"SEO Score: {state['lighthouse_results'].get('lighthouse_score', 0)}/100"),
    ]
    
    for agent, content in presentations:
        await state["redis_client"].publish_event(
            state["job_id"],
            {
                "type": "meeting_message",
                "agent": agent,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        # Small delay for UX realism
        import asyncio
        await asyncio.sleep(0.3)
    
    state["meeting_log"] = [p[1] for p in presentations]
    return state


async def boss_node(state: AgentState) -> AgentState:
    """Boss Agent evaluates and assigns rewards"""
    agent = BossAgent(state["redis_client"], state["job_id"], rl_engine=rl_engine)
    await agent.emit("agent_log", "👔 Boss evaluating iteration...")
    
    verdict = await agent.evaluate_iteration(
        state["prompt"],
        state["spec"],
        state["design"],
        state["codebase"],
        state.get("test_results", {}),
        state.get("security_report", {}),
        state.get("tech_debt_report", {}),
        state.get("seo_report", {}),
        state.get("lighthouse_results", {}),
    )
    
    # Store rewards
    state["rewards"] = {
        "pm": verdict.get("pm_score", 0),
        "architect": verdict.get("architect_score", 0),
        "developer": verdict.get("developer_score", 0),
        "qa": verdict.get("qa_score", 0),
        "security": verdict.get("security_score", 0),
        "tech_debt": verdict.get("tech_debt_score", 0),
        "seo": verdict.get("seo_score", 0),
    }
    
    # Emit boss verdict
    await agent.emit("boss_verdict", verdict.get("verdict_summary", ""))
    for agent_name, score in state["rewards"].items():
        await agent.emit("reward", f"{agent_name}: {score}/10", reward=score)
    
    return state


async def rl_node(state: AgentState) -> AgentState:
    """Store strategies in vector memory (Phase 3) using ChromaDB"""
    from agents.base import OllamaClient
    
    client = OllamaClient()
    
    # Build agent results dict for RL storage
    agent_results = {
        "pm": state.get("spec", ""),
        "architect": state.get("design", {}),
        "developer": state.get("codebase", {}),
        "qa": state.get("test_results", {}),
        "security": state.get("security_report", {}),
        "tech_debt": state.get("tech_debt_report", {}),
        "seo": state.get("seo_report", {}),
        "boss": state.get("rewards", {}),
    }
    
    # Store iteration results in ChromaDB
    await rl_engine.store_iteration_results(
        job_id=state["job_id"],
        iteration=state["iteration"],
        agent_results=agent_results,
        rewards=state.get("rewards", {}),
    )
    
    # Emit RL storage event
    event = {
        "type": "agent_log",
        "agent": "rl",
        "content": f"📚 Stored {len([r for r in state.get('rewards', {}).values() if r >= 7.0])} high-reward strategies from iteration {state['iteration']}",
        "timestamp": datetime.utcnow().isoformat(),
    }
    await state["redis_client"].publish_event(state["job_id"], event)
    
    # Increment iteration for next loop
    state["iteration"] += 1
    
    return state


def should_continue(state: AgentState) -> str:
    """Determine if pipeline should continue or stop"""
    current = state.get("iteration", 1)
    max_iterations = 3
    
    if current < max_iterations:
        return "continue"
    return END


# ============================================================================
# GRAPH CONSTRUCTION
# ============================================================================


def create_graph():
    """Build the complete LangGraph pipeline"""
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("pm", pm_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("qa", qa_node)
    workflow.add_node("tech_debt", tech_debt_node)
    workflow.add_node("security", security_node)
    workflow.add_node("seo", seo_node)
    workflow.add_node("meeting", meeting_node)
    workflow.add_node("boss", boss_node)
    workflow.add_node("rl", rl_node)
    
    # Add execution edges (linear order)
    workflow.add_edge("__start__", "pm")
    workflow.add_edge("pm", "architect")
    workflow.add_edge("architect", "developer")
    workflow.add_edge("developer", "execution")
    workflow.add_edge("execution", "qa")
    workflow.add_edge("qa", "tech_debt")
    workflow.add_edge("tech_debt", "security")
    workflow.add_edge("security", "seo")
    workflow.add_edge("seo", "meeting")
    workflow.add_edge("meeting", "boss")
    workflow.add_edge("boss", "rl")
    
    # Conditional edge: continue loop or end
    workflow.add_conditional_edges(
        "rl",
        should_continue,
        {
            "continue": "developer",  # Loop back to developer for next iteration
            END: END,
        }
    )
    
    return workflow.compile()


# Global graph instance
graph = create_graph()
