---
name: vibe-harness
version: 2.0.0
description: |
  MANUAL TRIGGER ONLY: invoke only when user types /vibe-harness.
  Autonomous vibe coding pipeline: validate idea → 15 generate/evaluate cycles → analysis.
  Maintains state in HARNESS-STATE.md. Produces HARNESS-ANALYSIS.md when done.
allowed-tools:
  - Read
  - Write
  - Edit
  - Agent
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - WebSearch
  - WebFetch
  - Skill
---

# /vibe-harness — Autonomous Vibe Coding Pipeline

## Overview

This is the **autonomous coding loop**. It assumes `/vibe-prep` was already run.
All cycles are pure coding — PRD, UI design, and scaffold are already done.

The dashboard opens automatically and tracks progress in real time.

Language: Match the user's language.

## MVP Pacing Philosophy

**A small deliverable MVP typically takes 20-40 cycles**, not 15. Do NOT rush to finish.

### Anti-Patterns to AVOID:
1. **Speed over correctness** — Never skip bug fixes to add the next feature. A broken feature is worse than no feature.
2. **Untested code** — Every feature must be manually runnable before moving on. The Evaluator should verify this.
3. **Context anxiety stopping** — Do NOT stop coding just because the context window is getting full. Use compaction, reset agents, or checkpoint and continue. The harness is designed to survive context resets via `HARNESS-STATE.md`.
4. **Stale documentation** — `docs/PRD.md`, `docs/ARCHITECTURE.md`, and `CLAUDE.md` MUST be updated in real-time as the codebase evolves. If a cycle changes the folder structure, adds a library, or completes a feature, the docs must reflect it IN THAT CYCLE.
5. **Premature completion** — Don't declare COMPLETE until ALL MVP features are working AND tested. Partial implementations with green scores are not done.
6. **Self-evaluation bias** — The evaluator tends to overestimate quality. Counter this by requiring real verification (browser checks, build tests, E2E) before scoring. A "working" feature often has untested edge cases.

### Context Reset vs Compaction (Anthropic Protocol)

These are **different tools** for different situations:

- **Compaction** = compress conversation history within the same session. Preserves continuity but carries accumulated anxiety and pollution. Use when the task is going well and you just need more room.
- **Context Reset** = end session, start a fresh agent with clean context. Use `HARNESS-STATE.md` + git history for structured handoff. More expensive but gives a truly clean starting state.

**When to use which:**
- Score trending up, no recurring bugs → **Compaction** is fine
- Score plateaued, evaluator keeps flagging same issues → **Context Reset** (fresh eyes)
- After REFACTOR or PIVOT verdict → **Context Reset** (break out of bad patterns)
- Every 10 cycles → Consider a **Context Reset** regardless

### Correct Pacing:
- **Cycles 1-5:** Core feature #1 end-to-end, working and tested
- **Cycles 6-10:** Core feature #2, polish feature #1 issues
- **Cycles 11-15:** Core feature #3, integration, edge cases
- **Cycles 16-25:** Polish, bug fixes, share flow, UX refinement
- **Cycles 25+:** Final testing, cleanup, ready for real users

---

## PRE-FLIGHT CHECK

Before starting, verify that `/vibe-prep` was completed:

1. Check for `docs/PRD.md` — if missing, tell user: **"No PRD found. Run `/vibe-prep` first to set up the project."** Stop.
2. Check for `docs/UI-DESIGN.md` — if missing, warn but continue.
3. Check for `VALIDATION-REPORT.md` — read it to extract `mvp_features`, `success_metric`, `kill_metric`.
4. Check for `CLAUDE.md` — read project guidelines.

If PRD exists, extract: idea name, MVP features, tech stack. Continue to launch.

### Generate init.sh (Anthropic Protocol)

Create `init.sh` in the project root — a deterministic startup script that any session can run to get the dev environment ready:

