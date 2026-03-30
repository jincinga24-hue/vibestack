# vibestack

> From idea to roasted MVP in one session. Three slash commands. Zero hand-holding.

The full vibe coding pipeline: **idea → autonomous coding → brutal product validation**.

Built by a uni student who got tired of building things nobody wanted. Inspired by [gstack](https://github.com/garrytan/gstack) (Garry Tan's Claude Code workflow) and the Shanghai EvoMap hackathon team's Agent VC concept.

```
/vibe-prep          → Interactive: validate idea, write PRD, design UI, scaffold
/vibe-harness       → Autonomous: 15 generate/evaluate cycles, live dashboard
/roast-mvp          → Brutal: evolving VC panel + community personas roast your MVP
```

**What makes this different from gstack:**
- gstack gives you **roles** (CEO, designer, QA). vibestack gives you a **pipeline**.
- gstack reviews code you've already written. vibestack **writes the code, then roasts it**.
- The roast uses **real users from Reddit/HN**, not generic personas.
- VCs **evolve** — bad critics die, good ones breed. The tool gets better every time you use it.
- VCs **research you** — they scrape your GitHub and call out bluffs.

## The Pipeline

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  /vibe-prep      │────▶│  /vibe-harness    │────▶│  /roast-mvp             │
│                  │     │                   │     │                         │
│  Validate idea   │     │  15 autonomous    │     │  VC Gate (5 VCs)        │
│  Write PRD       │     │  coding cycles    │     │  ↓ pass?                │
│  Design UI       │     │  Live dashboard   │     │  Community Gate (20+    │
│  Scaffold code   │     │  Quality gates    │     │  real Reddit/HN users)  │
│                  │     │                   │     │  ↓ pass?                │
│  Human approves  │     │  Agent decides    │     │  CERTIFIED 🏆           │
│  each step       │     │  each cycle       │     │  PDF report generated   │
└─────────────────┘     └──────────────────┘     └─────────────────────────┘
```

## Quick Start

### Install (30 seconds)

```bash
# Clone vibestack
git clone https://github.com/YOUR_USERNAME/vibestack.git

# Install skills to Claude Code
cp -r vibestack/skills/* ~/.claude/skills/

# Install roastmymvp CLI (the roast engine)
cd vibestack/roastmymvp
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium

# Initialize the gene pool
roastmymvp evolve
```

### Run the Pipeline

```bash
# Step 1: Prep (interactive)
# In Claude Code, type:
/vibe-prep

# Step 2: Build (autonomous)
/vibe-harness

# Step 3: Roast (brutal)
/roast-mvp
```

Or run the roast directly on any URL:

```bash
# Quick VC roast
roastmymvp run https://your-app.com --mode vc

# Full gauntlet with real personas
roastmymvp run https://your-app.com --mode gauntlet --real -n 20

# VC roast with founder research (they WILL check your GitHub)
roastmymvp run https://your-app.com --mode vc \
  --github https://github.com/you \
  --pitch "Uber for dogs"
```

## Skills

### Core Pipeline (3 stages)

| Skill | Stage | What it does |
|-------|-------|-------------|
| `/validate-idea` | 0 | 6-step idea stress test (Socratic, first principles, business model, risk, multi-role panel, Occam's MVP) |
| `/vibe-prep` | 1 | Interactive: validate idea → PRD → UI design → scaffold (calls /validate-idea) |
| `/vibe-harness` | 2 | Autonomous: 15 generate/evaluate cycles with live dashboard |
| `/roast-mvp` | 3 | Brutal: evolving VC panel + community personas roast your MVP |

### Product Review Skills (from gstack)

| Skill | When to use |
|-------|-------------|
| `/office-hours` | YC-style forcing questions before you build anything |
| `/plan-ceo-review` | CEO/founder-mode: rethink the problem, find the 10-star product |
| `/plan-eng-review` | Eng manager-mode: lock architecture, data flow, edge cases |
| `/plan-design-review` | Designer's eye: rate each dimension 0-10, fix the plan |
| `/design-consultation` | Full design system: aesthetic, typography, color, layout |

### Code Quality Skills (from gstack)

| Skill | When to use |
|-------|-------------|
| `/review` | Pre-landing PR review: SQL safety, trust boundaries, side effects |
| `/design-review` | Visual QA: find spacing issues, hierarchy problems, AI slop |
| `/investigate` | Debug with root cause investigation (no fixes without root cause) |
| `/cso` | Security audit: secrets, supply chain, OWASP Top 10, STRIDE |

### Testing & QA Skills (from gstack)

| Skill | When to use |
|-------|-------------|
| `/qa` | QA test a web app and fix bugs found |
| `/qa-only` | Report-only QA (no fixes, just the report) |
| `/browse` | Headless browser: navigate, interact, screenshot, verify |
| `/connect-chrome` | Launch real Chrome controlled by Claude with live Side Panel |
| `/benchmark` | Performance regression detection with Core Web Vitals |
| `/canary` | Post-deploy monitoring for console errors and regressions |

### Ship & Deploy Skills (from gstack)

| Skill | When to use |
|-------|-------------|
| `/ship` | Merge base, run tests, review diff, bump version, push, create PR |
| `/document-release` | Update all docs to match what shipped |

### `/roast-mvp` Details

Three modes powered by `roastmymvp` CLI:

| Mode | What happens |
|------|-------------|
| `vc` | 5 brutal VC personas roast your prototype with kill shots |
| `community` | 10-100 personas from real Reddit/HN users test your UX |
| `gauntlet` | Must pass VC gate to unlock community testing → certification |

**Key features:**
- **Evolving VCs** — Gene pool persists between runs. Bad critics die, good ones breed.
- **Founder profiling** — VCs scrape your GitHub before the meeting. They will call out bluffs.
- **Real personas** — Built from actual Reddit/HN comments, not generic templates.
- **PDF reports** — Visual reports with scores, kill shots, UX bars, action plans.

## The Evolution Engine

Inspired by [EvoMap's Genome Evolution Protocol (GEP)](https://evomap.ai/).

```
Run roast → User rates critiques → Gene fitness updates
    ↑                                       ↓
    └── Evolve: kill weak, mutate mid, breed top ──┘
```

Each persona's traits are encoded as **genes**:
- Kill questions, pet peeves, frustrations, tone = mutable genes
- User feedback determines **fitness** (0.0 = useless, 1.0 = killer insight)
- Evolution: kill bottom 20%, mutate mid-tier, crossover top performers
- Dead VCs are replaced by evolved offspring

```bash
roastmymvp pool      # Check gene pool status
roastmymvp feedback  # Rate critiques from last run
roastmymvp evolve    # Run evolution cycle
```

## Repo Structure

```
vibestack/
├── README.md
├── INSTALL.md
├── install.sh                 # One-line install script
│
├── skills/                    # 21 slash commands
│   ├── validate-idea/         # /validate-idea — 6-step stress test
│   ├── vibe-prep/             # /vibe-prep — interactive preparation
│   ├── vibe-harness/          # /vibe-harness — autonomous coding loop
│   │   ├── SKILL.md
│   │   ├── dashboard.html     # Live progress dashboard
│   │   └── launch-dashboard.sh
│   ├── roast-mvp/             # /roast-mvp — brutal product validation
│   │
│   ├── gstack-office-hours/   # YC-style forcing questions
│   ├── gstack-plan-ceo-review/    # CEO review
│   ├── gstack-plan-eng-review/    # Eng manager review
│   ├── gstack-plan-design-review/ # Designer review
│   ├── gstack-design-consultation/ # Full design system
│   ├── gstack-design-review/  # Visual QA
│   ├── gstack-review/         # PR code review
│   ├── gstack-investigate/    # Root cause debugging
│   ├── gstack-cso/            # Security audit
│   ├── gstack-qa/             # QA + fix bugs
│   ├── gstack-qa-only/        # QA report only
│   ├── gstack-browse/         # Headless browser testing
│   ├── gstack-connect-chrome/ # Real Chrome with Side Panel
│   ├── gstack-benchmark/      # Performance regression
│   ├── gstack-canary/         # Post-deploy monitoring
│   ├── gstack-ship/           # Ship workflow
│   └── gstack-document-release/ # Post-ship docs update
│
├── roastmymvp/                # The roast engine (Python CLI)
│   ├── pyproject.toml
│   ├── roastmymvp/
│   │   ├── browser/           # Playwright page exploration
│   │   ├── personas/          # 7 archetypes, irrationality injection
│   │   ├── vc/                # 5 VC personas, kill shots
│   │   ├── research/          # Reddit/HN scraping, persona factory
│   │   ├── founder/           # GitHub/LinkedIn profiling, bluff detection
│   │   ├── evolution/         # Gene pool, mutation, crossover
│   │   ├── report/            # Markdown + PDF report generation
│   │   ├── llm/               # Claude CLI + API backend
│   │   └── cli.py             # Click CLI entry point
│   └── tests/                 # 150+ tests, 84%+ coverage
│
└── docs/
    ├── ARCHITECTURE.md        # Full system diagram
    └── EVOLUTION.md           # How the gene pool works
```

## Who This Is For

- **Solo builders** who vibe code and need honest feedback before shipping
- **Hackathon teams** who want to validate in hours, not weeks
- **Students** building portfolio projects who want to know if it's actually good
- **Anyone tired of "looks good!" from friends** and wants to hear the truth

## Credits

- [gstack](https://github.com/garrytan/gstack) by Garry Tan — the skill pack that started it all
- [EvoMap](https://evomap.ai/) — Genome Evolution Protocol inspiration
- The Shanghai EvoMap hackathon team — Agent VC concept that inspired the VC roast mode
- Claude Code by Anthropic — the runtime that makes this possible

## License

MIT
