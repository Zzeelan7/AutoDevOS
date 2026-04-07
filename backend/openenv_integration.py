"""
OpenEnv Integration Module for AutoDevOS

This module provides OpenEnv-compatible task environments for evaluating 
and training the AI agents that generate websites.

OpenEnv Specification:
- task: The objective for the agent to achieve
- grader: Evaluates if the agent's output meets task requirements
- state: Current state of the environment
- reward: Numerical feedback for agent performance
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any, List, Tuple
from enum import Enum
import json
from pathlib import Path


class TaskDifficulty(Enum):
    """Task complexity levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class TaskSpec:
    """OpenEnv Task Specification"""
    task_id: str
    task_type: str  # e.g., "website_generation", "design_improvement"
    description: str
    prompt: str
    difficulty: TaskDifficulty
    constraints: Dict[str, Any]  # e.g., max_iterations, required_features
    metadata: Dict[str, Any]
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['difficulty'] = self.difficulty.value
        return data


@dataclass
class EnvironmentState:
    """Current state of the environment"""
    task_id: str
    job_id: str
    current_iteration: int
    agents_executed: List[str]
    codebase: Optional[Dict[str, str]] = None
    metrics: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


class Grader(ABC):
    """Base grader for evaluating agent outputs"""
    
    @abstractmethod
    async def grade(self, state: EnvironmentState) -> Tuple[float, Dict[str, Any]]:
        """
        Grade the environment state.
        
        Returns:
            Tuple of (reward_score, evaluation_details)
        """
        pass
    
    @abstractmethod
    def get_criteria(self) -> List[str]:
        """Return list of evaluation criteria"""
        pass


