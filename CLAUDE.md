# vibestack

## What This Is

Full vibe coding pipeline: `/vibe-prep` → `/vibe-harness` → `/roast-mvp`

## Workflow

1. **Start with an idea** → type `/vibe-prep`
2. **Build it autonomously** → type `/vibe-harness`
3. **Get brutally roasted** → type `/roast-mvp`

## Rules

- Always validate before building. Never skip `/vibe-prep`.
- The harness runs 15 autonomous cycles. Don't interrupt unless it's stuck.
- Roast mode uses the `roastmymvp` CLI. Activate venv first: `source roastmymvp/.venv/bin/activate`
- After every roast, rate critiques with `roastmymvp feedback` to evolve the gene pool.
- Use `--real` flag for community testing — real Reddit/HN personas are better than defaults.
- Use `--github` flag for VC mode — VCs will research you and call out bluffs.

## Prerequisites

- [gstack](https://github.com/garrytan/gstack) installed (for /qa, /review, /ship, /browse)
- Python 3.12+ (for roastmymvp CLI)
- Claude Code with claude CLI available
