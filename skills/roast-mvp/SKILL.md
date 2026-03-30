---
name: roast-mvp
version: 2.0.0
description: |
  MANUAL TRIGGER ONLY: invoke only when user types /roast-mvp.
  Roasts MVPs using roastmymvp CLI — evolving VC panel + community personas
  built from real Reddit/HN users. Gauntlet mode: VC gate → community gate → certification.
  Founder profiling via GitHub/LinkedIn. Gene pool evolves with each run.
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
---

# /roast-mvp — Roast Your MVP (v2)

## Overview

Production roast using `roastmymvp` CLI with evolving AI personas.

**Modes:**
- `vc` — 5 brutal VC personas roast your product (evolves over time)
- `community` — 10-100 personas from real Reddit/HN users test your UX
- `gauntlet` — Must pass VC gate to unlock community testing

**Key features:**
- Founder profiling (GitHub/LinkedIn scraping, bluff detection)
- Personas evolve via gene pool — bad critics die, good ones breed
- Real user signals from Reddit/HN feed into persona generation
- PDF report generation

Language: Match the user's language.

---

## Step 1: Pre-flight

1. Check if `roastmymvp` CLI is available:
```bash
cd ~/Vs\ Code/First\ Project/ai-beta-test && source .venv/bin/activate
roastmymvp --help
```

2. If not available, install:
```bash
cd ~/Vs\ Code/First\ Project/ai-beta-test
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
```

3. Check gene pool status:
```bash
roastmymvp pool
```

4. If gene pool is empty, initialize:
```bash
roastmymvp evolve
```

---

## Step 2: Determine Target

Ask the user:
- **URL**: What URL to test? (deployed site, localhost, etc.)
- **Mode**: vc / community / gauntlet? (default: gauntlet)
- **Founder info**: GitHub URL? LinkedIn? (optional, for VC mode)
- **Pitch**: One-line pitch? (optional, for VC mode)
- **Topics**: What domain? (for Reddit/HN persona building)

---

## Step 3: Run the Roast

### Option A: Full Gauntlet (recommended)
```bash
roastmymvp run <URL> \
  --mode gauntlet \
  --real -n 20 \
  --github <founder_github_url> \
  --pitch "<one-line pitch>" \
  -t "<topic1>" -t "<topic2>" \
  -s "<subreddit1>" -s "<subreddit2>"
```

### Option B: VC Only (quick brutal feedback)
```bash
roastmymvp run <URL> \
  --mode vc \
  --github <founder_github_url> \
  --pitch "<pitch>"
```

### Option C: Community Only (UX focused)
```bash
roastmymvp run <URL> \
  --mode community \
  --real -n 20 \
  -t "<topic>" -s "<subreddit>"
```

### Option D: For localhost projects
If the project isn't deployed, start dev server first:
```bash
# Start server in background
cd <project_dir> && npm run dev &>/tmp/roast-server.log &
sleep 5

# Then roast localhost
roastmymvp run http://localhost:3000 --mode gauntlet --skip-research
```

---

## Step 4: Generate PDF Report

After the CLI run completes, generate a visual PDF:

1. Read the output files (FEEDBACK-REPORT.md, VC-ROAST-REPORT.md, or GAUNTLET-REPORT.md)
2. Build a styled HTML report with:
   - Cover page (scores, verdict)
   - PMF signals + UX dimension bars
   - VC kill shots + grudging praise
   - Community friction points, bugs, praise
   - Selected persona narratives
   - Action plan (priority 1/2/3)
3. Convert to PDF via Playwright:
```python
import asyncio
from playwright.async_api import async_playwright

async def to_pdf(html_path, pdf_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(f'file://{html_path}')
        await page.wait_for_timeout(1000)
        await page.pdf(path=pdf_path, format='A4', print_background=True,
                       margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'})
        await browser.close()
```

4. Open the PDF for the user:
```bash
open <pdf_path>
```

---

## Step 5: Collect Feedback & Evolve

After presenting results, ask the user to rate critiques:

```bash
# Rate the critiques from the last run
roastmymvp feedback

# Run evolution cycle
roastmymvp evolve

# Check who survived
roastmymvp pool
```

Or do it programmatically — ask user to rate top 5 critiques on a 0-10 scale,
then apply ratings via the feedback command.

---

## Step 6: Present Results

Print summary:

> **Roast complete!** Score: [X]/100 — [VERDICT]
>
> [1-2 sentence summary]
>
> PDF report: [path]
>
> Options:
> (a) Rate critiques to evolve the gene pool (`roastmymvp feedback`)
> (b) Run more `/vibe-harness` cycles to fix top issues
> (c) Ship it anyway
> (d) Done

---

## Available CLI Commands

```bash
roastmymvp run <URL> [options]   # Run a roast
roastmymvp evolve                # Run evolution cycle on gene pool
roastmymvp feedback [run_id]     # Rate critiques to drive evolution
roastmymvp pool                  # View gene pool status
```

### Run Options
| Flag | Description |
|------|-------------|
| `--mode vc/community/gauntlet` | Testing mode (default: community) |
| `--real` | Build personas from real Reddit/HN users |
| `-n 20` | Number of personas |
| `--github <url>` | Founder's GitHub (VCs will research you) |
| `--linkedin <url>` | Founder's LinkedIn |
| `--twitter <url>` | Founder's Twitter/X |
| `--pitch "<text>"` | Elevator pitch for VC mode |
| `-t "<topic>"` | Search terms for real users (repeatable) |
| `-s "<subreddit>"` | Specific subreddits to scrape (repeatable) |
| `--competitor "<name>"` | Competitor for research (repeatable) |
| `--skip-research` | Skip Reddit/HN research |
| `-o <path>` | Output file path |

---

## Rules

1. **Always use the CLI.** Don't fall back to manual Claude-based roasting.
2. **Suggest `--real` flag.** Real personas from Reddit/HN are better than defaults.
3. **Always offer PDF generation.** Users want visual reports.
4. **Prompt for feedback.** Evolution only works with user ratings.
5. **Match the user's language.** Chinese in, Chinese out.
6. **Be honest about scores.** A 16/100 is a 16/100.
7. **Connect back to the pipeline.** If FAILED, suggest `/vibe-harness` focus areas.