class WebsiteQualityGrader(Grader):
    """Grader for website generation quality"""
    
    async def grade(self, state: EnvironmentState) -> Tuple[float, Dict[str, Any]]:
        """
        Grade a generated website based on multiple criteria.
        
        Criteria:
        - Code quality (valid HTML/CSS/JS)
        - Performance (page load time, bundle size)
        - Accessibility (semantic HTML, ARIA labels)
        - Design (responsive, visual hierarchy)
        - Functionality (interactive elements work)
        """
        evaluation = {
            'code_quality': 0.0,
            'performance': 0.0,
            'accessibility': 0.0,
            'design': 0.0,
            'functionality': 0.0,
        }
        
        # Check code quality
        if state.codebase:
            html_valid = self._validate_html(state.codebase.get('index.html', ''))
            css_valid = self._validate_css(state.codebase.get('style.css', ''))
            js_valid = self._validate_javascript(state.codebase.get('script.js', ''))
            
            evaluation['code_quality'] = (html_valid + css_valid + js_valid) / 3.0
        
        # Check performance characteristics
        if state.codebase:
            evaluation['performance'] = self._evaluate_performance(state.codebase)
        
        # Check accessibility
        if state.codebase:
            evaluation['accessibility'] = self._evaluate_accessibility(state.codebase.get('index.html', ''))
        
        # Check design responsiveness
        if state.codebase:
            evaluation['design'] = self._evaluate_design(state.codebase)
        
        # Weighted average: code_quality(20%) + performance(20%) + accessibility(15%) + design(30%) + functionality(15%)
        weights = {
            'code_quality': 0.20,
            'performance': 0.20,
            'accessibility': 0.15,
            'design': 0.30,
            'functionality': 0.15,
        }
        
        final_score = sum(evaluation[k] * weights[k] for k in evaluation.keys())
        
        return final_score, evaluation
    
    def get_criteria(self) -> List[str]:
        return [
            'Code Quality',
            'Performance',
            'Accessibility',
            'Design',
            'Functionality'
        ]
    
    def _validate_html(self, html: str) -> float:
        """Simple HTML validation (0.0 to 1.0)"""
        if not html:
            return 0.0
        
        score = 0.0
        
        # Check for DOCTYPE
        if '<!DOCTYPE html>' in html.lower() or '<!doctype html>' in html:
            score += 0.2
        
        # Check for meta tags
        if '<meta' in html.lower():
            score += 0.2
        
        # Check for proper heading hierarchy
        if '<h1' in html.lower():
            score += 0.2
        
        # Check for semantic HTML
        if any(tag in html.lower() for tag in ['<header', '<nav', '<main', '<footer', '<article', '<section']):
            score += 0.2
        
        # Check for proper tag closure (basic check)
        if html.count('<div') == html.count('</div'):
            score += 0.2
        
        return min(score, 1.0)
    
    def _validate_css(self, css: str) -> float:
        """Simple CSS validation (0.0 to 1.0)"""
        if not css:
            return 0.0
        
        score = 0.0
        
        # Check for valid CSS selectors
        if '{' in css and '}' in css:
            score += 0.3
        
        # Check for responsive design (media queries)
        if '@media' in css.lower():
            score += 0.3
        
        # Check for color definitions
        if 'color:' in css.lower() or '#' in css:
            score += 0.2
        
        # Check for layout properties
        if any(prop in css.lower() for prop in ['flex', 'grid', 'display']):
            score += 0.2
        
        return min(score, 1.0)
    
    def _validate_javascript(self, js: str) -> float:
        """Simple JavaScript validation (0.0 to 1.0)"""
        if not js:
            return 0.5  # Websites don't require JS
        
        score = 0.0
        
        # Check for function definitions
        if 'function' in js or '=>' in js:
            score += 0.3
        
        # Check for event listeners
        if 'addEventListener' in js or 'onclick' in js.lower():
            score += 0.3
        
        # Check for DOM manipulation
        if 'document.' in js or 'querySelector' in js:
            score += 0.2
        
        # Check for valid syntax (basic check)
        if js.count('(') == js.count(')'):
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_performance(self, codebase: Dict[str, str]) -> float:
        """Evaluate performance characteristics"""
        score = 0.0
        
        # Check CSS file size
        css_content = codebase.get('style.css', '')
        if len(css_content) < 5000:  # Less than 5KB
            score += 0.3
        elif len(css_content) < 10000:
            score += 0.15
        
        # Check JS file size
        js_content = codebase.get('script.js', '')
        if len(js_content) < 5000:  # Less than 5KB
            score += 0.3
        elif len(js_content) < 10000:
            score += 0.15
        
        # Check HTML file size
        html_content = codebase.get('index.html', '')
        if len(html_content) < 10000:  # Less than 10KB
            score += 0.2
        elif len(html_content) < 20000:
            score += 0.1
        
        # Check for minification hints (no excessive whitespace)
        total_lines = sum(len(v.split('\n')) for v in codebase.values())
        total_chars = sum(len(v) for v in codebase.values())
        
        if total_lines < total_chars / 50:  # Good whitespace optimization
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_accessibility(self, html: str) -> float:
        """Evaluate accessibility features"""
        score = 0.0
        
        # Check for alt text
        if 'alt=' in html:
            score += 0.2
        
        # Check for proper heading hierarchy
        heading_count = sum(html.lower().count(f'<h{i}') for i in range(1, 7))
        if heading_count > 0:
            score += 0.2
        
        # Check for semantic HTML elements
        semantic_count = sum(html.lower().count(tag) for tag in 
                           ['<header', '<nav', '<main', '<footer', '<article', '<section', '<aside'])
        if semantic_count > 0:
            score += 0.2
        
        # Check for form labels
        if '<label' in html.lower():
            score += 0.2
        
        # Check for ARIA attributes
        if 'aria-' in html.lower():
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_design(self, codebase: Dict[str, str]) -> float:
        """Evaluate design quality"""
        score = 0.0
        
        html = codebase.get('index.html', '')
        css = codebase.get('style.css', '')
        
        # Check for responsive design
        if '@media' in css.lower():
            score += 0.25
        
        # Check for consistent color scheme (multiple colors used)
        if css.count('color:') > 2 or css.count('#') > 3:
            score += 0.25
        
        # Check for layout structure (divs, sections, etc)
        structure_elements = sum(html.lower().count(tag) for tag in 
                                ['<header', '<nav', '<main', '<footer', '<section', '<div'])
        if structure_elements > 3:
            score += 0.25
        
        # Check for visual hierarchy (multiple font sizes or weights)
        if 'font-size' in css.lower() or 'font-weight' in css.lower():
            score += 0.25
        
        return min(score, 1.0)


