# AI Beta Test — Project Progress

**Last updated:** 2026-03-28
**Current phase:** Post-MVP (VC mode + Gauntlet + Research shipped)

---

## Phase Status

| Phase | Status | Notes |
|-------|--------|-------|
| I. Brainstorm (Steps 1-3) | COMPLETE | Requirements defined, PRD written |
| II. Foundation (Steps 4-6) | COMPLETE | Architecture drafted, tech stack chosen |
| III. Ready to Build (Steps 7-9) | COMPLETE | Living docs created |
| IV. Building (Sprints 1-3) | COMPLETE | All 3 sprints done, MVP ready |
| V. Persona Engine v2 | COMPLETE | Archetypes, irrationality, industry templates |
| VI. Market Research | COMPLETE | Reddit/HN scraping, persona enrichment |
| VII. VC Roast + Gauntlet | COMPLETE | 5 VC personas, 2-stage gate pipeline |
| VIII. Claude CLI Backend | COMPLETE | No API key needed, uses Claude Code subscription |

---

## Validation History (2026-03-27)

All validation was done in a single session before writing any code:

1. **Idea validation** — `/validate-idea` framework used, result: CONDITIONAL GO
2. **Competitive research** — 6 competitors identified (Blok, Artificial Societies, Synthetic Users, Uxia, Ask Rally, Limbik). None target indie developers.
3. **Route A feasibility** — 20 AI personas tested HideAndSeek+. Result: produced 5+ non-obvious insights. VALIDATED.
4. **Route B feasibility** — Playwright agent tested ActuaWiki. Result: found 4 real bugs that Route A couldn't find. VALIDATED.
5. **Scale strategy** — 20 deep (qualitative) + 10000 quantified (quantitative) approach designed.
6. **Moat strategy** — Persona database + calibration data flywheel identified as defensibility.

---

## What's Been Built (2026-03-28)

### Sprint 1: Browser Agent — COMPLETE
- [x] Project setup (pyproject.toml, dependencies)
- [x] Playwright explorer — auto-navigate URL, find interactive elements
- [x] Screenshot capture — desktop + mobile + tablet
- [x] Interaction logging — structured JSON
- [x] Performance metrics — load time, JS errors
- [x] Mobile testing — overflow detection, tap target validation

### Sprint 2: Persona Engine — COMPLETE
- [x] 20 rich default personas with 7 archetypes (power_user, skeptic, advocate, confused, churner, pragmatist, accessibility)
- [x] 4 evaluation styles (task_driven, exploratory, comparison, first_impression)
- [x] 30% irrationality injection (20 realistic irrational behaviors)
- [x] Task-based evaluation prompts (not generic "rate this")
- [x] Custom persona generation from free-text descriptions
- [x] Variant generation with archetype cycling (not just random noise)
- [x] 4 industry templates (SaaS, e-commerce, education, game)

### Sprint 3: Report + CLI — COMPLETE
- [x] Context builder — unify browser data for LLM
- [x] Report builder with PMF signals (GO / CONDITIONAL GO / NO-GO)
- [x] Click CLI: `--mode`, `--personas`, `--persona`, `--competitor`, `--pitch`, `--skip-research`
- [x] YAML config support (.ai-beta-test.yaml)

### Post-MVP: Market Research — COMPLETE
- [x] Reddit scraper (public JSON API, no auth)
- [x] Hacker News scraper (Algolia API)
- [x] Signal classifier (complaint, praise, feature_request, churn_reason)
- [x] Competitor intel gathering
- [x] Persona enricher — injects real user complaints into personas

### Post-MVP: VC Roast Mode — COMPLETE
- [x] 5 VC personas (shark, domain expert, pattern matcher, devil's advocate, cold caller)
- [x] Kill questions, pet peeves, investability scoring (0-100)
- [x] Roast verdicts: kill shot, grudging praise, must-fix list
- [x] VC Gate: pass threshold (score >= 40 + at least one "maybe/invest")

### Post-MVP: Gauntlet Pipeline — COMPLETE
- [x] 2-stage pipeline: VC Gate → Community Gate → Certification
- [x] 4 certification levels: DESTROYED, SURVIVED, CERTIFIED GOOD, CERTIFIED GREAT
- [x] Community testing locked until VC gate passes
- [x] Combined final score from both stages

### Post-MVP: Claude CLI Backend — COMPLETE
- [x] `claude -p` backend — uses existing Claude Code subscription
- [x] Auto-detection: API key → API backend, else claude CLI → CLI backend
- [x] Zero setup for Claude Code users

---

## Stats

- **159 tests** (unit + integration + E2E)
- **84%+ coverage** (above 80% target)
- **All dataclasses frozen** (immutable)
- **All files < 400 lines**
- **4 commits** on main

---

## Usage

```bash
# Community test (default)
ai-beta-test https://your-app.com

# VC roast
ai-beta-test https://your-app.com --mode vc --pitch "Uber for dogs"

# Full gauntlet (VC → Community → Certification)
ai-beta-test https://your-app.com --mode gauntlet

# With competitor research
ai-beta-test https://your-app.com --competitor Notion --competitor Linear

# Custom personas
ai-beta-test https://your-app.com -p "22yo CS student" -p "35yo skeptical CTO"
```

---

## Future (v2+)

- [ ] Quantified personas (1000+ via Haiku, JSON-only ratings)
- [ ] Multi-LLM cross-validation (Claude + GPT + Gemini)
- [ ] Figma input support (screenshot extraction)
- [ ] GitHub Action integration (CI/CD gate)
- [ ] Calibration engine (AI vs real user data comparison)
- [ ] Web UI / Dashboard
- [ ] Leaderboard for gauntlet results
- [ ] Team/multiplayer mode (multiple founders defend their pitch)

---

## Module Ownership

| Module | Files | Touches | Does NOT touch |
|--------|-------|---------|----------------|
| browser | ai_beta_test/browser/*.py | Playwright, screenshots, /tmp/ | LLM APIs, report output |
| personas | ai_beta_test/personas/*.py | LLM APIs, browser context | Playwright, file I/O |
| report | ai_beta_test/report/*.py | All module outputs, file I/O | Playwright, LLM APIs |
| llm | ai_beta_test/llm/*.py | Claude CLI, Anthropic SDK | Browser, report formatting |
| research | ai_beta_test/research/*.py | Reddit/HN APIs, persona data | Browser, LLM direct |
| vc | ai_beta_test/vc/*.py | LLM APIs, product context | Browser, persona generator |
| gauntlet | ai_beta_test/gauntlet.py | VC + community results | Direct LLM, browser |
| cli | ai_beta_test/cli.py | All modules, user config | Internal module logic |
