#!/bin/bash
set -e

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║         vibestack installer          ║"
echo "  ║  idea → build → roast in one session ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# 1. Install all skills
echo "📦 Installing skills to ~/.claude/skills/..."
mkdir -p ~/.claude/skills
count=0
for skill_dir in skills/*/; do
  skill_name=$(basename "$skill_dir")
  cp -r "$skill_dir" ~/.claude/skills/
  count=$((count + 1))
done
echo "   ✅ $count skills installed"
echo ""

# 2. Install roastmymvp CLI
echo "🔧 Installing roastmymvp CLI..."
cd roastmymvp
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -e ".[dev]" --quiet 2>/dev/null || pip install -e ".[dev]"
echo "   ✅ roastmymvp CLI ready"
echo ""

# 3. Install Playwright
echo "🎭 Installing browser engine..."
playwright install chromium 2>/dev/null || python -m playwright install chromium
echo "   ✅ Chromium installed"
echo ""

# 4. Initialize gene pool
echo "🧬 Initializing gene pool..."
roastmymvp evolve 2>/dev/null || echo "   (run 'roastmymvp evolve' manually if this failed)"
echo ""

cd ..

echo "╔══════════════════════════════════════════════╗"
echo "║            Installation complete!             ║"
echo "╠══════════════════════════════════════════════╣"
echo "║                                              ║"
echo "║  Unified pipeline (recommended):             ║"
echo "║    /vibe           Full 9-stage pipeline      ║"
echo "║                                              ║"
echo "║  Individual commands:                        ║"
echo "║    /validate-idea  Should I build this?       ║"
echo "║    /vibe-prep      Plan it properly           ║"
echo "║    /vibe-harness   Build autonomously         ║"
echo "║    /roast-mvp      Get brutally roasted       ║"
echo "║                                              ║"
echo "║  Or roast any URL directly:                  ║"
echo "║    cd roastmymvp && source .venv/bin/activate ║"
echo "║    roastmymvp run https://app.com --mode vc  ║"
echo "║                                              ║"
echo "║  For full /vibe experience, also install:    ║"
echo "║    github.com/garrytan/gstack                ║"
echo "║    github.com/obra/superpowers               ║"
echo "║                                              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
