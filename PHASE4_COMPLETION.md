# Phase 4: Frontend Dashboard - Completion Guide

## Overview

Phase 4 adds a real-time monitoring and visualization layer to AutoDevOS. Users can now:
- Submit business ideas to generate websites
- Monitor agent execution in real-time
- View performance metrics and rewards
- Access previously learned strategies
- Track iteration progress

## Architecture

### Frontend Structure

```
frontend/
├── app/
│   ├── page.tsx              # Landing page + job creation
│   ├── dashboard/
│   │   └── [jobId]/
│   │       └── page.tsx      # Real-time job dashboard
│   └── globals.css
├── components/
│   ├── AgentTimeline.tsx     # Real-time activity feed
│   ├── RewardMetrics.tsx     # Boss agent scores visualization
│   ├── StrategyPanel.tsx     # High-reward strategies display
│   └── IterationControl.tsx  # Iteration progress tracker
├── hooks/
│   └── useJobStream.ts       # WebSocket real-time connection hook
└── package.json
```

## Key Components & Features

### 1. Landing Page (`app/page.tsx`)

**Features:**
- Job creation form with prompt input
- Real-time job history (last 10 jobs)
- Status indicators (running, completed, error)
- Job performance scores (overall_reward)
- One-click navigation to job dashboard
- Feature highlights (PM, Architect, Developer workflow)

**API Calls:**
- `POST /api/jobs` - Create new job
- `GET /api/jobs?limit=10` - Fetch job history

### 2. Job Dashboard (`app/dashboard/[jobId]/page.tsx`)

**Layout:**
```
┌─── Agent Timeline ──────┬─ Rewards ─┐
│ (2 cols activity feed)  │ Metrics   │
│                         ├─ Progress │
└─────────────────────────┴───────────┘
┌─ Agent Execution Summary (8 cards) ─┐
│ pm | arch | dev | qa | sec | debt   │
│ seo | boss                           │
└──────────────────────────────────────┘
┌─ High-Reward Strategies Panel ───────┐
│ Clickable agent buttons to filter    │
│ Strategy list (task + output + score)│
└──────────────────────────────────────┘
┌─ Raw Event Log (JSON format) ────────┐
│ Latest 20 events in real-time        │
└──────────────────────────────────────┘
```

**Real-time Updates:**
- WebSocket `/ws/{jobId}` connection via `useJobStream` hook
- Auto-updates for:
  - Agent execution logs
  - Meeting messages
  - Boss agent rewards
  - Strategy storage events
  - Iteration completion

### 3. AgentTimeline Component

**Props:**
```typescript
interface AgentTimelineProps {
  events: JobEvent[];
  currentAgent?: string;
}
```

**Features:**
- Color-coded by agent type (8 agents, 8 colors)
- Event icons (🔄 log, 💬 message, 🏆 reward, 💾 strategy, ✅ complete)
- Latest 20 events with timestamps
- Highlights current agent execution
- Shows iteration and reward scores

**Event Types:**
- `agent_log` - Agent processing log
- `meeting_message` - Team discussion
- `reward` - Boss evaluation (0-10 per agent)
- `strategy_stored` - High-reward strategy saved
- `iteration_complete` - Iteration finished

### 4. RewardMetrics Component

**Props:**
```typescript
interface RewardMetricsProps {
  rewards?: Record<string, number>;
  totalReward?: number;
  currentIteration?: number;
}
```

**Features:**
- Displays boss agent scores (0-10) for each agent
- Color-coded bars (green 8+, yellow 6-7, red <6)
- Overall average score prominent display
- Iteration counter
- Summary statistics (Excellent/Good/Needs work counts)

### 5. StrategyPanel Component

**Props:**
```typescript
interface StrategyPanelProps {
  jobId: string;
  agentType?: string;  // Optional filter
}
```

**Features:**
- Lists high-reward strategies (reward >= 7.0)
- Filterable by agent type via parent dashboard
- Auto-refreshes every 5 seconds
- Shows: agent name, truncated output, reward score, timestamp
- Loads strategies from Phase 3 ChromaDB integration

**API Calls:**
- `GET /api/strategies?jobId={jobId}` - All strategies
- `GET /api/strategies/{agentType}?jobId={jobId}` - Agent-specific

### 6. IterationControl Component