```bash
cat > init.sh << 'INITEOF'
#!/bin/bash
set -e

echo "🔧 Setting up dev environment..."

# Install dependencies
if [ -f "package.json" ]; then
  npm install 2>/dev/null || yarn install 2>/dev/null || pnpm install 2>/dev/null
elif [ -f "requirements.txt" ]; then
  pip install -r requirements.txt 2>/dev/null
elif [ -f "go.mod" ]; then
  go mod download 2>/dev/null
fi

# Validate required env vars
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
  echo "⚠️  No .env file found. Copying from .env.example"
  cp .env.example .env
fi

# Start dev server (detect framework)
if grep -q "next" package.json 2>/dev/null; then
  echo "Starting Next.js dev server..."
  npm run dev &
elif grep -q "vite" package.json 2>/dev/null; then
  echo "Starting Vite dev server..."
  npm run dev &
elif [ -f "manage.py" ]; then
  echo "Starting Django dev server..."
  python manage.py runserver &
fi

echo "✅ Dev environment ready"
INITEOF
chmod +x init.sh
```

Customize the script based on the actual tech stack from the PRD. The key principle: **any new session should be able to run `./init.sh` and have a working environment without guessing.**

### Generate Feature Checklist (Anthropic Protocol)

Break each MVP feature into 10-20 granular sub-features and write `FEATURES.json`:

```json
{
  "features": [
    {"id": "map-01", "parent": "Interactive Map", "name": "Render base map with tiles", "status": "FAIL"},
    {"id": "map-02", "parent": "Interactive Map", "name": "Display restaurant pins on map", "status": "FAIL"},
    {"id": "map-03", "parent": "Interactive Map", "name": "Click pin shows popup with name", "status": "FAIL"},
    {"id": "map-04", "parent": "Interactive Map", "name": "Zoom to pin on sidebar click", "status": "FAIL"},
    {"id": "map-05", "parent": "Interactive Map", "name": "Pin clustering at low zoom", "status": "FAIL"},
    ...
  ]
}
```

Rules:
- Start ALL features as `"FAIL"`
- Generator can ONLY change status to `"PASS"` — never delete or edit feature definitions
- Evaluator verifies PASS claims via real testing — reverts to FAIL if verification fails
- Target 30-50 sub-features for a typical 3-feature MVP
- This prevents premature "DONE" claims — a feature is DONE only when ALL its sub-features are PASS

### Initialize Live Log

Create `HARNESS-LIVE.md` in the project root. This file is updated in real-time during each cycle so the dashboard can show live file activity:

```bash
echo "# Live Activity" > HARNESS-LIVE.md
echo "" >> HARNESS-LIVE.md
echo "Waiting for first cycle..." >> HARNESS-LIVE.md
```

### Launch Dashboard

Launch the dashboard server and open it in the browser:
```bash
cp ~/.claude/skills/vibe-harness/dashboard.html ./harness-dashboard.html
# Kill any existing dashboard server
lsof -ti:9999 2>/dev/null | xargs kill 2>/dev/null
sleep 0.5
# Start server from project dir in background
cd "$(pwd)" && python3 -m http.server 9999 &>/dev/null &
sleep 1
open "http://localhost:9999/harness-dashboard.html"
```
Tell the user: "Dashboard is live at http://localhost:9999/harness-dashboard.html — click **Auto-refresh** to watch progress in real time."

### Step 1e: Initialize state

Write `HARNESS-STATE.md` in the project root:

```markdown
# Harness State

## Config
- **Idea:** [one-liner from validation]
- **MVP Features:** [3 features]
- **Success Metric:** [metric]
- **Kill Metric:** [metric]
- **Tech Stack:** [stack]
- **Total Cycles:** 0
- **Current Phase:** GENERATING

## Cycle Log
```

---

## STAGE 2: Vibe Coding Loop

Run cycles continuously (default batch: 15 at a time, checkpoint and ask user). For EACH cycle:

### Step 2a: Session Startup Protocol (Anthropic Protocol)

Every cycle (and especially after a context reset) MUST start with this checklist:

```
1. Run `pwd` to confirm working directory
2. Run `./init.sh` to ensure dev environment is ready
3. Read `HARNESS-STATE.md` — extract last 3 cycles of feedback, current progress, recent verdicts
4. Read `FEATURES.json` — count PASS vs FAIL features, pick highest-priority FAIL feature
5. Read `git log --oneline -10` — understand what was committed recently
6. Run smoke test: start dev server, verify app loads without errors
7. Select the single feature/sub-feature to work on this cycle
```

This startup sequence ensures every session — whether fresh or after compaction — begins from a known-good state. It directly counters **context anxiety** by grounding the agent in verified reality rather than stale memory.

### Step 2b: Generator Phase

Launch an **Agent** with this prompt:

```
You are a vibe coder. Your job is to write working code FAST.

## IMPORTANT: Live Activity Log
Before each file read/write, append a line to HARNESS-LIVE.md so the dashboard shows real-time activity:
```bash
echo "$(date +%H:%M:%S) | Cycle [N] | [action] | [filepath]" >> HARNESS-LIVE.md
```
Examples:
- `echo "14:32:01 | Cycle 1 | Reading | docs/PRD.md" >> HARNESS-LIVE.md`
- `echo "14:32:15 | Cycle 1 | Writing | src/components/Header.tsx" >> HARNESS-LIVE.md`
- `echo "14:33:02 | Cycle 1 | Installing | npm install leaflet" >> HARNESS-LIVE.md`
- `echo "14:33:45 | Cycle 1 | Testing | npm run dev" >> HARNESS-LIVE.md`

Do this for EVERY significant file operation. The dashboard polls this file every 2 seconds.

## IMPORTANT: Read Project Guidelines First
- Read CLAUDE.md in the project root if it exists. Follow ALL instructions in it.
- These guidelines override the vibe coding principles below where they conflict.

## IMPORTANT: Official Docs Before Guessing
- Before using ANY library or framework API, check the official documentation first.
- Do NOT guess function signatures, config options, or API patterns from memory.
- Use WebFetch to read docs if unsure. Wrong API calls waste entire cycles.

## Vibe Coding Principles
- Start with the simplest thing that works
- One feature or major improvement per cycle
- ALWAYS leave the app in a runnable state
- Prefer libraries over hand-rolled code
- No premature abstraction — copy-paste is fine for now
- If stuck for more than 2 minutes on an approach, try a different one
- Commit to a file structure early, extend it later
- Write brief inline comments explaining WHY, not WHAT

## Context
- Idea: [idea]
- Tech Stack: [stack]
- MVP Features: [features]
- Cycle: [N] of 15
- Previous feedback: [last 3 cycles of evaluator feedback]
- Files changed so far: [from state]

## Your Task for Cycle [N]

PRD, UI design, and project scaffold are already done by the user in Stage 1. Read docs/PRD.md, docs/UI-DESIGN.md, and docs/ARCHITECTURE.md for context. Your job is to CODE.

### Cycle 1: Implement core feature #1
- Read the PRD and UI design docs. Follow them exactly.
- Implement the first and most important MVP feature end-to-end
- Connect frontend to backend if applicable
- Make it runnable and demonstrable

### Cycles 2-15: Build & Iterate
[If REFACTOR verdict]: Do NOT add new features. Fix the issues listed in the evaluator feedback.
[If PIVOT verdict]: The current approach is failing. Try a fundamentally different approach to the same feature.
[Otherwise]: Implement the next MVP feature or improve an existing one based on feedback.
Always refer back to docs/PRD.md and docs/UI-DESIGN.md for what to build.

## MANDATORY: Update Living Docs
After coding, check if any of these docs need updating:
- `docs/PRD.md` — mark features as DONE, update scope changes
- `docs/ARCHITECTURE.md` — update folder structure, new libraries, data flow changes
- `CLAUDE.md` — update conventions, new decisions, file structure changes
- `docs/REFERENCE.md` — update if new patterns established
- `docs/QUALITY-GATES.md` — update if new checks needed
If ANY of these are stale after your changes, update them. This is NOT optional.

## MANDATORY: Git Commit as Recovery Point (Anthropic Protocol)
After coding, create a git commit with a descriptive message:
```bash
git add -A
git commit -m "cycle [N]: [1-line summary of what was done]"
```
This commit is a recovery point. If a future cycle breaks something, we can revert to this commit. NEVER skip this step.

## MANDATORY: Update FEATURES.json
For any sub-features you completed this cycle, change their status from "FAIL" to "PASS" in FEATURES.json. Only mark PASS if the feature is genuinely working — the Evaluator will verify and revert false claims.

## Output
After you're done, list:
1. Files created/modified
2. What you did in 1-2 sentences
3. How to run the app (if changed)
4. Docs updated (list which docs were updated and why, or "none needed")
5. Git commit hash for this cycle
6. Sub-features marked PASS this cycle
```