class OpenEnvTask:
    """OpenEnv-compatible Task with environment and grader"""
    
    def __init__(self, spec: TaskSpec, grader: Grader):
        self.spec = spec
        self.grader = grader
        self.state: Optional[EnvironmentState] = None
    
    async def reset(self) -> EnvironmentState:
        """Reset environment to initial state"""
        self.state = EnvironmentState(
            task_id=self.spec.task_id,
            job_id='',
            current_iteration=0,
            agents_executed=[],
            codebase=None,
            metrics=None
        )
        return self.state
    
    async def step(self, action: Dict[str, Any]) -> Tuple[EnvironmentState, float, bool]:
        """
        Execute a step in the environment.
        
        Args:
            action: Dictionary with action type and parameters
        
        Returns:
            Tuple of (new_state, reward, done)
        """
        if not self.state:
            await self.reset()
        
        # Ensure state exists
        assert self.state is not None, "State should be initialized after reset"
        
        # Process action
        if action.get('type') == 'update_codebase':
            self.state.codebase = action.get('codebase')
        
        if action.get('type') == 'add_agent':
            agent_name = action.get('agent_name')
            if agent_name and agent_name not in self.state.agents_executed:
                self.state.agents_executed.append(agent_name)
        
        if action.get('type') == 'increment_iteration':
            self.state.current_iteration += 1
        
        # Grade current state
        reward, evaluation = await self.grader.grade(self.state)
        self.state.metrics = evaluation
        
        # Determine if task is done
        done = (
            self.state.current_iteration >= self.spec.constraints.get('max_iterations', 3) or
            reward >= self.spec.constraints.get('target_reward', 0.95)
        )
        
        return self.state, reward, done
    
    async def render(self) -> Dict[str, Any]:
        """Render current environment state for display"""
        if not self.state:
            return {}
        
        return {
            'task_id': self.state.task_id,
            'job_id': self.state.job_id,
            'iteration': self.state.current_iteration,
            'agents_executed': self.state.agents_executed,
            'metrics': self.state.metrics,
            'codebase_preview': {
                k: v[:100] + '...' if len(v) > 100 else v
                for k, v in (self.state.codebase or {}).items()
            }
        }


class OpenEnvBenchmark:
    """Collection of OpenEnv tasks for evaluating AutoDevOS agents"""
    
    TASKS = {
        'simple_landing_page': TaskSpec(
            task_id='simple_landing_page',
            task_type='website_generation',
            description='Create a simple landing page with hero section and CTA',
            prompt='Design a simple landing page for a SaaS product',
            difficulty=TaskDifficulty.EASY,
            constraints={'max_iterations': 2, 'target_reward': 0.8},
            metadata={'estimated_time_seconds': 60, 'min_agents': 3}
        ),
        'portfolio_website': TaskSpec(
            task_id='portfolio_website',
            task_type='website_generation',
            description='Create a professional portfolio website',
            prompt='Create a professional portfolio website for a designer with project showcase',
            difficulty=TaskDifficulty.MEDIUM,
            constraints={'max_iterations': 3, 'target_reward': 0.85},
            metadata={'estimated_time_seconds': 120, 'min_agents': 5}
        ),
        'responsive_ecommerce': TaskSpec(
            task_id='responsive_ecommerce',
            task_type='website_generation',
            description='Create a responsive e-commerce product listing page',
            prompt='Build a responsive e-commerce product listing page with filters and search',
            difficulty=TaskDifficulty.HARD,
            constraints={'max_iterations': 4, 'target_reward': 0.9},
            metadata={'estimated_time_seconds': 180, 'min_agents': 8}
        ),
    }
    
    @classmethod
    def get_task(cls, task_id: str) -> OpenEnvTask:
        """Get a task from the benchmark"""
        if task_id not in cls.TASKS:
            raise ValueError(f"Unknown task: {task_id}")
        
        spec = cls.TASKS[task_id]
        grader = WebsiteQualityGrader()
        
        return OpenEnvTask(spec, grader)
    
    @classmethod
    def list_tasks(cls) -> List[Dict[str, Any]]:
        """List all available tasks"""
        return [
            {
                'task_id': task_id,
                'description': spec.description,
                'difficulty': spec.difficulty.value,
                'constraints': spec.constraints,
            }
            for task_id, spec in cls.TASKS.items()
        ]


# Utility functions for integration with AutoDevOS

async def evaluate_website(codebase: Dict[str, str]) -> Tuple[float, Dict[str, Any]]:
    """Quick evaluation of a generated website"""
    grader = WebsiteQualityGrader()
    state = EnvironmentState(
        task_id='direct_eval',
        job_id='',
        current_iteration=0,
        agents_executed=[],
        codebase=codebase,
        metrics=None
    )
    return await grader.grade(state)


def create_task_from_prompt(prompt: str, job_id: str) -> OpenEnvTask:
    """Create a task from a user prompt"""
    task_spec = TaskSpec(
        task_id=job_id,
        task_type='website_generation',
        description=f'Generate website: {prompt[:50]}...',
        prompt=prompt,
        difficulty=TaskDifficulty.MEDIUM,
        constraints={'max_iterations': 3, 'target_reward': 0.85},
        metadata={'custom_prompt': True, 'job_id': job_id}
    )
    
    grader = WebsiteQualityGrader()
    return OpenEnvTask(task_spec, grader)