**Props:**
```typescript
interface IterationControlProps {
  currentIteration: number;
  maxIterations?: number;
  isRunning?: boolean;
  onStopClick?: () => void;
}
```

**Features:**
- Visual progress bar (3 iterations max)
- Completed/pending/current iteration colors
- Iteration counter display
- Stop button (when running)
- Completion message (when done)

### 7. useJobStream Hook

**WebSocket Integration:**

```typescript
export function useJobStream(jobId: string) {
  // Returns:
  // {
  //   jobId: string
  //   status: 'running' | 'completed' | 'error' | 'idle'
  //   events: JobEvent[]
  //   currentIteration: number
  //   totalReward: number
  //   isConnected: boolean
  //   clearEvents: () => void
  // }
}
```

**Event Processing:**
- Auto-calculates iteration count from events
- Computes average reward (totalReward = avg of boss agent scores)
- Maintains ordererd event history
- Handles connection loss and reconnection

## Backend Integration

### New API Endpoints

All endpoints prefixed with `/api/`

#### 1. Strategy Retrieval

**GET `/api/strategies`**
- Query params: `jobId`, `agent_type`, `limit` (default 20)
- Returns: List of high-reward strategies with agent, output, reward
- Purpose: Frontend StrategyPanel component

**GET `/api/strategies/{agent_type}`**
- Query params: `jobId`, `limit` (default 10)
- Returns: Agent-specific high-reward strategies
- Purpose: Filtered strategy view

#### 2. Agent Statistics

**GET `/api/agent-stats/{agent_type}`**
- Returns: { count, avg_reward, max_reward } per agent
- Purpose: Performance analytics

#### 3. Memory Management

**POST `/api/cleanup-strategies`**
- Query params: `agent_type` (optional), `min_reward` (default 5.0)
- Returns: Success message with cleanup count
- Purpose: Frontend memory cleanup trigger (optional feature)

### WebSocket Message Format

Events from `/ws/{jobId}`:

```typescript
interface JobEvent {
  type: 'agent_log' | 'meeting_message' | 'reward' | 'strategy_stored' | 'iteration_complete';
  agent?: string;           // e.g. "developer", "pm"
  message?: string;         // Event description
  reward?: Record<string, number>;  // Boss scores: { pm: 8.5, architect: 7.2, ... }
  iteration?: number;       // Current iteration (1-3)
  timestamp: number;        // Unix timestamp
}
```

## Integration Points with Phases 1-3

### Phase 1 (Foundation)
- Uses FastAPI endpoints: `/api/jobs` (POST/GET/LIST)
- Uses PostgreSQL: Job and Reward tables
- Uses Redis pub/sub for event streaming
- Uses WebSocket for real-time updates

### Phase 2 (Orchestration)
- Displays 8 agent execution in timeline
- Shows LangGraph node execution (pm → architect → developer → qa → security → tech_debt → seo → boss → rl)
- Visualizes iteration looping (max 3)
- Displays boss agent evaluation scores

### Phase 3 (RL Memory)
- StrategyPanel retrieves from ChromaDB via rl_engine
- Shows high-reward strategies in UI
- Fetches strategies stored in `{agent_type}_strategies` collections
- Displays reward scores >= 7.0

## Installation & Setup

### Prerequisites
```bash
# Node.js 18+
node --version

# Frontend dependencies already in package.json:
# - next@14.1.0
# - react@18
# - typescript@5
# - tailwind@3.4.1
# - shadcn/ui (components)
# - lucide-react (icons)
```

### Installation
```bash
cd frontend
npm install  # Already done
```

### Run Development Server
```bash
npm run dev
# Runs on http://localhost:3000
# Hot-reload enabled
```

## UI/UX Design

