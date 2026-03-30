# AI Beta Test — Architecture Document

**Version:** 1.0
**Date:** 2026-03-27
**Status:** Living document

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────┐
│                    CLI Entry Point                   │
│         ai-beta-test <input> [options]               │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────▼────────┐
              │  Input Router   │
              │                 │
              │  URL → Browser  │
              │  Image → Vision │
              │  Text → Direct  │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ Browser Agent│ │ Vision   │ │ Text         │
│ (Playwright) │ │ Analyzer │ │ Analyzer     │
│              │ │          │ │              │
│ - Navigate   │ │ - Read   │ │ - Parse PRD  │
│ - Click      │ │   images │ │ - Extract    │
│ - Screenshot │ │ - Detect │ │   features   │
│ - Log events │ │   UI     │ │ - Identify   │
│ - Mobile test│ │   issues │ │   user flows │
└──────┬───────┘ └────┬─────┘ └──────┬───────┘
       │              │              │
       └──────────────┼──────────────┘
                      ▼
            ┌──────────────────┐
            │  Context Builder │
            │                  │
            │  Unified format: │
            │  - Screenshots   │
            │  - Interactions  │
            │  - Features list │
            │  - Target users  │
            └────────┬─────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
┌──────────────┐ ┌────────┐ ┌──────────────┐
│ Layer 1      │ │Layer 2 │ │ Layer 3      │
│ Tech Testing │ │UX Test │ │ PMF Testing  │
│              │ │        │ │              │
│ - Bugs       │ │- Depth │ │- Quantified  │
│ - Perf       │ │ persona│ │  personas    │
│ - Mobile     │ │ (20)   │ │  (1000+)     │
│ - A11y       │ │- UX    │ │- Download %  │
│              │ │ scores │ │- Pay intent  │
│              │ │- Frict.│ │- Retention   │
└──────┬───────┘ └───┬────┘ └──────┬───────┘
       │             │             │
       └─────────────┼─────────────┘
                     ▼
            ┌──────────────────┐
            │ Report Generator │
            │                  │
            │ FEEDBACK-REPORT  │
            │ .md              │
            └──────────────────┘
```

---

## 2. Module Details

### 2.1 Browser Agent (`src/browser/`)

**Responsibility:** Open a URL, explore it like a real user, collect evidence.

| File | Purpose |
|------|---------|
| `explorer.py` | Playwright session — open URL, find interactive elements, click through |
| `screenshotter.py` | Take screenshots at each state change, desktop + mobile |
| `interaction_log.py` | Record all clicks, navigations, errors as structured JSON |
| `mobile_tester.py` | Resize viewport, test responsive breakpoints |
| `performance.py` | Measure load time, resource sizes, JS errors |

**Output:** `BrowserContext` dataclass
```python
@dataclass(frozen=True)
class BrowserContext:
    screenshots: list[Screenshot]      # path + description
    interactions: list[Interaction]    # element + action + result
    errors: list[BrowserError]         # JS errors, 404s, etc.
    performance: PerformanceMetrics    # load time, resource count
    elements: list[InteractiveElement] # all buttons, links, inputs found
```

### 2.2 Persona Engine (`src/personas/`)

**Responsibility:** Generate diverse user perspectives based on real product data.

| File | Purpose |
|------|---------|
| `generator.py` | Create persona profiles from user config or defaults |
| `depth_analyst.py` | Run 20 deep persona analyses (full narrative, Sonnet) |
| `quant_analyst.py` | Run 1000+ quantified persona ratings (JSON only, Haiku) |
| `irrationality.py` | Inject non-rational behavior modifiers |
| `templates/` | Pre-built persona templates by industry |

**Persona Profile:**
```python
@dataclass(frozen=True)
class PersonaProfile:
    name: str
    age: int
    background: str
    tech_savvy: float          # 0-1
    patience_seconds: int      # how long before they leave
    language: str              # primary language
    has_alternative: bool      # already using a competitor?
    alternative_name: str | None
    irrationality_mod: str | None  # random constraint
