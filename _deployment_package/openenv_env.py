"""
OpenEnv-compliant environment for AutoDevOS website generation.

This module implements the full OpenEnv specification with:
- Typed Observation, Action, and Reward Pydantic models
- step(action) → (observation, reward, done, info)
- reset() → observation  
- state() → current environment state
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List, Tuple
from enum import Enum
import json
from datetime import datetime


# ============================================================================
# OpenEnv Models: Observation, Action, Reward
# ============================================================================

class TaskType(str, Enum):
    """Task types for website generation"""
    SIMPLE_LANDING_PAGE = "simple_landing_page"
    PORTFOLIO_WEBSITE = "portfolio_website"
    RESPONSIVE_ECOMMERCE = "responsive_ecommerce"


class Observation(BaseModel):
    """
    OpenEnv Observation: The state the agent perceives.
    
    Represents the current state of the website generation process,
    allowing agents to understand what has been generated so far
    and what feedback they received on the previous iteration.
    """
    task_id: str = Field(..., description="Unique task identifier")
    task_type: TaskType = Field(..., description="Type of website generation task")
    task_description: str = Field(..., description="Human-readable task description")
    current_iteration: int = Field(..., description="Current iteration number (0-indexed)")
    max_iterations: int = Field(..., description="Maximum allowed iterations")
    
    # Current codebase state
    generated_html: Optional[str] = Field(None, description="Current HTML code (truncated to 5000 chars)")
    generated_css: Optional[str] = Field(None, description="Current CSS code (truncated to 5000 chars)")
    generated_js: Optional[str] = Field(None, description="Current JavaScript code (truncated to 5000 chars)")
    
    # Feedback from previous iteration
    last_reward: float = Field(0.0, description="Reward from previous step (0.0-1.0)")
    last_feedback: Dict[str, float] = Field(
        default_factory=dict,
        description="Detailed evaluation feedback (code_quality, performance, accessibility, design, functionality)"
    )
    
    # Episode state
    done: bool = Field(False, description="Whether episode is complete")
    error_message: Optional[str] = Field(None, description="Error message if step failed")
    
    class Config:
        use_enum_values = True


class Action(BaseModel):
    """
    OpenEnv Action: What the agent wants to do.
    
    For website generation, agents provide improved HTML/CSS/JS code
    based on the current state and feedback from previous iterations.
    """
    html: str = Field(..., description="Updated HTML code (max 10000 chars)")
    css: str = Field(default="", description="Updated CSS code (max 10000 chars)")
    js: str = Field(default="", description="Updated JavaScript code (max 10000 chars)")
    reasoning: str = Field(
        default="",
        description="Agent's reasoning for the changes (for debugging)"
    )
    
    class Config:
        # Allow large JSON payloads for code
        json_encoders = {
            str: lambda v: v[:10000] if len(v) > 10000 else v
        }


class Reward(BaseModel):
    """
    OpenEnv Reward: Numerical feedback on agent performance.
    
    Provides multi-dimensional feedback on website quality with:
    - Overall score (0.0-1.0)
    - Breakdown scores for each evaluation dimension
    - Flags for partial progress (e.g., "has valid HTML" → partial reward)
    """
    total_score: float = Field(..., description="Overall quality score (0.0-1.0)", ge=0.0, le=1.0)
    code_quality: float = Field(..., description="Code quality score (0.0-1.0)", ge=0.0, le=1.0)
    performance: float = Field(..., description="Performance score (0.0-1.0)", ge=0.0, le=1.0)
    accessibility: float = Field(..., description="Accessibility score (0.0-1.0)", ge=0.0, le=1.0)
    design: float = Field(..., description="Design quality score (0.0-1.0)", ge=0.0, le=1.0)
    functionality: float = Field(..., description="Functionality score (0.0-1.0)", ge=0.0, le=1.0)
    
    # Partial progress signals for better learning
    has_valid_html: bool = Field(..., description="True if HTML is well-formed")
    has_responsive_css: bool = Field(..., description="True if CSS has responsive design")
    has_interactivity: bool = Field(..., description="True if JavaScript adds functionality")
    
    progress_delta: float = Field(
        0.0,
        description="Change in score from previous iteration (-1.0 to +1.0)"
    )


class StepResponse(BaseModel):
    """
    OpenEnv step() response: What happens after an action.
    """
    observation: Observation
    reward: Reward
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ResetResponse(BaseModel):
    """
    OpenEnv reset() response: Initial state.
    """
    observation: Observation


# ============================================================================
# Environment Implementation
# ============================================================================

class WebsiteGenerationEnv:
    """
    OpenEnv environment for website generation tasks.
    
    This environment simulates the process of iteratively generating
    and improving website code through agent interaction.
    
    State machine:
    - reset() → initial observation
    - step(action) → (observation, reward, done, info)
    - state() → current internal state
    """
    
    def __init__(self, task_type: str = "simple_landing_page"):
        """Initialize environment for a specific task type."""
        self.task_type = TaskType(task_type)
        self.task_specs = self._get_task_specs()
        
        # Environment state
        self.iteration = 0
        self.generated_html = ""
        self.generated_css = ""
        self.generated_js = ""
        self.best_reward = 0.0
        self.last_reward = 0.0
        self.last_feedback: Dict[str, float] = {}
        self.done = False
        self.history: List[Tuple[Action, Reward]] = []
        self.reset_timestamp = None
        
    def _get_task_specs(self) -> Dict[str, Any]:
        """Get task specifications by type."""
        specs = {
            TaskType.SIMPLE_LANDING_PAGE: {
                "description": "Create a simple landing page with hero section and call-to-action button",
                "max_iterations": 2,
                "target_reward": 0.8,
                "difficulty": "easy",
            },
            TaskType.PORTFOLIO_WEBSITE: {
                "description": "Create a professional portfolio website with project showcase, about section, and contact form",
                "max_iterations": 3,
                "target_reward": 0.85,
                "difficulty": "medium",
            },
            TaskType.RESPONSIVE_ECOMMERCE: {
                "description": "Create a responsive e-commerce product listing page with filters, search, and shopping cart",
                "max_iterations": 4,
                "target_reward": 0.9,
                "difficulty": "hard",
            },
        }
        return specs.get(self.task_type, specs[TaskType.SIMPLE_LANDING_PAGE])
    
    async def reset(self) -> ResetResponse:
        """Reset environment to initial state."""
        self.iteration = 0
        self.generated_html = ""
        self.generated_css = ""
        self.generated_js = ""
        self.best_reward = 0.0
        self.last_reward = 0.0
        self.last_feedback = {}
        self.done = False
        self.history = []
        self.reset_timestamp = datetime.utcnow().isoformat()
        
        initial_obs = Observation(
            task_id=self.task_type.value,
            task_type=self.task_type,
            task_description=self.task_specs["description"],
            current_iteration=self.iteration,
            max_iterations=self.task_specs["max_iterations"],
            generated_html="",
            generated_css="",
            generated_js="",
            last_reward=0.0,
            last_feedback={},
            done=False,
            error_message=None,
        )
        
        return ResetResponse(observation=initial_obs)
    
    async def step(self, action: Action) -> StepResponse:
        """Execute one step of the environment."""
        if self.done:
            return self._create_error_response("Episode already complete")
        
        # Validate action
        if not action.html:
            return self._create_error_response("HTML code is required")
        
        # Update state
        self.generated_html = action.html[:10000]
        self.generated_css = action.css[:10000] if action.css else ""
        self.generated_js = action.js[:10000] if action.js else ""
        self.iteration += 1
        
        # Grade the submission
        reward = await self._grade_submission()
        
        # Update tracking
        self.history.append((action, reward))
        self.last_reward = reward.total_score
        self.last_feedback = {
            "code_quality": reward.code_quality,
            "performance": reward.performance,
            "accessibility": reward.accessibility,
            "design": reward.design,
            "functionality": reward.functionality,
        }
        
        if reward.total_score > self.best_reward:
            self.best_reward = reward.total_score
        
        # Check if done
        target_reward = self.task_specs["target_reward"]
        max_iterations = self.task_specs["max_iterations"]
        
        self.done = (
            reward.total_score >= target_reward or
            self.iteration >= max_iterations
        )
        
        # Create observation
        obs = Observation(
            task_id=self.task_type.value,
            task_type=self.task_type,
            task_description=self.task_specs["description"],
            current_iteration=self.iteration,
            max_iterations=max_iterations,
            generated_html=self.generated_html[:5000],
            generated_css=self.generated_css[:5000],
            generated_js=self.generated_js[:5000],
            last_reward=self.last_reward,
            last_feedback=self.last_feedback,
            done=self.done,
            error_message=None,
        )
        
        info = {
            "best_reward": self.best_reward,
            "best_reward_at_iteration": self.history.index((action, reward)) if (action, reward) in self.history else -1,
            "episode_summary": {
                "total_steps": self.iteration,
                "completed": self.done,
                "target_reward": target_reward,
            } if self.done else {}
        }
        
        return StepResponse(
            observation=obs,
            reward=reward,
            done=self.done,
            info=info
        )
    
    async def state(self) -> Dict[str, Any]:
        """Get current environment state (for debugging/monitoring)."""
        return {
            "task_type": self.task_type.value,
            "iteration": self.iteration,
            "done": self.done,
            "best_reward": self.best_reward,
            "last_reward": self.last_reward,
            "generated_html_length": len(self.generated_html),
            "generated_css_length": len(self.generated_css),
            "generated_js_length": len(self.generated_js),
            "history_length": len(self.history),
            "reset_timestamp": self.reset_timestamp,
        }
    
    async def _grade_submission(self) -> Reward:
        """Grade the generated website code."""
        html_score = self._score_html()
        css_score = self._score_css()
        js_score = self._score_js()
        
        # Weighted scoring
        code_quality = (html_score + css_score + js_score) / 3.0
        performance = self._score_performance()
        accessibility = self._score_accessibility()
        design = self._score_design()
        functionality = self._score_functionality()
        
        # Weighted average for final score
        total_score = (
            code_quality * 0.2 +
            performance * 0.2 +
            accessibility * 0.15 +
            design * 0.3 +
            functionality * 0.15
        )
        
        # Partial progress signals
        has_valid_html = html_score > 0.4
        has_responsive_css = "@media" in self.generated_css.lower()
        has_interactivity = "addEventListener" in self.generated_js or "onclick" in self.generated_js.lower()
        
        # Progress delta
        progress_delta = total_score - self.last_reward
        
        return Reward(
            total_score=min(max(total_score, 0.0), 1.0),
            code_quality=min(max(code_quality, 0.0), 1.0),
            performance=min(max(performance, 0.0), 1.0),
            accessibility=min(max(accessibility, 0.0), 1.0),
            design=min(max(design, 0.0), 1.0),
            functionality=min(max(functionality, 0.0), 1.0),
            has_valid_html=has_valid_html,
            has_responsive_css=has_responsive_css,
            has_interactivity=has_interactivity,
            progress_delta=progress_delta,
        )
    
    def _score_html(self) -> float:
        """Score HTML validity and structure (0.0-1.0)."""
        if not self.generated_html:
            return 0.0
        
        score = 0.0
        html_lower = self.generated_html.lower()
        
        # DOCTYPE declaration (REQUIRED)
        if "<!doctype html" in html_lower:
            score += 0.15
        
        # Meta tags (REQUIRED: charset and viewport)
        has_charset = "charset" in html_lower
        has_viewport = "viewport" in html_lower
        meta_score = 0
        if has_charset:
            meta_score += 0.075
        if has_viewport:
            meta_score += 0.075
        score += meta_score
        
        # Semantic structure (REQUIRED)
        semantic_tags = ["<header", "<nav", "<main", "<footer", "<section", "<article"]
        semantic_count = sum(1 for tag in semantic_tags if tag in html_lower)
        if semantic_count >= 3:
            score += 0.15  # Multiple semantic tags
        elif semantic_count >= 1:
            score += 0.08
        
        # Proper heading hierarchy
        h1_count = self.generated_html.lower().count("<h1")
        if h1_count == 1:
            score += 0.10  # Exactly one H1
        elif h1_count > 1:
            score += 0.05  # Multiple H1s (not ideal)
        
        # Tag closure validation (basic)
        opening_divs = self.generated_html.count("<div")
        closing_divs = self.generated_html.count("</div>")
        opening_p = self.generated_html.count("<p")
        closing_p = self.generated_html.count("</p>")
        
        if opening_divs == closing_divs and opening_p == closing_p:
            score += 0.15
        
        # Content quality
        if len(self.generated_html) > 200:  # Substantial content
            score += 0.15
        
        # Image alt attributes (accessibility)
        if 'alt="' in self.generated_html or "alt='" in self.generated_html:
            score += 0.10
        
        return min(score, 1.0)
    
    def _score_css(self) -> float:
        """Score CSS validity and structure (0.0-1.0)."""
        if not self.generated_css:
            return 0.5  # CSS not required but helpful
        
        score = 0.0
        css_lower = self.generated_css.lower()
        
        # Valid CSS structure with multiple rules
        rule_count = self.generated_css.count("{")
        if rule_count >= 5:
            score += 0.20  # Multiple CSS rules
        elif rule_count >= 2:
            score += 0.10
        
        # Responsive design (@media queries)
        if "@media" in css_lower:
            score += 0.25  # Has responsive design
        
        # Color definitions (variety)
        color_count = self.generated_css.count("color:") + self.generated_css.count("#")
        if color_count >= 5:
            score += 0.20  # Rich color palette
        elif color_count >= 2:
            score += 0.10
        
        # Layout properties (flexbox/grid)
        layout_props = ["flex", "grid", "display"]
        layout_count = sum(1 for prop in layout_props if prop in css_lower)
        if layout_count >= 2:
            score += 0.15  # Modern layout system
        
        # Typography properties (font-size, font-weight, line-height)
        typography_props = ["font-size", "font-weight", "line-height", "font-family"]
        typography_count = sum(1 for prop in typography_props if prop in css_lower)
        if typography_count >= 2:
            score += 0.15
        
        # Spacing and visual hierarchy (margin/padding)
        if any(prop in css_lower for prop in ["margin", "padding"]):
            score += 0.10
        
        # Comments or well-organized structure (optional bonus)
        if "/*" in self.generated_css:
            score += 0.05
        
        return min(score, 1.0)
    
    def _score_js(self) -> float:
        """Score JavaScript validity and functionality (0.0-1.0)."""
        if not self.generated_js:
            return 0.5  # JS not required but helpful
        
        score = 0.0
        js_lower = self.generated_js.lower()
        
        # Function definitions
        if "function" in js_lower or "=>" in self.generated_js:
            score += 0.15
        
        # Event listeners (addEventListener is better than onclick)
        if "addeventlistener" in js_lower:
            score += 0.20  # Modern event handling
        elif "onclick" in js_lower or "onload" in js_lower:
            score += 0.10  # Inline event handlers (older style)
        
        # DOM manipulation
        dom_apis = ["document", "queryselector", "getelementbyid", "innerhtml", "textcontent"]
        dom_count = sum(1 for api in dom_apis if api in js_lower)
        if dom_count >= 2:
            score += 0.20  # Multiple DOM interactions
        
        # Valid syntax checking
        open_parens = self.generated_js.count("(")
        close_parens = self.generated_js.count(")")
        open_braces = self.generated_js.count("{")
        close_braces = self.generated_js.count("}")
        
        if open_parens == close_parens and open_braces == close_braces:
            score += 0.20  # Balanced syntax
        
        # Code organization
        if ";" in self.generated_js and len(self.generated_js.split(";")) >= 3:
            score += 0.15  # Multiple statements (organized code)
        
        # Substantial code
        if len(self.generated_js) > 100:
            score += 0.10
        
        return min(score, 1.0)
    
    def _score_performance(self) -> float:
        """Score performance characteristics (0.0-1.0)."""
        score = 0.0
        total_size = len(self.generated_html) + len(self.generated_css) + len(self.generated_js)
        
        # File size efficiency
        if total_size < 20000:  # 20KB total
            score += 0.4
        elif total_size < 50000:
            score += 0.2
        
        # No excessive whitespace
        lines = len(self.generated_html.split("\n"))
        if total_size > 0 and lines < total_size / 20:
            score += 0.3
        
        # Inline vs separate files (prefer separate)
        if len(self.generated_css) > 0 and len(self.generated_js) > 0:
            score += 0.3
        
        return min(score, 1.0)
    
    def _score_accessibility(self) -> float:
        """Score accessibility features (0.0-1.0)."""
        score = 0.0
        html_lower = self.generated_html.lower()
        
        # Alt attributes for images (REQUIRED for accessibility)
        img_count = self.generated_html.lower().count("<img")
        alt_count = self.generated_html.count('alt="') + self.generated_html.count("alt='")
        if img_count > 0:
            alt_ratio = alt_count / img_count
            score += 0.15 * alt_ratio  # Partial credit if some have alt
        else:
            score += 0.15  # Full credit if no images
        
        # Heading hierarchy (REQUIRED)
        h1_count = self.generated_html.lower().count("<h1")
        if h1_count > 0:
            score += 0.20  # Has H1
            # Check for proper hierarchy (h2, h3, etc)
            h_tags = sum(self.generated_html.lower().count(f"<h{i}") for i in range(1, 7))
            if h_tags >= 2:
                score += 0.10  # Multiple heading levels
        
        # Semantic HTML (REQUIRED - header, nav, main, footer, etc)
        semantic_tags = sum(
            self.generated_html.lower().count(tag)
            for tag in ["<header", "<nav", "<main", "<footer", "<article", "<section"]
        )
        if semantic_tags >= 3:
            score += 0.25  # Full credit with multiple semantic tags
        elif semantic_tags >= 1:
            score += 0.12  # Partial credit for some semantic tags
        
        # Form labels (REQUIRED for forms)
        has_forms = "<form" in html_lower or "<input" in html_lower
        has_labels = "<label" in html_lower
        if has_forms and has_labels:
            score += 0.15  # Forms with labels
        elif has_forms and not has_labels:
            score += 0.05  # Forms but no labels (bad accessibility)
        elif not has_forms:
            score += 0.15  # No forms = no requirement
        
        # ARIA attributes (bonus)
        if "aria-" in html_lower:
            score += 0.15
        
        return min(score, 1.0)
    
    def _score_design(self) -> float:
        """Score design quality (0.0-1.0)."""
        score = 0.0
        css_lower = self.generated_css.lower()
        html_lower = self.generated_html.lower()
        
        if not self.generated_css:
            return 0.0  # No CSS = no design
        
        # Responsive design (REQUIRED)
        if "@media" in css_lower:
            score += 0.25  # Has responsive rules
            # Check for multiple breakpoints (even better)
            media_count = self.generated_css.count("@media")
            if media_count >= 2:
                score += 0.05
        
        # Visual consistency - Color palette
        color_count = self.generated_css.count("color:") + self.generated_css.count("#")
        gradient_count = self.generated_css.count("gradient")
        if color_count >= 5 or gradient_count > 0:
            score += 0.25  # Rich color palette
        elif color_count >= 2:
            score += 0.12  # Basic colors
        
        # Layout system (flexbox or grid)
        has_flex = "display:flex" in css_lower or "display: flex" in css_lower
        has_grid = "display:grid" in css_lower or "display: grid" in css_lower
        if has_flex or has_grid:
            score += 0.20  # Modern layout system
        
        # Structural layout - sections
        section_count = sum(
            self.generated_html.count(tag)
            for tag in ["<header", "<nav", "<main", "<footer", "<section", "<article"]
        )
        if section_count >= 4:
            score += 0.15  # Multiple distinct sections
        elif section_count >= 2:
            score += 0.08
        
        # Typography with variation
        font_styles = 0
        if "font-size" in css_lower:
            font_styles += 1
        if "font-weight" in css_lower:
            font_styles += 1
        if "line-height" in css_lower:
            font_styles += 1
        
        if font_styles >= 2:
            score += 0.15
        elif font_styles >= 1:
            score += 0.08
        
        return min(score, 1.0)
    
    def _score_functionality(self) -> float:
        """Score functional features (0.0-1.0)."""
        html_lower = self.generated_html.lower()
        score = 0.3  # Base score for having content
        
        # Interactive elements - buttons
        has_buttons = "<button" in html_lower
        has_onclick = "onclick" in html_lower or "addeventlistener" in self.generated_js.lower()
        if has_buttons and has_onclick:
            score += 0.25  # Buttons with handlers
        elif has_buttons:
            score += 0.12
        
        # Form elements with proper handling
        has_forms = "<form" in html_lower
        has_inputs = "<input" in html_lower or "<textarea" in html_lower or "<select" in html_lower
        if has_forms and has_inputs:
            score += 0.25  # Full form structure
        elif has_inputs:
            score += 0.12  # Form elements without form tag
        
        # Navigation/Links
        has_nav = "<nav" in html_lower or "<a" in html_lower
        nav_count = self.generated_html.lower().count("<a")
        if nav_count >= 2:
            score += 0.20  # Multiple working links
        elif has_nav:
            score += 0.10
        
        return min(score, 1.0)
    
    def _create_error_response(self, error_msg: str) -> StepResponse:
        """Create an error response with zero reward."""
        obs = Observation(
            task_id=self.task_type.value,
            task_type=self.task_type,
            task_description=self.task_specs["description"],
            current_iteration=self.iteration,
            max_iterations=self.task_specs["max_iterations"],
            generated_html=self.generated_html[:5000],
            generated_css=self.generated_css[:5000],
            generated_js=self.generated_js[:5000],
            last_reward=self.last_reward,
            last_feedback=self.last_feedback,
            done=True,
            error_message=error_msg,
        )
        
        reward = Reward(
            total_score=0.0,
            code_quality=0.0,
            performance=0.0,
            accessibility=0.0,
            design=0.0,
            functionality=0.0,
            has_valid_html=False,
            has_responsive_css=False,
            has_interactivity=False,
            progress_delta=0.0 - self.last_reward,
        )
        
        return StepResponse(
            observation=obs,
            reward=reward,
            done=True,
            info={"error": error_msg}
        )
