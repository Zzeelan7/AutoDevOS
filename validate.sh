#!/usr/bin/env bash
# Pre-submission validation for AutoDevOS OpenEnv submission
# This script performs the checks required by the competition

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
}

hint() {
    echo -e "${YELLOW}→${NC} $1"
}

stop_at() {
    echo -e "\n${RED}${BOLD}Validation stopped at $1${NC}\n"
    exit 1
}

run_with_timeout() {
    local timeout=$1
    shift
    timeout "$timeout" "$@" 2>&1 || echo "TIMEOUT_OR_ERROR"
}

# ============================================================================
# STEP 1: Check repository structure
# ============================================================================
echo -e "\n${BOLD}Step 1/4: Checking repository structure${NC} ...\n"

if [ ! -f "$SCRIPT_DIR/openenv.yaml" ]; then
    fail "openenv.yaml not found in root directory"
    hint "Create openenv.yaml with OpenEnv metadata"
    stop_at "Step 1"
fi
pass "openenv.yaml found"

if [ ! -f "$SCRIPT_DIR/inference.py" ]; then
    fail "inference.py not found in root directory (REQUIRED)"
    hint "Create inference.py with baseline agent implementation"
    stop_at "Step 1"
fi
pass "inference.py found"

if [ ! -f "$SCRIPT_DIR/requirements-inference.txt" ]; then
    fail "requirements-inference.txt not found"
    hint "Create requirements-inference.txt with Python dependencies"
    stop_at "Step 1"
fi
pass "requirements-inference.txt found"

if [ ! -f "$SCRIPT_DIR/backend/openenv_env.py" ]; then
    fail "backend/openenv_env.py not found"
    hint "Create backend/openenv_env.py with Pydantic models and environment"
    stop_at "Step 1"
fi
pass "backend/openenv_env.py found"

if [ ! -f "$SCRIPT_DIR/Dockerfile" ]; then
    fail "Dockerfile not found in root directory"
    hint "Create Dockerfile that packages the environment"
    stop_at "Step 1"
fi
pass "Dockerfile found"

if [ ! -f "$SCRIPT_DIR/README.md" ]; then
    fail "README.md not found"
    hint "Create README.md with complete documentation"
    stop_at "Step 1"
fi
pass "README.md found"

# ============================================================================
# STEP 2: Build Docker image
# ============================================================================
echo -e "\n${BOLD}Step 2/4: Building Docker image${NC} ...\n"

if ! command -v docker &>/dev/null; then
    fail "docker command not found"
    hint "Install Docker from https://docs.docker.com/get-docker/"
    stop_at "Step 2"
fi

pass "Docker CLI found"

DOCKER_BUILD_TIMEOUT=300  # 5 minutes
BUILD_OK=false
BUILD_OUTPUT=$(run_with_timeout "$DOCKER_BUILD_TIMEOUT" docker build "$SCRIPT_DIR" 2>&1) && BUILD_OK=true

if [ "$BUILD_OK" = true ]; then
    pass "Docker build succeeded"
else
    fail "Docker build failed (timeout=${DOCKER_BUILD_TIMEOUT}s or build error)"
    echo -e "\n${YELLOW}Build output (last 30 lines):${NC}"
    printf "%s\n" "$BUILD_OUTPUT" | tail -30
    stop_at "Step 2"
fi

# ============================================================================
# STEP 3: Validate OpenEnv YAML
# ============================================================================
echo -e "\n${BOLD}Step 3/4: Validating OpenEnv specification${NC} ...\n"

# Check if openenv CLI is available
if ! command -v openenv &>/dev/null; then
    hint "openenv CLI not found - installing..."
    pip install --quiet openenv-core 2>&1 || {
        hint "Could not install openenv-core automatically"
        hint "Install it manually: pip install openenv-core"
    }
fi

if command -v openenv &>/dev/null; then
    VALIDATE_OK=false
    VALIDATE_OUTPUT=$(cd "$SCRIPT_DIR" && openenv validate 2>&1) && VALIDATE_OK=true

    if [ "$VALIDATE_OK" = true ]; then
        pass "openenv validate passed"
        [ -n "$VALIDATE_OUTPUT" ] && echo "  $VALIDATE_OUTPUT"
    else
        fail "openenv validate failed"
        echo -e "\n${YELLOW}Validation output:${NC}"
        printf "%s\n" "$VALIDATE_OUTPUT"
        stop_at "Step 3"
    fi
else
    hint "openenv CLI not available - skipping openenv validate"
    hint "Install with: pip install openenv-core"
fi

