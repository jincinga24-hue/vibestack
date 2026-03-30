# Architecture

## Pipeline

```
/vibe-prep (human-in-the-loop)
    │
    ├── Idea Validation (Socratic questioning, first principles)
    ├── PRD Generation (acceptance criteria, scope)
    ├── UI Design (layout, components, flows)
    └── Project Scaffold (dependencies, structure)
    │
    ▼
/vibe-harness (autonomous)
    │
    ├── 15 generate/evaluate cycles
    ├── Quality gates per cycle
    ├── Live HTML dashboard
    └── Produces HARNESS-STATE.md + HARNESS-ANALYSIS.md
    │
    ▼
/roast-mvp (brutal validation)
    │
    ├── Playwright Browser Agent
    │   ├── Page exploration (53+ elements)
    │   ├── Page text extraction (visible only)
    │   ├── Screenshots (desktop/tablet/mobile)
    │   ├── Performance metrics
    │   └── Mobile testing (overflow, tap targets)
    │
    ├── Founder Profiler
    │   ├── GitHub API scraping
    │   ├── Credibility checks
    │   └── Bluff detection
    │
    ├── VC Roast Panel (Stage 1)
    │   ├── 5 VC archetypes (shark, domain expert, etc.)
    │   ├── Evolved kill questions from gene pool
    │   ├── Founder intel referenced in roasts
    │   └── Pass/fail gate (score >= 40 + interest)
    │
    ├── Community Testing (Stage 2, unlocked by VC gate)
    │   ├── Real personas from Reddit/HN
    │   ├── 7 behavioral archetypes
    │   ├── 30% irrationality injection
    │   └── PMF signals (GO / CONDITIONAL / NO-GO)
    │
    ├── Evolution Engine
    │   ├── Gene encoding (traits as mutable genes)
    │   ├── Fitness tracking (user feedback)
    │   ├── Kill / mutate / crossover cycles
    │   └── Persistent gene pool (memory/genes/)
    │
    └── Report Generation
        ├── Markdown reports
        ├── PDF visual reports (Playwright)
        └── Action plans (priority 1/2/3)
```

## LLM Backend

```
Priority:
1. ANTHROPIC_API_KEY set → Anthropic API (Sonnet for deep, Haiku for fast)
2. claude CLI installed → Claude Code subscription (zero cost)
```

## Data Flow

```
URL → Playwright → BrowserContext → ProductContext (text)
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
              VC Prompts          Community Prompts     Founder Intel
              (+ evolved genes)  (+ Reddit signals)    (+ GitHub data)
                    │                    │                    │
                    ▼                    ▼                    ▼
              Claude (LLM)        Claude (LLM)         Credibility
                    │                    │              Checks
                    ▼                    ▼                    │
              RoastVerdicts       PersonaFeedback            │
                    │                    │                    │
                    └────────┬───────────┘                    │
                             ▼                               │
                    Reports + PDF  ◄─────────────────────────┘
                             │
                             ▼
                    User Feedback → Gene Pool → Evolution
```
