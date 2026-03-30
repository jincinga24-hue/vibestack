# How the Evolution Engine Works

Inspired by [EvoMap's Genome Evolution Protocol (GEP)](https://evomap.ai/).

## The Problem

Static AI personas give the same generic feedback every time. They never learn what's useful.

## The Solution

Encode persona traits as **genes**. Track which critiques users find useful. Kill bad critics. Breed good ones.

## Gene Encoding

Each persona's traits become mutable genes:

```json
{
  "persona_id": "Richard Zhao",
  "role": "vc",
  "generation": 3,
  "avg_usefulness": 0.77,
  "genes": {
    "kill_q_0": {
      "name": "kill_question_0",
      "value": "What's your CAC and LTV? Give me numbers.",
      "fitness": 0.82,
      "mutations": 1,
      "origin": "mutated"
    },
    "tone": {
      "value": "ice cold, numbers-obsessed",
      "fitness": 0.75
    }
  }
}
```

## The Evolution Cycle

```
1. SCAN     — After each roast run, collect user ratings
2. SIGNAL   — Map ratings to gene fitness scores
3. INTENT   — Identify which personas need evolution
4. MUTATE   — Modify genes of mid-tier performers
5. VALIDATE — Test mutated genes in next run
6. SOLIDIFY — Persist successful mutations to gene pool
```

### Kill (Bottom 20%)

After 3+ runs, personas with avg fitness < 0.3 are killed:
```
Kevin Wu: fitness 0.26 → KILLED
```
Dead personas are removed from the active panel.

### Mutate (Mid-tier 30-70%)

Genes of average performers get mutated to be sharper:
```
Sarah Chen.kill_q_1: "This is a feature, not a product"
  → MUTATED: "This is a feature, not a product — and be more specific about WHY this matters"
```

### Crossover (Top Performers)

The two best performers breed to create an evolved offspring:
```
BORN: evolved_1774878374
  Parent A: Richard Zhao (fitness 0.77)
  Parent B: Diana Volkov (fitness 0.57)
  Child inherits: best genes from each parent
```

## Feedback Loop

```bash
# 1. Run a roast
roastmymvp run https://app.com --mode vc

# 2. Rate the critiques (this is the key step)
roastmymvp feedback
#   Richard Zhao: "Your TAM is a conference room" → Rate: 9/10 (killer)
#   Kevin Wu: "Show me the product" → Rate: 2/10 (useless)

# 3. Evolve
roastmymvp evolve
#   KILLED: Kevin Wu (fitness 0.26)
#   MUTATED: Sarah Chen.kill_q_1
#   BORN: evolved_1774878374 from Richard Zhao x Diana Volkov

# 4. Next run uses evolved panel automatically
roastmymvp run https://another-app.com --mode vc
#   🧬 Using EVOLVED VC panel (gen 3, 25 alive)
```

## Gene Persistence

Genes survive between runs in `memory/genes/gene_pool.json`.

Evolution history is logged in `memory/genes/evolution_history.jsonl` — every mutation, kill, and crossover is recorded with timestamps.