### Step 2c: Evaluator Phase

Launch a separate **Agent** with this prompt:

```
You are a strict code evaluator. Score the current codebase.

Read all source files in the project (ignore node_modules, __pycache__, .git, etc.).

## Bug Reporting Format
When you find bugs, report each one as:
- **Expected:** [what should happen]
- **Actual:** [what happens instead]
- **Repro:** [minimal steps to trigger it]
This format goes into the feedback so the Generator can fix efficiently.

## Scoring Rubric (each 0-10)

1. **Functionality (30%)** — Does the code do what it claims? Any obvious bugs?
2. **MVP Coverage (30%)** — How many of these features are working: [3 MVP features]
   - 0/3 = 0, 1/3 = 3, 2/3 = 6, 3/3 = 10
3. **Runnability (20%)** — Can a user actually start and use this right now? Dependencies installed? Entry point clear?
4. **Code Quality (10%)** — Readable? No hardcoded secrets? Basic error handling?
5. **Progress Delta (10%)** — Compared to previous cycle scores: [previous scores], how much improved?

## Calculate
- **Overall Score** = (Functionality × 0.3) + (MVP Coverage × 0.3) + (Runnability × 0.2) + (Quality × 0.1) + (Delta × 0.1)

## MANDATORY MINIMUM: 15 CYCLES
**The first 15 cycles are MANDATORY. No verdict can stop the loop before cycle 15.** Even if all features are done and the score is high, the evaluator MUST output CONTINUE or POLISH for cycles 1-14. COMPLETE is only valid at cycle 15 or later.

This exists because:
- AI evaluators inflate scores — a "working" feature often has untested edge cases
- 4 cycles is never enough for a real MVP — polish, edge cases, and UX matter
- Early COMPLETE creates a false sense of done-ness

## Verdict Rules

**Cycles 1-14 (COMPLETE is BANNED):**
- Score >= 8.0 AND MVP = 10: → `POLISH` (features seem done, but keep polishing)
- Score >= 5.0: → `CONTINUE`
- Score 3.0-4.9: → `REFACTOR`
- Score < 3.0: → `PIVOT`

**Cycles 15+ (COMPLETE is allowed):**
- Score >= 9.0 AND MVP = 10 AND delta from previous cycle <= 0.1: → `COMPLETE`
- Score >= 8.0 AND MVP = 10: → `POLISH`
- Score >= 5.0: → `CONTINUE`
- Score 3.0-4.9: → `REFACTOR`
- Score < 3.0: → `PIVOT`

**POLISH verdict behavior:** When verdict is POLISH, the Generator should focus on:
- Fixing ALL evaluator feedback items (not just some)
- Edge cases, error handling, boundary checks
- UX polish (animations, transitions, responsive layout, small device support)
- Code cleanup (dead code, duplication, naming)
- Testing: manually verify each feature works end-to-end
- Do NOT add new features — only refine existing ones

## Strict Scoring Guidelines
Evaluators MUST score harshly. Inflation kills quality.
- **Functionality 8+** requires: zero known bugs, all edge cases handled, error states covered
- **Functionality 6-7** is appropriate when: features work in happy path but have known issues
- **MVP Coverage 10** requires: ALL features fully working with no caveats, not "implemented but untested"
- **Runnability 8+** requires: can be run by a NEW person with zero guidance beyond README/docs
- **A score above 9.0 should be rare.** It means production-ready quality. Most MVPs plateau at 8.0-8.5.

## Output
Provide:
1. Score breakdown (each dimension)
2. Overall score
3. Verdict
4. Feedback: exactly 5 bullet points of specific, actionable improvements for the next cycle
5. MVP feature status: [feature] → DONE / PARTIAL / NOT_STARTED
```