### Color Scheme
- **Background**: Slate 900 (dark mode)
- **Agent Colors**:
  - PM: Blue (#3B82F6)
  - Architect: Purple (#A855F7)
  - Developer: Green (#22C55E)
  - QA: Yellow (#FBBF24)
  - Security: Red (#EF4444)
  - Tech Debt: Orange (#F97316)
  - SEO: Cyan (#06B6D4)
  - Boss: Pink (#EC4899)

### Components Used
- **shadcn/ui**: Card, Button, Badge, Progress
- **lucide-react**: Icons (ArrowLeft, Download, RefreshCw, Loader, Zap)
- **Tailwind CSS**: Utilities for layout and styling

### Responsive Layout
- **Mobile**: Single column (timeline stacked)
- **Tablet**: 2-column (timeline + right sidebar)
- **Desktop**: 3-column + full width sections

## Testing Phase 4

### 1. Frontend Component Testing
```bash
# Test individual components can import/render
npm run build
```

### 2. End-to-End Workflow
1. Start backend: `docker-compose up -d backend`
2. Start frontend: `npm run dev`
3. Submit job at http://localhost:3000
4. Watch real-time updates in dashboard
5. Verify WebSocket connection (DevTools > Network > WS)
6. Check strategy panel loads data
7. Verify agent timeline updates

### 3. API Integration Testing
```bash
# Test strategy endpoints
curl http://localhost:8000/api/strategies
curl http://localhost:8000/api/strategies/developer
curl http://localhost:8000/api/agent-stats/developer
```

## Known Limitations & Future Enhancements

### Current Limitations
- ✅ Job creation works
- ✅ Real-time updates via WebSocket
- ✅ No authentication (localhost only)
- ✅ Strategy display is read-only

### Phase 5 Enhancements
1. **Site Preview** - Embedded iframe showing generated HTML
2. **Code Export** - Download generated HTML/CSS/JS files
3. **Feedback Loop** - User can rate iteration results
4. **Strategy Editor** - Manually edit and re-submit strategies
5. **Analytics Dashboard** - Historical performance graphs
6. **Authentication** - JWT tokens for multi-user
7. **Error Handling** - Detailed error messages + recovery
8. **Mobile App** - React Native version

## Performance Considerations

### Optimizations Applied
- ✅ Component memo-ization (React.memo on event items)
- ✅ Event history capped at 20 latest events
- ✅ Strategy panel auto-refreshes (5 sec interval)
- ✅ WebSocket reconnection logic
- ✅ Lazy loading (Next.js automatic)

### Bandwidth
- WebSocket: ~1KB per event (text-based JSON)
- Strategy API: ~5-10KB per request
- Estimated: ~50KB/min during job execution

## Debugging

### Enable WebSocket Logging
```typescript
// In useJobStream.ts
ws.current.onmessage = (event) => {
  console.log('📨 WebSocket message:', event.data);  // Add this
  // ... rest of code
}
```

### Check Browser DevTools
1. **Network > WS**: WebSocket connection status
2. **Console**: Any React errors or warnings
3. **Application > Local Storage**: Job ID (if added)
4. **Performance**: Component render times

## File Structure Summary

**Created Files:**
- `frontend/hooks/useJobStream.ts` - WebSocket hook (150 lines)
- `frontend/components/AgentTimeline.tsx` - Activity timeline (120 lines)
- `frontend/components/RewardMetrics.tsx` - Score visualization (130 lines)
- `frontend/components/StrategyPanel.tsx` - Strategy list (140 lines)
- `frontend/components/IterationControl.tsx` - Progress tracker (80 lines)
- `frontend/app/dashboard/[jobId]/page.tsx` - Main dashboard (280 lines)
- `frontend/app/page.tsx` - Landing page (updated, 240 lines)
- `backend/api/strategies.py` - Strategy endpoints (180 lines)
- `backend/main.py` - Updated with router (3 lines added)

**Total New Code**: ~1,200 lines

## Next Steps (Phase 5)

### Priority 1: Polish
- Add error boundaries
- Improve loading states
- Add toast notifications

### Priority 2: Features
- Site preview iframe
- Code export functionality
- Iteration feedback form

### Priority 3: Production
- Authentication
- Rate limiting
- Logging/monitoring
- Email notifications

## Success Criteria ✅

- ✅ Landing page displays + accepts job submissions
- ✅ Real-time dashboard shows agent execution
- ✅ WebSocket receives events (agent_log, reward, strategy_stored)
- ✅ Timeline shows all agents in execution order
- ✅ Rewards display with color-coded scores
- ✅ Iteration progress tracks accurately
- ✅ Strategy panel loads high-reward strategies
- ✅ Job history displays in landing page
- ✅ All UI components render without errors
- ✅ Responsive on mobile/tablet/desktop

## Completion Status

**Phase 4 Complete**: All core components, hooks, API endpoints, and integration finished.

**Time to Deploy:** ~2 hours (Docker Compose rebuild + testing)
