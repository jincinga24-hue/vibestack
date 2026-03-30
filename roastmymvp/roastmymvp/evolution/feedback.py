"""Feedback collection and evolution trigger.

After each roast, the user rates critiques. This drives evolution:
- High-rated critiques → those persona genes get reinforced
- Low-rated critiques → those genes get mutated or the persona dies
- After enough feedback → trigger an evolution cycle
"""

import json
import time
from pathlib import Path

from roastmymvp.evolution.genes import GenePool

FEEDBACK_DIR = Path(__file__).parent.parent.parent / "memory" / "feedback"
EVOLUTION_THRESHOLD = 5  # Evolve after this many feedback sessions


def save_run_results(
    run_id: str,
    url: str,
    mode: str,
    verdicts: list[dict],
) -> Path:
    """Save a run's results for later feedback collection."""
    FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
    run_file = FEEDBACK_DIR / f"run_{run_id}.json"
    run_file.write_text(json.dumps({
        "run_id": run_id,
        "url": url,
        "mode": mode,
        "timestamp": time.time(),
        "verdicts": verdicts,
        "feedback_collected": False,
    }, indent=2))
    return run_file


def collect_feedback_for_run(run_id: str, ratings: dict[str, float]) -> dict:
    """Apply user ratings to the gene pool.

    ratings: {persona_id: usefulness_score} where score is 0.0-1.0
    Returns evolution stats.
    """
    pool = GenePool()

    for persona_id, score in ratings.items():
        pool.record_feedback(persona_id, score)

    # Check if we should trigger evolution
    run_count = _count_feedback_sessions()
    should_evolve = run_count > 0 and run_count % EVOLUTION_THRESHOLD == 0

    mutations = []
    if should_evolve:
        mutations = pool.evolve()

    pool.save()

    return {
        "ratings_applied": len(ratings),
        "total_sessions": run_count,
        "evolved": should_evolve,
        "mutations": mutations,
        "pool_stats": pool.stats(),
    }


def _count_feedback_sessions() -> int:
    """Count how many feedback sessions have been recorded."""
    if not FEEDBACK_DIR.exists():
        return 0
    return sum(
        1 for f in FEEDBACK_DIR.glob("run_*.json")
        if json.loads(f.read_text()).get("feedback_collected")
    )


def initialize_gene_pool_from_defaults():
    """Seed the gene pool with the default VC and community personas."""
    from roastmymvp.vc.personas import DEFAULT_VC_PANEL
    from roastmymvp.personas.generator import generate_default_personas
    from roastmymvp.evolution.genes import (
        GenePool, encode_vc_genes, encode_community_genes,
    )

    pool = GenePool()

    # Seed VCs
    for vc in DEFAULT_VC_PANEL:
        if not pool.get(vc.name):
            genome = encode_vc_genes(
                vc.name, vc.kill_questions, vc.pet_peeves, vc.tone,
            )
            pool.put(genome)

    # Seed community personas
    for persona in generate_default_personas():
        if not pool.get(persona.name):
            genome = encode_community_genes(
                persona.name, persona.archetype.value,
                persona.evaluation_style.value, persona.frustrations,
            )
            pool.put(genome)

    pool.save()
    return pool.stats()