### Step 2d: Update State

Append to `HARNESS-STATE.md`:

```markdown
### Cycle [N]
- **Generator Action:** [summary]
- **Files Changed:** [list]
- **Scores:** Functionality=[X], MVP=[X], Runnability=[X], Quality=[X], Delta=[X]
- **Overall Score:** [X.X]
- **Verdict:** [CONTINUE/REFACTOR/PIVOT/COMPLETE/STOP]
- **Feedback:**
  1. [item]
  2. [item]
  3. [item]
  4. [item]
  5. [item]
- **MVP Status:** [feature1]=DONE/PARTIAL/NOT_STARTED, [feature2]=..., [feature3]=...
```

Update the header: increment `Total Cycles`, update `Current Phase`.

### Step 2e: Early Exit Checks

**Cycles 1-14: NO EARLY EXIT.** Always continue. The only exception is 3 consecutive PIVOT verdicts.

**Cycles 15+:**
- **COMPLETE:** Score >= 9.0 AND MVP = 10 AND delta <= 0.1 → Break loop → Stage 3 with success
- **POLISH:** Score >= 8.0 AND MVP = 10 but delta > 0.1 → Continue loop
- **3 consecutive PIVOT verdicts:** Set verdict to `STOP`. Break loop → Stage 3 with failure
- **Kill metric triggered:** If evaluator notes the kill metric condition is met → STOP
- **Score plateau at < 9.0:** If 3 consecutive cycles have delta <= 0.1 but score < 9.0 → Ask user whether to continue or stop

### Step 2f: After Cycle 15

Use `AskUserQuestion`:

> **15 cycles complete.** Check `HARNESS-STATE.md` for full progress.
>
> Current score: [X.X] | MVP: [X/3 features done]
>
> Options:
> (a) Run 15 more cycles
> (b) Run N more cycles (specify N)
> (c) Stop and analyze
> (d) Give direction for next cycles

- (a): Continue loop for 15 more
- (b): Continue for N cycles
- (c): Proceed to Stage 3
- (d): Incorporate direction into Generator context, continue

---

## STAGE 3: Analysis

Generate `HARNESS-ANALYSIS.md` in the project root:

```markdown
# Vibe Harness Analysis Report

**Date:** [today's date]
**Idea:** [one-liner]
**Total Cycles Run:** [N]
**Exit Reason:** COMPLETE | KILLED | PAUSED_BY_USER

## Score Trajectory
| Cycle | Score | Verdict |
|-------|-------|---------|
| 1 | [X.X] | [verdict] |
| ... | ... | ... |

## Feature Status
| Feature | Status | Notes |
|---------|--------|-------|
| [feat 1] | DONE/PARTIAL/NOT_STARTED | [details] |
| [feat 2] | ... | ... |
| [feat 3] | ... | ... |

## Is the Prototype Working?
[Can a user run this right now? What works? What doesn't?]

## Is the MVP Complete?
[Assessment against success metric: "[success_metric]"]
[X/3 features implemented. Missing: ...]

## Kill Metric Check
Kill metric: "[kill_metric]"
[Is it triggered? Why or why not?]

## What the Evaluator Flagged Most
[Top 3 recurring themes from evaluator feedback across all cycles]

## Recommendations
1. [Most impactful next step]
2. [Second priority]
3. [Third priority]

## Next Actions
- [ ] [Specific action items to complete the MVP]
- [ ] [Or pivot directions if killed]
```

