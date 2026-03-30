# AI Beta Test — Agent Rules

## Project Context
CLI tool for AI-simulated beta testing. Python + Playwright + Claude API.

## Living Documents (always read before working)
- `PRD.md` — what to build
- `ARCHITECTURE.md` — how it's structured
- `PROGRESS.md` — current state

## Rules

### 1. Small Slices
One module at a time. Build → test → commit. Never implement multiple modules in one go.

### 2. Immutability
All dataclasses use `frozen=True`. Never mutate objects. Create new instances instead.

### 3. File Limits
- Module: < 400 lines → extract
- Function: < 50 lines → split
- One class per file

### 4. No Secrets in Code
- API keys via environment variables (`ANTHROPIC_API_KEY`)
- Never hardcode keys, URLs, or credentials

### 5. Two-Strike Rule
If a bug isn't fixed in 2 attempts → stop, write down what happened, rethink approach.

### 6. Update Docs After Changes
- Changed features → update PRD.md
- Changed architecture → update ARCHITECTURE.md
- Changed progress → update PROGRESS.md

### 7. Test First
Write tests before implementation. Target 80% coverage.
