# vibestack

**A step-by-step workflow for building projects with Claude Code.**

You just installed Claude Code. Now what? vibestack gives you 4 slash commands that walk you through the entire process — from "I have an idea" to "is this actually good?"

```bash
git clone https://github.com/jincinga24-hue/vibestack.git
cd vibestack && bash install.sh
```

---

## The Workflow

### Step 1: You have an idea

Type `/validate-idea` in Claude Code.

It asks you hard questions before you waste time building:
- What problem are you solving?
- Who has this problem?
- What do they do today without your product?
- Why would they switch?
- What's the simplest version that proves the idea?

You get a `VALIDATION-REPORT.md` with a go/no-go recommendation.

### Step 2: Plan and design

Type `/vibe-prep`.

It walks you through:
- Writing a PRD (what to build, what NOT to build)
- Designing the UI (layout, pages, components)
- Setting up the project (dependencies, folder structure)

Everything is interactive — it asks, you approve. Nothing gets written without your OK.

You end up with `docs/PRD.md`, `docs/UI-DESIGN.md`, and a scaffolded project.

### Step 3: Build it

Type `/vibe-harness`.

This is the autonomous part. Claude codes for you in a loop:
- Reads the PRD and UI design
- Writes code
- Evaluates what it built
- Fixes issues
- Repeats (up to 15 cycles)

A live dashboard opens in your browser so you can watch progress.

You end up with a working prototype.

### Step 4: Is it any good?

Type `/roast-mvp`.

This is the honest feedback part. It:
1. Opens your site in a headless browser
2. Reads everything a real user would see
3. Runs simulated users against it who give brutally honest feedback
4. Generates a report telling you what's broken, what's good, and what to fix

You get a `FEEDBACK-REPORT.md` and optionally a PDF.

---

## That's It

```
/validate-idea    →  "Should I build this?"
/vibe-prep        →  "OK, let's plan it properly"
/vibe-harness     →  "Build it for me"
/roast-mvp        →  "Be honest — is it good?"
```

For most projects, this takes one session.

---

## Install

**You need:** [Claude Code](https://claude.ai/code) installed + Python 3.12+

```bash
git clone https://github.com/jincinga24-hue/vibestack.git
cd vibestack
bash install.sh
```

That's it. Open Claude Code in any project and the slash commands are available.

---

## Example: What the roast looks like

When you run `/roast-mvp` on a real site, you get feedback like this:

```
Verdict: NO-GO | UX: 5.5/10

Top Issues:
- 47 of 53 navigation buttons hidden on load — users can't find anything
- Search bar is hidden — the core feature is invisible
- "Coming soon" section listed alongside finished ones — feels incomplete
- Footer says © 2025 — looks abandoned

What They Liked:
- 695ms load time — genuinely fast
- Zero JS errors
- Content structure is solid — "whoever built this knows the domain"

Fix These First:
1. Show search on the landing page
2. Remove "coming soon" sections
3. Update the copyright year
```

Real issues. Not generic advice. Things you can fix today.

![Sample roast report](docs/images/roast-cover.png)

---

## Going Deeper

Once you're comfortable with the basic workflow, there's more:

### Roast modes

```bash
# Activate the CLI
cd vibestack/roastmymvp && source .venv/bin/activate

# Quick test — community feedback only
roastmymvp run https://your-app.com

# VC mode — 5 brutal investors roast your prototype
roastmymvp run https://your-app.com --mode vc

# Full gauntlet — must pass VCs to unlock community testing
roastmymvp run https://your-app.com --mode gauntlet
```

### Real users from Reddit

Instead of generic personas, build them from actual Reddit/HN discussions:

```bash
roastmymvp run https://your-app.com --real -n 20 -t "your topic" -s "your_subreddit"
```

### Founder profiling

VCs can research your GitHub before roasting. They'll catch bluffs.

```bash
roastmymvp run https://your-app.com --mode vc --github https://github.com/you
```

### Harness engineering

The autonomous coding loop is the most powerful part — and the one that needs the most understanding. When it gets stuck, when to reset context, how to tune pacing:

**[docs/HARNESS-GUIDE.md](docs/HARNESS-GUIDE.md)** — full guide on how the loop works, what to do when it breaks, and how to tune it.

### Evolution

The critics get better over time. Rate their feedback, and the good ones survive:

```bash
roastmymvp feedback    # Rate critiques from last run
roastmymvp evolve      # Bad critics die, good ones breed
roastmymvp pool        # Check who survived
```

Details: [docs/EVOLUTION.md](docs/EVOLUTION.md)

---

## Also Recommended

vibestack handles the idea-to-roast pipeline. For code review, QA, and shipping:

- **[gstack](https://github.com/garrytan/gstack)** by Garry Tan — adds `/review`, `/qa`, `/ship`, `/browse`
- **[Everything Claude Code](https://github.com/nicobailey/everything-claude-code)** — 65+ engineering pattern skills

They complement vibestack. Install all three for the full setup.

---

## Credits

- [gstack](https://github.com/garrytan/gstack) — the skill pack that inspired this
- [EvoMap](https://evomap.ai/) — evolution engine inspiration
- [Everything Claude Code](https://github.com/nicobailey/everything-claude-code) — engineering skills
- Claude Code by Anthropic

MIT License — fork it, improve it, share it.