### Auto-generate PROGRESS.md

After writing the analysis, generate `PROGRESS.md` in the project root — a human-readable summary of the entire workflow:

```markdown
# Project Progress: [Idea Name]

**Generated:** [date]
**Total Cycles:** [N]
**Status:** COMPLETE / IN PROGRESS / KILLED

---

## Timeline

### Prep Phase (vibe-prep)
- Idea validated: [date]
- PRD written: [date]
- Architecture designed: [date]
- Project scaffolded: [date]

### Coding Phase (vibe-harness)
- Started: [date]
- Cycles completed: [N]
- Exit reason: [COMPLETE/KILLED/PAUSED]

## Feature Status

| Feature | Status | Cycle Completed |
|---------|--------|-----------------|
| [feat 1] | DONE/PARTIAL/NOT_STARTED | Cycle [N] |
| [feat 2] | ... | ... |
| [feat 3] | ... | ... |

## Score Progression
- Start: [cycle 1 score]
- End: [final score]
- Trend: [improving/plateauing/declining]

## Key Milestones
1. Cycle [N]: [first feature working]
2. Cycle [N]: [second feature working]
3. ...

## Files Created
[list all project files with brief descriptions]

## What Works Now
[bullet list of working functionality]

## What's Left
[bullet list of remaining work]

## How to Run
[commands to run the app]

## Next Steps
1. [most important next action]
2. [second priority]
3. [third priority]
```

After writing the analysis and progress report, print a summary to the user and ask:

> **Analysis complete.** See `HARNESS-ANALYSIS.md`.
>
> [1-2 sentence summary: working or not, what's done, what's missing]
>
> Want to: (a) Continue vibe coding, (b) Review and refine, (c) Done for now?

---

## Rules

1. **Never skip the validation gate.** Even for "simple" ideas.
2. **Generator and Evaluator are SEPARATE agents.** Never combine them — the evaluator must be independent.
3. **State file is append-only for cycle logs.** Never rewrite previous cycles. Only update the header counters.
4. **Last 3 cycles only for context.** Do not pass all 15 cycles to Generator/Evaluator — keep context lean.
5. **Runnable state is non-negotiable.** If the Generator leaves the app broken, the Evaluator gives REFACTOR.
6. **Match the user's language.** Chinese in, Chinese out. English in, English out.
7. **Always produce the analysis report.** Even on early STOP/KILL.
8. **Human checkpoint at cycle 15.** Never run more than 15 cycles without asking.
9. **Each Agent call should use `model: "sonnet"` for Generator and Evaluator** to keep costs reasonable. Use opus only for the analysis stage.
10. **The vibe coding principles override normal coding rules** (from ~/.claude/rules/) during Generation. Speed > perfection. The Evaluator enforces quality.
11. **Living docs are mandatory.** PRD, ARCHITECTURE, and CLAUDE.md must be updated in every cycle where relevant changes occur. Stale docs = AI confusion in later cycles.
12. **No premature stopping.** Do NOT stop because context is getting large. Use HARNESS-STATE.md to survive context resets. A typical small MVP takes 20-40 cycles.
13. **No skipping bugs for speed.** Fix bugs before adding new features. A broken feature is worse than no feature.
14. **PROGRESS.md is auto-generated** at the end of the workflow (Stage 3). It summarizes the entire journey from prep to coding completion.
