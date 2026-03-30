# Harness Engineering Guide

How the autonomous coding loop works, how to tune it, and what to do when things go wrong.

---

## How `/vibe-harness` Works

The harness runs a loop:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  READ    │────▶│  CODE    │────▶│ EVALUATE │
│  state   │     │  a       │     │  what    │
│  + PRD   │     │  feature │     │  was     │
│          │     │          │     │  built   │
└──────────┘     └──────────┘     └─────┬────┘
     ▲                                  │
     │           ┌──────────┐           │
     └───────────│  DECIDE  │◀──────────┘
                 │          │
                 │ continue │
                 │ fix      │
                 │ done     │
                 └──────────┘
```

Each cycle:
1. **Read** — Loads `HARNESS-STATE.md`, `docs/PRD.md`, `docs/UI-DESIGN.md`
2. **Code** — Implements the next feature or fixes a bug
3. **Evaluate** — Scores the work (0-10) and checks if it actually runs
4. **Decide** — Continue to next feature, fix current issues, or declare done

State survives between sessions via `HARNESS-STATE.md`.

---

## Typical Pacing

Don't rush. A working MVP usually takes 20-40 cycles, not 15.

| Cycles | What should happen |
|--------|-------------------|
| 1-5 | Core feature #1 — end-to-end, working, tested |
| 6-10 | Core feature #2 + polish feature #1 |
| 11-15 | Core feature #3 + integration + edge cases |
| 16-25 | Polish, bug fixes, UX refinement |
| 25+ | Final testing, cleanup, ready for real users |

**Anti-patterns:**
- Rushing to add features when the current one is broken
- Declaring "done" when it only works on the happy path
- Stopping because context window is getting full (use compaction)

---

## When It Gets Stuck

### Score plateaued (same issues every cycle)

The evaluator keeps flagging the same bugs but the coder isn't fixing them. This happens when the context is polluted with failed attempts.

**Fix:** Context reset. Let the current session end, then start a new one. The new session reads `HARNESS-STATE.md` and picks up where you left off with fresh eyes.

### Score dropping

Something broke and the coder is making it worse.

**Fix:**
1. Check `git log` — find the last good commit
2. Reset to it: `git checkout <good-commit> -- .`
3. Update `HARNESS-STATE.md` with what went wrong
4. Resume the harness

### Build won't compile

The coder introduced a dependency conflict or syntax error it can't resolve.

**Fix:** Run the build manually, read the error, and paste it into Claude Code. Sometimes a human eye catches what the loop missed.

### Context window full

The harness has been running for many cycles and Claude is running out of context.

**Fix:** Two options:
- **Compaction** — compress history, stay in the same session. Good when things are going well.
- **Context reset** — end session, start fresh. Better after a pivot or repeated failures. The harness is designed for this — `HARNESS-STATE.md` + git history = structured handoff.

**When to use which:**

| Situation | Use |
|-----------|-----|
| Score trending up, no issues | Compaction |
| Same bug keeps recurring | Context reset |
| After a major pivot | Context reset |
| Every ~10 cycles | Context reset (preventive) |

---

## Files the Harness Creates

| File | Purpose |
|------|---------|
| `HARNESS-STATE.md` | Current state — what's done, what's next, scores |
| `HARNESS-ANALYSIS.md` | Final analysis after all cycles complete |
| `init.sh` | Dev environment setup script (auto-generated) |
| `harness-dashboard.html` | Live progress dashboard (opens in browser) |

---

## Tuning the Harness

### More cycles

The default is 15 cycles. For complex projects, you can tell Claude to keep going:

> "Continue the harness for 10 more cycles, focus on polish and edge cases"

### Focus areas

If the harness is building features you don't want:

> "Stop adding new features. Spend the next 5 cycles on bug fixes and mobile responsiveness only."

### Manual intervention

You can intervene at any point:
- Edit `HARNESS-STATE.md` to change priorities
- Push a commit with a manual fix — the harness will pick it up next cycle
- Type "pause" to stop and review, then "continue" to resume

---

## HARNESS-STATE.md Format

This is the harness's memory. It looks like:

```markdown
# Harness State

## Project
- Name: My App
- Tech: Next.js + Tailwind
- PRD: docs/PRD.md

## Progress
- Cycle: 8/15
- Score: 7/10
- Features complete: auth, dashboard
- Features remaining: settings page, export

## Current Focus
Settings page — user profile editing

## Issues
- [ ] Dashboard chart doesn't render on mobile
- [ ] Auth redirect loop on expired sessions

## History
- Cycle 7: Added dashboard charts (score: 7)
- Cycle 6: Fixed auth flow (score: 6→7)
- Cycle 5: Implemented dashboard layout (score: 5)
```

If you need to reset, just edit this file and the next session picks up from your edits.

---

## After the Harness

When the harness finishes, you have a working prototype. Next steps:

1. **Run `/roast-mvp`** — get honest feedback before showing anyone
2. **Fix the top 3 issues** from the roast
3. **Run the harness again** with focused goals: "Fix these 3 issues"
4. **Roast again** — see if the score improved
5. **Ship it** when you're happy (use gstack's `/ship` if installed)

The cycle is: **build → roast → fix → roast → ship**.
