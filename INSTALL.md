# Installation

## Prerequisites

- [Claude Code](https://claude.ai/code) installed (`claude` CLI available)
- Python 3.12+
- Node.js 18+ (for EvoMap Evolver, optional)

## One-Line Install

```bash
git clone https://github.com/YOUR_USERNAME/vibestack.git && cd vibestack && bash install.sh
```

## Manual Install

### 1. Install Skills (slash commands)

```bash
# Copy skills to Claude Code
cp -r skills/vibe-prep ~/.claude/skills/
cp -r skills/vibe-harness ~/.claude/skills/
cp -r skills/roast-mvp ~/.claude/skills/
```

### 2. Install roastmymvp CLI

```bash
cd roastmymvp
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
```

### 3. Initialize Gene Pool

```bash
source roastmymvp/.venv/bin/activate
roastmymvp evolve
roastmymvp pool
```

### 4. (Optional) Install EvoMap Evolver

```bash
cd roastmymvp
npm install @evomap/evolver@latest
```

## Verify Installation

```bash
# Check skills are loaded (in Claude Code)
# Type /vibe-prep, /vibe-harness, /roast-mvp — they should appear

# Check CLI
source roastmymvp/.venv/bin/activate
roastmymvp --help

# Check gene pool
roastmymvp pool
```

## Uninstall

```bash
rm -rf ~/.claude/skills/vibe-prep
rm -rf ~/.claude/skills/vibe-harness
rm -rf ~/.claude/skills/roast-mvp
```
