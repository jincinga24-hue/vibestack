---
name: vibe-prep
version: 1.0.0
description: |
  MANUAL TRIGGER ONLY: invoke only when user types /vibe-prep.
  Interactive preparation for vibe coding: validate idea, write PRD, design UI,
  scaffold project. All steps require human approval. Once complete, tells the
  user to run /vibe-harness for the autonomous coding loop.
allowed-tools:
  - Read
  - Write
  - Edit
  - Agent
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - WebSearch
  - WebFetch
  - Skill
---

# /vibe-prep — Interactive Project Preparation

## Overview

You are guiding the user through project setup BEFORE autonomous coding begins.
Every step is interactive — ask questions, show drafts, wait for approval.
Nothing gets finalized without the user saying yes.

After this skill completes, the user runs `/vibe-harness` for the autonomous coding loop.

Language: Match the user's language.

---

## Step 1: Idea Validation

Check if `VALIDATION-REPORT.md` exists in the project root.

- **If it exists:** Read it. Show the user a summary: idea, GO/NO-GO, MVP features. Ask: **"Found an existing validation. Use this, or start fresh?"**

- **If it does NOT exist:** Ask the user:
  > "Let's validate your idea first. Options:
  > (a) Full validation with /validate-idea (recommended — 6-step deep dive)
  > (b) Quick validation — tell me your idea in 1-2 sentences
  > (c) Skip — I already know what I want to build"

  - If (a): Invoke `/validate-idea` using the Skill tool. Once done, continue.
  - If (b): Ask for the idea. Run a lightweight check: problem, target user, competitors, risk. Write `VALIDATION-REPORT.md`.
  - If (c): Ask for: idea (one sentence), target user, 3 MVP features. Write a minimal `VALIDATION-REPORT.md`.

### GO/NO-GO Gate

- **NO-GO:** Explain why. Suggest pivots. Stop here.
- **CONDITIONAL GO:** Show conditions. Ask if they want to proceed.
- **GO:** Continue to Step 2.

---

## Step 2: Tech Stack

Ask: **"What tech stack do you want? Some options based on your idea:"**

Suggest 2-3 options based on the idea type. For example:
- Web app → Next.js + Tailwind, or Python + Flask, or SvelteKit
- Mobile → React Native, or Flutter, or Swift
- CLI tool → Python, or Node.js, or Go

Wait for the user to pick or specify their own.

---

## Step 3: PRD (Product Requirements Document)

Write the PRD **with the user**:

1. Ask: **"What's the core problem this solves in one sentence?"**
2. Ask: **"Any features that are explicitly NOT in scope for v1?"**
3. Draft `docs/PRD.md`:

```markdown
# PRD: [Idea Name]

## Problem
[one sentence]

## Target User
[from validation]

## MVP Features (v1)
1. [feature 1]
2. [feature 2]
3. [feature 3]

## Success Metrics
- [from validation]

## Non-Goals (explicitly out of scope)
- [user's answers]

## Tech Stack
- [chosen stack]
```

4. Show the PRD: **"Here's the PRD. Anything to change?"**
5. Edit until user says it's good.

---

## Step 4: UI/UX Design

Design the UI **with the user**:

1. Ask: **"What kind of interface? Dashboard, landing page, mobile app, CLI? Any design references or sites you like?"**
2. Ask: **"Walk me through the main user flow — what does someone do when they open the app?"**
3. Draft `docs/UI-DESIGN.md`:

```markdown
# UI Design: [Idea Name]

## Style
- [user's preferences: minimal, colorful, dark, etc.]
- References: [any sites mentioned]

## Pages / Screens
1. [page]: [description + key elements]
2. [page]: [description + key elements]
3. [page]: [description + key elements]

## User Flow
1. User opens app → sees [what]
2. User does [action] → sees [result]
3. ...

## Components
- [component list: navbar, cards, forms, etc.]

## Color / Typography (if specified)
- [any preferences]
```

4. Show: **"Here's the UI plan. Want to change anything?"**
5. Edit until approved.

---

## Step 5: Architecture

Draft the architecture doc based on PRD and UI decisions:

1. Write `docs/ARCHITECTURE.md`:

```markdown
# Architecture: [Idea Name]

## Tech Stack
- Frontend: [framework]
- Backend: [framework/API]
- Database: [if any]
- Hosting: [if discussed]

## Folder Structure
```
[proposed structure]
```

## Key Libraries
- [lib]: [what for]

## Data Flow
[brief description of how data moves]
```

2. Show: **"Here's the architecture. Make sense?"**
3. Edit until approved.

---

## Step 6: Scaffold Project

Set up the actual project files:

1. Create the folder structure from the architecture doc
2. Install dependencies (package.json, requirements.txt, etc.)
3. Create entry point
4. Show: **"Project scaffolded. Here's what was created:"** (list the files)
5. Edit until approved.

---

## Step 7: Output Context Documents

Generate three documents that serve as the **coding context** for the vibe-harness autonomous loop:

1. **`docs/PRD.md`** — finalized from Step 3 (should already exist, verify it's complete)
2. **`docs/ARCHITECTURE.md`** — finalized from Step 5 (should already exist, verify it's complete)
3. **`CLAUDE.md`** — project guidelines file that:
   - References PRD, UI-DESIGN, and ARCHITECTURE docs
   - Summarizes the project in 2-3 sentences
   - Lists key decisions made during prep
   - Lists the tech stack
   - Describes the folder structure
   - Contains any project-specific coding rules from Step 8

Show: **"Here are the three context documents for autonomous coding. Look good?"**
Edit until approved.

### IMPORTANT: Live Document Updates
These three documents are **living documents**. During the vibe-harness autonomous coding loop:
- `docs/PRD.md` — update when features are completed, descoped, or new requirements emerge
- `docs/ARCHITECTURE.md` — update when folder structure, data flow, or libraries change
- `CLAUDE.md` — update when new conventions, decisions, or guidelines are established

The Generator agent MUST update these docs as part of each cycle when relevant changes occur. This is NOT optional — stale docs lead to AI confusion in later cycles.

---

## Step 8: Development Standards & Reference

Establish coding standards and reference materials for the AI to follow during autonomous coding.

### 8a. Ask the user:
> **"Do you have any coding style preferences or reference projects? For example:**
> - **File naming:** camelCase, kebab-case, snake_case?
> - **File size limit:** max lines per file? (recommend 200-400)
> - **Reference project:** any existing codebase or repo to follow as a style guide?
> - **Component patterns:** any preferred patterns? (e.g., functional components, class-based)
> - **Any other conventions?"**

### 8b. Create `docs/REFERENCE.md`:

```markdown
# Development Standards: [Idea Name]

## File Naming
- [convention]: e.g., camelCase for JS files, kebab-case for components

## File Size Limits
- Max [X] lines per file (default: 400)
- If a file exceeds the limit, split into smaller modules

## Code Style
- [language-specific conventions]
- [formatting rules]

## Reference
- [link or description of reference project/codebase, if any]
- [key patterns to follow from the reference]

## Component/Module Patterns
- [how to structure components/modules]
- [naming conventions for functions, variables, classes]

## Import/Export Conventions
- [how to organize imports]
- [default vs named exports]
```

### 8c. If the user provides a reference project/repo:
1. Read key files from the reference to extract patterns
2. Create `docs/reference/` folder with example snippets showing the style to follow
3. Add notes in `REFERENCE.md` pointing to these examples

### 8d. Update `CLAUDE.md` to include a section pointing to `docs/REFERENCE.md`

Show: **"Here are the dev standards. Anything to change?"**
Edit until approved.

---

## Step 9: Git Init & Quality Gates

Set up version control and quality checks for the vibe-harness to use.

### 9a. Initialize Git
1. `git init` (if not already a git repo)
2. Create `.gitignore` appropriate for the tech stack
3. Make initial commit with all scaffolded files

### 9b. Define Quality Gates
Ask: **"What quality checks should run after each coding cycle? Defaults:"**

Show default gates based on tech stack:
- **Lint:** ESLint / Pylint / etc.
- **Build:** Does it compile/build without errors?
- **Tests:** Do existing tests pass?
- **File size:** No file exceeds the limit from Step 8

Create `docs/QUALITY-GATES.md`:

```markdown
# Quality Gates: [Idea Name]

## After Each Cycle
- [ ] Build passes (no errors)
- [ ] Lint passes (no warnings)
- [ ] All tests pass
- [ ] No file exceeds [X] lines
- [ ] No hardcoded secrets

## Before Merge/Ship
- [ ] Manual review of all changes
- [ ] Test coverage > [X]%
- [ ] All docs up to date
```

### 9c. Update `CLAUDE.md` to reference quality gates

Show: **"Git initialized and quality gates set. Ready?"**
Edit until approved.

---

## Step 10: Handoff

Print this message:

> **Prep complete!** Here's what's ready:
> - `VALIDATION-REPORT.md` — idea validated
> - `docs/PRD.md` — product requirements
> - `docs/UI-DESIGN.md` — UI/UX plan
> - `docs/ARCHITECTURE.md` — technical architecture
> - `docs/REFERENCE.md` — development standards & coding conventions
> - `docs/QUALITY-GATES.md` — quality gates for each cycle
> - `CLAUDE.md` — project guidelines (references all docs above)
> - Project scaffolded with dependencies
> - Git initialized with initial commit
>
> **Next:** Run `/vibe-harness` to start the autonomous 15-cycle coding loop.
> The dashboard will open automatically and track progress in real time.

---

## Rules

1. **Every step needs user approval.** Never skip ahead without a "yes" or "looks good".
8. **Search before building.** Before choosing a library or approach, ask: "Is there an existing repo or package that does 80% of this?" Use WebSearch to check. Don't reinvent wheels.
9. **Read official docs.** When the user picks a framework, fetch its official quickstart/docs and include key patterns in the ARCHITECTURE doc so the Generator doesn't guess APIs.
2. **Ask, don't assume.** If you're unsure about a preference, ask.
3. **Show drafts, not final versions.** Always present as "here's a draft" so the user feels comfortable editing.
4. **Match the user's language.** Chinese in, Chinese out.
5. **Keep it conversational.** This is a planning session, not a formal process.
6. **Reference the validation report.** Use the data from /validate-idea to pre-fill fields.
7. **Don't write code yet.** Scaffold only. The coding happens in /vibe-harness.
