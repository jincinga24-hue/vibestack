#!/bin/bash
set -e

echo "🚀 Installing vibestack..."
echo ""

# 1. Install skills
echo "📦 Installing skills to ~/.claude/skills/..."
mkdir -p ~/.claude/skills
cp -r skills/vibe-prep ~/.claude/skills/
cp -r skills/vibe-harness ~/.claude/skills/
cp -r skills/roast-mvp ~/.claude/skills/
echo "   ✅ /vibe-prep"
echo "   ✅ /vibe-harness"
echo "   ✅ /roast-mvp"
echo ""

# 2. Install roastmymvp CLI
echo "🔧 Installing roastmymvp CLI..."
cd roastmymvp
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]" --quiet
echo "   ✅ roastmymvp CLI installed"
echo ""

# 3. Install Playwright
echo "🎭 Installing Playwright browser..."
playwright install chromium --quiet 2>/dev/null || playwright install chromium
echo "   ✅ Chromium installed"
echo ""

# 4. Initialize gene pool
echo "🧬 Initializing gene pool..."
roastmymvp evolve
echo ""

# Done
echo "============================================"
echo "  vibestack installed successfully! 🎉"
echo "============================================"
echo ""
echo "  Usage (in Claude Code):"
echo "    /vibe-prep      — Prepare your project"
echo "    /vibe-harness   — Autonomous coding loop"
echo "    /roast-mvp      — Roast your MVP"
echo ""
echo "  Or use the CLI directly:"
echo "    source roastmymvp/.venv/bin/activate"
echo "    roastmymvp run https://your-app.com --mode gauntlet --real"
echo ""
