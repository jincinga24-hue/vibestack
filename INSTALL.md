# Installation

## One-Line Install

```bash
git clone https://github.com/jincinga24-hue/vibestack.git && cd vibestack && bash install.sh
```

## What It Installs

1. **30 Claude Code skills** → `~/.claude/skills/`
2. **roastmymvp CLI** → Python venv in `roastmymvp/.venv/`
3. **Chromium** → for Playwright browser testing
4. **Gene pool** → initialized with 25 personas (5 VCs + 20 community)

## Prerequisites

| Requirement | Why | Install |
|-------------|-----|---------|
| Claude Code | Runtime for all skills | `npm install -g @anthropic-ai/claude-code` |
| Python 3.12+ | roastmymvp CLI | `brew install python` |
| gstack (recommended) | /qa, /review, /ship, /browse | [github.com/garrytan/gstack](https://github.com/garrytan/gstack) |

## Verify

```bash
# In Claude Code, these should appear:
/vibe-prep
/vibe-harness
/roast-mvp
/validate-idea

# CLI should work:
cd vibestack/roastmymvp && source .venv/bin/activate
roastmymvp --help
roastmymvp pool
```

## Uninstall

```bash
# Remove skills
for skill in validate-idea vibe-prep vibe-harness roast-mvp; do
  rm -rf ~/.claude/skills/$skill
done

# Remove ECC skills installed by vibestack
for skill in tdd-workflow python-testing e2e-testing verification-loop coding-standards python-patterns security-review security-scan api-design frontend-patterns backend-patterns deployment-patterns database-migrations agentic-engineering autonomous-loops continuous-agent-loop cost-aware-llm-pipeline agent-harness-construction eval-harness content-engine article-writing investor-materials investor-outreach market-research continuous-learning-v2 search-first; do
  rm -rf ~/.claude/skills/$skill
done
```