```

### 2.3 Report Generator (`src/report/`)

**Responsibility:** Combine all layers into a human-readable report.

| File | Purpose |
|------|---------|
| `builder.py` | Assemble markdown report from all data |
| `stats.py` | Calculate aggregate statistics from quantified personas |
| `visualizer.py` | Generate ASCII charts for CLI output |
| `templates/report.md` | Report template |

---

## 3. Data Flow

```
Input (URL)
  → Browser Agent explores (60-90 seconds)
  → Screenshots + interaction log saved to /tmp/ai-beta-test/{session}/
  → Context Builder creates unified product context
  → Layer 1: Browser errors/bugs extracted directly from agent data
  → Layer 2: 20 deep personas analyze screenshots + context (parallel, ~2 min)
  → Layer 3: 1000 quant personas rate product (batch API calls, ~3 min)
  → Report Generator combines all layers
  → FEEDBACK-REPORT.md written to current directory
```

---

## 4. Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.12+ | Playwright ecosystem, LLM SDKs, user's existing venv |
| Browser automation | Playwright | Proven in feasibility spike (2026-03-27) |
| LLM (deep analysis) | Claude Sonnet via Anthropic SDK | Best coding/analysis model |
| LLM (quantified) | Claude Haiku via Anthropic SDK | 3x cheaper, fast enough for JSON |
| CLI framework | Click | Lightweight, well-documented |
| Config | YAML | Human-readable, `.ai-beta-test.yaml` |
| Output | Markdown | Universal, dev-friendly |
| Package manager | pip / pyproject.toml | Standard Python packaging |

---

## 5. Directory Structure

```
ai-beta-test/
├── src/
│   ├── __init__.py
│   ├── cli.py                 # Click CLI entry point
│   ├── config.py              # YAML config loader
│   ├── browser/
│   │   ├── __init__.py
│   │   ├── explorer.py        # Playwright page exploration
│   │   ├── screenshotter.py   # Screenshot capture
│   │   ├── interaction_log.py # Structured interaction recording
│   │   ├── mobile_tester.py   # Responsive testing
│   │   └── performance.py     # Load time, errors
│   ├── context/
│   │   ├── __init__.py
│   │   └── builder.py         # Unify all inputs into product context
│   ├── personas/
│   │   ├── __init__.py
│   │   ├── generator.py       # Persona profile creation
│   │   ├── depth_analyst.py   # 20 deep persona analysis
│   │   ├── quant_analyst.py   # 1000+ quantified ratings
│   │   ├── irrationality.py   # Non-rational behavior injection
│   │   └── templates/         # Industry-specific persona presets
│   │       ├── saas.yaml
│   │       ├── game.yaml
│   │       ├── education.yaml
│   │       └── ecommerce.yaml
│   ├── report/
│   │   ├── __init__.py
│   │   ├── builder.py         # Report assembly
│   │   ├── stats.py           # Aggregate statistics
│   │   └── visualizer.py      # ASCII charts
│   └── llm/
│       ├── __init__.py
│       ├── client.py          # LLM API wrapper (model routing)
│       └── prompts.py         # All prompt templates
├── tests/
│   ├── test_browser.py
│   ├── test_personas.py
│   └── test_report.py
├── PRD.md
├── ARCHITECTURE.md
├── PROGRESS.md
├── pyproject.toml
├── README.md
└── .ai-beta-test.yaml        # Example config
```

---

## 6. Key Design Decisions

| Decision | Choice | Alternatives Considered | Why |
|----------|--------|------------------------|-----|
| CLI first, no web UI | CLI | Web dashboard, VS Code extension | Fastest to validate, dev-native |
| Immutable dataclasses | `frozen=True` | Mutable dicts | Coding style rule — no mutation |
| Markdown output | .md file | JSON, HTML, PDF | Universal, zero-dependency |
| Session-based temp storage | `/tmp/ai-beta-test/{id}/` | Persistent DB | Simple, no cleanup needed |
| Separate deep vs quant personas | Two-tier | Single tier | 20 deep for insights, 1000 quant for statistics |

---

## 7. API Cost Model

| Operation | Model | Tokens (est.) | Cost per run |
|-----------|-------|---------------|-------------|
| Browser context summary | Sonnet | ~2K in, ~1K out | ~$0.02 |
| 1 deep persona (with screenshots) | Sonnet | ~4K in, ~2K out | ~$0.04 |
| 20 deep personas | Sonnet | ~80K in, ~40K out | ~$0.80 |
| 1 quant persona | Haiku | ~500 in, ~100 out | ~$0.0003 |
| 1000 quant personas | Haiku | ~500K in, ~100K out | ~$0.30 |
| **Total per run (20 deep + 1000 quant)** | | | **~$1.10** |