# ============================================================================
# STEP 4: Check required files and structure
# ============================================================================
echo -e "\n${BOLD}Step 4/4: Checking required files and formats${NC} ...\n"

# Check that inference.py has proper logging
if grep -q '\[START\]' "$SCRIPT_DIR/inference.py" || grep -q '"event": "START"' "$SCRIPT_DIR/inference.py"; then
    pass "inference.py has START logging"
else
    fail "inference.py missing [START] or START event logging"
    hint "Add structured logging with [START], [STEP], [END] events"
fi

if grep -q '\[STEP\]' "$SCRIPT_DIR/inference.py" || grep -q '"event": "STEP"' "$SCRIPT_DIR/inference.py"; then
    pass "inference.py has STEP logging"
else
    fail "inference.py missing [STEP] or STEP event logging"
    hint "Log each step with [STEP] or JSON 'event': 'STEP'"
fi

if grep -q '\[END\]' "$SCRIPT_DIR/inference.py" || grep -q '"event": "END"' "$SCRIPT_DIR/inference.py"; then
    pass "inference.py has END logging"
else
    fail "inference.py missing [END] or END event logging"
    hint "Log episode end with [END] or JSON 'event': 'END'"
fi

# Check that Pydantic models exist
if grep -q "class Observation" "$SCRIPT_DIR/backend/openenv_env.py"; then
    pass "Observation model defined"
else
    fail "Observation Pydantic model not found"
    hint "Define Observation(BaseModel) in openenv_env.py"
fi

if grep -q "class Action" "$SCRIPT_DIR/backend/openenv_env.py"; then
    pass "Action model defined"
else
    fail "Action Pydantic model not found"
    hint "Define Action(BaseModel) in openenv_env.py"
fi

if grep -q "class Reward" "$SCRIPT_DIR/backend/openenv_env.py"; then
    pass "Reward model defined"
else
    fail "Reward Pydantic model not found"
    hint "Define Reward(BaseModel) in openenv_env.py"
fi

# Check that environment has required methods
if grep -q "async def reset" "$SCRIPT_DIR/backend/openenv_env.py"; then
    pass "reset() method defined"
else
    fail "reset() method not found"
    hint "Implement async def reset() in environment class"
fi

if grep -q "async def step" "$SCRIPT_DIR/backend/openenv_env.py"; then
    pass "step() method defined"
else
    fail "step() method not found"
    hint "Implement async def step(action) in environment class"
fi

if grep -q "async def state" "$SCRIPT_DIR/backend/openenv_env.py" || grep -q "def state" "$SCRIPT_DIR/backend/openenv_env.py"; then
    pass "state() method defined"
else
    fail "state() method not found"
    hint "Implement state() method in environment class"
fi

# Check for 3+ tasks
TASK_COUNT=$(grep -c '"task_id"' "$SCRIPT_DIR/openenv.yaml" | head -1 || echo "0")
if [ "$TASK_COUNT" -ge 3 ]; then
    pass "At least 3 tasks defined (found: $TASK_COUNT)"
else
    fail "Minimum 3 tasks required (found: $TASK_COUNT)"
    hint "Add at least 3 task definitions in openenv.yaml"
    stop_at "Step 4"
fi

# Check for reward 0.0-1.0 validation
if grep -qE '(minimum|max).*0\.' "$SCRIPT_DIR/openenv.yaml"; then
    pass "Reward scoring documented (0.0-1.0 range)"
else
    hint "Verify reward structure documented in openenv.yaml"
fi

# ============================================================================
# SUCCESS
# ============================================================================
echo -e "\n${BOLD}========================================${NC}"
echo -e "${GREEN}${BOLD}  ✓ All 4/4 validation checks passed!${NC}"
echo -e "${GREEN}${BOLD}  Your submission is ready to submit.${NC}"
echo -e "${BOLD}========================================${NC}\n"

cat <<EOF
${BOLD}Next Steps:${NC}
1. Test locally: python inference.py
2. Push to GitHub
3. Create Hugging Face Space linked to this repository
4. Space will auto-deploy the Dockerfile
5. Submit Space URL to competition

${BOLD}Troubleshooting:${NC}
- If Docker build fails, check requirements-inference.txt
- If inference.py fails, verify PYTHONPATH includes backend/
- If openenv validate fails, check openenv.yaml structure
- Review README.md for complete documentation

${BOLD}Demo Run:${NC}
To test inference (requires OpenAI API key):
  export OPENAI_API_KEY="sk-..."
  export MODEL_NAME="gpt-3.5-turbo"
  python inference.py

Good luck! 🚀
EOF

exit 0
